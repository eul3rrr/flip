"""Utilities for parsing German relative dates into ISO format."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_de_relative_date(text: str, *, now: Optional[datetime] = None) -> Optional[str]:
    """Convert German date expressions like 'Heute', 'Gestern', 'vor X Tagen'
    into ISO date strings (YYYY-MM-DD).

    Returns ``None`` if the text cannot be parsed.
    """
    if now is None:
        now = datetime.now()

    t = text.strip().lower()
    if not t:
        return None

    if t.startswith("heute"):
        dt = now
    elif t.startswith("gestern"):
        dt = now - timedelta(days=1)
    else:
        m = re.search(r"vor\s+(\d+)\s+tag", t)
        if m:
            days = int(m.group(1))
            dt = now - timedelta(days=days)
        else:
            # try dd.mm.yyyy or ISO date
            for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(t, fmt)
                    break
                except ValueError:
                    continue
            else:
                return None
    return dt.date().isoformat()
