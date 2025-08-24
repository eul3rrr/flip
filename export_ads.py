"""Export active ads to a CSV file with optional filters."""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from typing import Optional, List

from db import get_connection, init_db


OUTPUT_FILE = "ads.csv"


def prompt_int(prompt: str) -> Optional[int]:
    """Prompt user for an integer value, allowing blank for None."""
    while True:
        val = input(prompt).strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            print("Please enter a valid integer or leave blank.")


def query_ads(
    min_price: Optional[int],
    max_price: Optional[int],
    max_age_days: Optional[int],
) -> List[tuple]:
    """Query ads table and return rows matching filters."""
    conn = get_connection()
    try:
        init_db(conn)
        sql = (
            "SELECT title, price, location, date_posted, link "
            "FROM ads WHERE is_active = 1"
        )
        params: List[object] = []

        if min_price is not None:
            sql += " AND price >= ?"
            params.append(min_price)
        if max_price is not None:
            sql += " AND price <= ?"
            params.append(max_price)
        if max_age_days is not None:
            cutoff = (datetime.utcnow() - timedelta(days=max_age_days)).date().isoformat()
            sql += " AND date_posted IS NOT NULL AND date_posted >= ?"
            params.append(cutoff)

        sql += " ORDER BY date_posted DESC"
        rows = conn.execute(sql, params).fetchall()
        return [(r["title"], r["price"], r["location"], r["date_posted"], r["link"]) for r in rows]
    finally:
        conn.close()


def write_csv(rows: List[tuple], path: str = OUTPUT_FILE) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["title", "price", "location", "date_posted", "link"])
        writer.writerows(rows)


def main() -> None:
    print("Export active ads to CSV")
    min_price = prompt_int("Minimum price (blank for none): ")
    max_price = prompt_int("Maximum price (blank for none): ")
    max_age_days = prompt_int("Maximum age in days (blank for any): ")

    rows = query_ads(min_price, max_price, max_age_days)
    write_csv(rows, OUTPUT_FILE)
    print(f"Wrote {len(rows)} ads to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
