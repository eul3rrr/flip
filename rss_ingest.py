"""Poll RSS feeds and store ads in the database."""
from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Iterable, List, Set

import feedparser
from bs4 import BeautifulSoup

try:  # Python 3.11+
    import tomllib
except Exception:  # pragma: no cover - fallback for older versions
    import tomli as tomllib  # type: ignore

from db import DATABASE_FILE, get_connection, init_db, mark_inactive, upsert_ad
from de_dates import parse_de_relative_date
from model import Ad

CONFIG_FILE = "config.toml"


def load_config(path: str = CONFIG_FILE) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def entry_to_ad(entry, now_iso: str) -> Ad:
    link = entry.link
    m = re.search(r"/(\d+)(?:\?|$)", link)
    if not m:
        raise ValueError(f"Cannot extract ID from link: {link}")
    ad_id = m.group(1)
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    soup = BeautifulSoup(summary, "html.parser")
    text = soup.get_text(" ", strip=True)
    price_match = re.search(r"(\d+[\.\d]*)\s*€", text)
    price = (
        int(price_match.group(1).replace(".", "")) if price_match else None
    )
    location = None
    loc = soup.find(class_="location")
    if loc:
        location = loc.get_text(strip=True)
    published = entry.get("published")
    date_posted = parse_de_relative_date(published) if published else None
    image = None
    media = entry.get("media_content") or entry.get("media_thumbnail")
    if media:
        image = media[0].get("url")
    return Ad(
        id=ad_id,
        title=title,
        price=price,
        location=location,
        date_posted=date_posted,
        link=link,
        image=image,
        body_text=None,
        first_seen=now_iso,
        last_seen=now_iso,
        is_active=True,
    )


def poll_once(feeds: Iterable[str], conn) -> int:
    now_iso = datetime.utcnow().isoformat()
    seen: Set[str] = set()
    for url in feeds:
        d = feedparser.parse(url)
        for entry in d.entries:
            try:
                ad = entry_to_ad(entry, now_iso)
            except Exception:
                continue
            seen.add(ad.id)
            upsert_ad(conn, ad)
    mark_inactive(conn, now_iso)
    return len(seen)


def main() -> None:
    cfg = load_config()
    feeds: List[str] = cfg.get("feeds", [])
    interval = cfg.get("poll_interval_minutes", 15)
    db_path = cfg.get("database", DATABASE_FILE)

    conn = get_connection(db_path)
    init_db(conn)

    try:
        while True:
            count = poll_once(feeds, conn)
            print(f"Polled {len(feeds)} feeds, seen {count} ads")
            time.sleep(interval * 60)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
