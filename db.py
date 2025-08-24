"""SQLite database helpers for storing ads."""
from __future__ import annotations

import sqlite3
from typing import Iterable, Optional

from model import Ad

DATABASE_FILE = "ads.db"


def get_connection(path: str = DATABASE_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ads (
            id TEXT PRIMARY KEY,
            title TEXT,
            price INTEGER,
            location TEXT,
            date_posted TEXT,
            link TEXT,
            image TEXT,
            body_text TEXT,
            first_seen TEXT,
            last_seen TEXT,
            is_active INTEGER
        )
        """
    )
    conn.commit()


def upsert_ad(conn: sqlite3.Connection, ad: Ad) -> None:
    existing = conn.execute("SELECT id FROM ads WHERE id = ?", (ad.id,)).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE ads
            SET title = ?, price = ?, location = ?, date_posted = ?, link = ?, image = ?,
                last_seen = ?, is_active = 1
            WHERE id = ?
            """,
            (
                ad.title,
                ad.price,
                ad.location,
                ad.date_posted,
                ad.link,
                ad.image,
                ad.last_seen,
                ad.id,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO ads (
                id, title, price, location, date_posted, link, image, body_text,
                first_seen, last_seen, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ad.id,
                ad.title,
                ad.price,
                ad.location,
                ad.date_posted,
                ad.link,
                ad.image,
                ad.body_text,
                ad.first_seen,
                ad.last_seen,
                int(ad.is_active),
            ),
        )
    conn.commit()


def mark_inactive(conn: sqlite3.Connection, cutoff: str) -> None:
    """Mark ads as inactive if they haven't been seen since cutoff."""
    conn.execute(
        "UPDATE ads SET is_active = 0 WHERE last_seen < ?", (cutoff,)
    )
    conn.commit()


def update_details(
    conn: sqlite3.Connection,
    ad_id: str,
    *,
    price: Optional[int] = None,
    location: Optional[str] = None,
    date_posted: Optional[str] = None,
    image: Optional[str] = None,
    body_text: Optional[str] = None,
) -> None:
    conn.execute(
        """
        UPDATE ads
        SET price = COALESCE(?, price),
            location = COALESCE(?, location),
            date_posted = COALESCE(?, date_posted),
            image = COALESCE(?, image),
            body_text = COALESCE(?, body_text)
        WHERE id = ?
        """,
        (price, location, date_posted, image, body_text, ad_id),
    )
    conn.commit()
