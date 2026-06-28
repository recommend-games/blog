"""Refresh the Polymarket snapshot for the 2026 World Cup winner market.

Hits the public Gamma API and writes the raw JSON + a snapshot timestamp.
Re-run any time you want a fresher market quote; build_market_odds.py and
build_market_comparison.py then turn the raw snapshot into processed CSVs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.request

from world_cup_2026 import config

URL = "https://gamma-api.polymarket.com/events?slug=world-cup-winner"
UA = "Mozilla/5.0 (world-cup-2026-research/1.0; mk.schepke@gmail.com)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help="Write the snapshot into data/raw/conditional/ instead of the frozen baseline",
    )
    args = parser.parse_args()

    if args.conditional:
        snapshot = config.POLYMARKET_SNAPSHOT_CONDITIONAL
        snapshot_date = config.MARKET_ODDS_SNAPSHOT_DATE_CONDITIONAL
    else:
        snapshot = config.POLYMARKET_SNAPSHOT
        snapshot_date = config.MARKET_ODDS_SNAPSHOT_DATE

    request = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read())
    if not payload or "markets" not in payload[0]:
        raise RuntimeError("Unexpected Polymarket payload")
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps(payload))
    snapshot_date.write_text(dt.datetime.now(dt.timezone.utc).isoformat() + "\n")
    n_markets = len(payload[0]["markets"])
    print(f"Wrote {snapshot} ({n_markets} markets)")
    print(f"Wrote {snapshot_date} ({snapshot_date.read_text().strip()})")


if __name__ == "__main__":
    main()
