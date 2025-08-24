# eBay Kleinanzeigen Bike Ads Collector

This project polls public RSS feeds from [eBay Kleinanzeigen](https://www.kleinanzeigen.de/) to collect
second-hand bike advertisements. Ads are stored in a SQLite database and can be
optionally enriched with additional details using Playwright.

## Setup

```bash
pip install -r requirements.txt
# Playwright needs browsers:
playwright install
```

Edit `config.toml` and add the RSS feed URLs you want to monitor.

## Usage

### Ingest RSS feeds

```bash
python rss_ingest.py
```

The script runs continuously and polls the configured feeds every
`poll_interval_minutes`. New ads are inserted into the database and existing
ones are updated. Ads not seen in the latest poll are marked inactive.

### Enrich ads with Playwright

```bash
python enrich_playwright.py <ad_url> [<ad_url> ...]
```

For each provided ad URL, the script downloads the full description, price,
location, date string, and main image and updates the corresponding record in
the database. Requests are throttled and a custom User-Agent is used.

## Modules

* `model.py` – Dataclass representing an ad.
* `db.py` – SQLite helper functions.
* `de_dates.py` – Parse German relative dates to ISO format.
* `rss_ingest.py` – Poll RSS feeds and store ads.
* `enrich_playwright.py` – Enrich ads by visiting the ad page.

## Schema

The SQLite database contains a single table `ads` with the columns:

```
id TEXT PRIMARY KEY
title TEXT
price INTEGER
location TEXT
date_posted TEXT
link TEXT
image TEXT
body_text TEXT
first_seen TEXT
last_seen TEXT
is_active INTEGER
```

## License

MIT
