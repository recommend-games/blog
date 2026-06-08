"""Build data/processed/market_odds.csv from the Polymarket snapshot.

Polymarket runs an independent yes/no market for each team's chance of
winning the 2026 World Cup. Because the markets are independent the raw
'yes' prices don't sum to 1 (about 2.9% margin in this snapshot), so we
divide each by the total to produce a de-vigged implied probability that
does sum to 1 across the 48 qualifying teams.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUTPUT = PROC / "market_odds.csv"

NAME_OVERRIDES: dict[str, str] = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Congo DR": "DR Congo",
    "Czechia": "Czech Republic",
    "Turkiye": "Turkey",
    "USA": "United States",
}

QUESTION_RE = re.compile(r"Will (.+) win the 2026 FIFA World Cup\?")


def load_team_lookup() -> dict[str, str]:
    teams = list(csv.DictReader(open(ROOT / "data" / "processed" / "teams.csv")))
    return {row["team_name"]: row["team_id"] for row in teams}


def main() -> None:
    payload = json.load(open(RAW / "polymarket_world_cup_winner.json"))[0]
    team_id_by_name = load_team_lookup()

    raw_prices: dict[str, float] = {}
    skipped: list[str] = []
    for m in payload["markets"]:
        prices = m.get("outcomePrices")
        if prices in (None, ""):
            continue
        if isinstance(prices, str):
            prices = json.loads(prices)
        match = QUESTION_RE.match(m["question"])
        if not match:
            continue
        pm_name = match.group(1)
        team_name = NAME_OVERRIDES.get(pm_name, pm_name)
        if team_name not in team_id_by_name:
            skipped.append(pm_name)
            continue
        raw_prices[team_name] = float(prices[0])

    missing = set(team_id_by_name) - set(raw_prices)
    if missing:
        raise RuntimeError(f"No Polymarket price for: {sorted(missing)}")

    total = sum(raw_prices.values())
    rows = []
    for team_name, yes_price in raw_prices.items():
        devigged = yes_price / total
        rows.append(
            {
                "team_id": team_id_by_name[team_name],
                "team_name": team_name,
                "polymarket_yes_price": yes_price,
                "polymarket_p_winner": devigged,
                "polymarket_decimal_odds": (1.0 / devigged) if devigged > 0 else float("nan"),
            }
        )
    rows.sort(key=lambda r: -r["polymarket_p_winner"])

    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "team_id",
                "team_name",
                "polymarket_yes_price",
                "polymarket_p_winner",
                "polymarket_decimal_odds",
            ],
        )
        writer.writeheader()
        for r in rows:
            r["polymarket_yes_price"] = f"{r['polymarket_yes_price']:.6f}"
            r["polymarket_p_winner"] = f"{r['polymarket_p_winner']:.6f}"
            r["polymarket_decimal_odds"] = f"{r['polymarket_decimal_odds']:.4f}"
            writer.writerow(r)
    print(
        f"Wrote {len(rows)} rows to {OUTPUT} "
        f"(raw vig = {(total - 1) * 100:.2f}%; skipped {skipped or 'none'})"
    )


if __name__ == "__main__":
    main()
