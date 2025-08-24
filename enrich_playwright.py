"""Enrich ads by visiting the ad page with Playwright."""
from __future__ import annotations

import argparse
import asyncio
import re
from typing import Iterable

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from db import get_connection, update_details
from de_dates import parse_de_relative_date

USER_AGENT = "Mozilla/5.0 (compatible; KleinanzeigenBot/1.0; +https://example.com)"
THROTTLE_SECONDS = 2


def extract_details(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("#viewad-description-text")
    body_text = body.get_text(" ", strip=True) if body else None

    price = None
    price_el = soup.select_one("[itemprop='price'], #viewad-price, .price")
    if price_el:
        text = price_el.get_text(" ", strip=True)
        m = re.search(r"(\d+[\.\d]*)\s*€", text)
        if m:
            price = int(m.group(1).replace(".", ""))

    location = None
    loc_el = soup.select_one("[itemprop='address'], .location, #viewad-locality")
    if loc_el:
        location = loc_el.get_text(" ", strip=True)

    date_posted = None
    date_el = soup.select_one("time, .date")
    if date_el:
        date_posted = parse_de_relative_date(date_el.get_text(" ", strip=True))

    image = None
    img_el = soup.select_one("img[itemprop='image'], #viewad-image img")
    if img_el and img_el.get("src"):
        image = img_el["src"]

    return {
        "price": price,
        "location": location,
        "date_posted": date_posted,
        "image": image,
        "body_text": body_text,
    }


async def enrich(urls: Iterable[str]) -> None:
    conn = get_connection()
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        for url in urls:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(THROTTLE_SECONDS)
            details = extract_details(await page.content())
            ad_id = re.search(r"/(\d+)(?:\?|$)", url).group(1)
            update_details(conn, ad_id, **details)
        await browser.close()
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich ads with Playwright")
    parser.add_argument("urls", nargs="+", help="Ad URLs to enrich")
    args = parser.parse_args()
    asyncio.run(enrich(args.urls))


if __name__ == "__main__":
    main()
