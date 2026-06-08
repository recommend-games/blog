"""Refresh the Polymarket snapshot for the 2026 World Cup winner market.

Hits the public Gamma API and writes the raw JSON + a snapshot timestamp.
Re-run any time you want a fresher market quote; build_market_odds.py and
build_market_comparison.py then turn the raw snapshot into processed CSVs.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SNAPSHOT = RAW / "polymarket_world_cup_winner.json"
SNAPSHOT_DATE = RAW / "market_odds_snapshot_date.txt"

URL = "https://gamma-api.polymarket.com/events?slug=world-cup-winner"
UA = "Mozilla/5.0 (world-cup-2026-research/1.0; mk.schepke@gmail.com)"


def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read())
    if not payload or "markets" not in payload[0]:
        raise RuntimeError("Unexpected Polymarket payload")
    SNAPSHOT.write_text(json.dumps(payload))
    SNAPSHOT_DATE.write_text(dt.datetime.now(dt.timezone.utc).isoformat() + "\n")
    n_markets = len(payload[0]["markets"])
    print(f"Wrote {SNAPSHOT} ({n_markets} markets)")
    print(f"Wrote {SNAPSHOT_DATE} ({SNAPSHOT_DATE.read_text().strip()})")


if __name__ == "__main__":
    main()
