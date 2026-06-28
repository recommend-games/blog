"""Build data/processed/market_odds.csv from the Polymarket snapshot.

Polymarket runs an independent yes/no market for each team's chance of
winning the 2026 World Cup. Because the markets are independent the raw
'yes' prices don't sum to 1 (about 2.9% margin in this snapshot), so we
divide each by the total to produce a de-vigged implied probability that
does sum to 1 across the 48 qualifying teams.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from world_cup_2026 import config

NAME_OVERRIDES: dict[str, str] = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Congo DR": "DR Congo",
    "Czechia": "Czech Republic",
    "Turkiye": "Turkey",
    "USA": "United States",
}

QUESTION_RE = re.compile(r"Will (.+) win the 2026 FIFA World Cup\?")


def load_team_lookup(teams_csv: Path) -> dict[str, str]:
    teams = list(csv.DictReader(open(teams_csv)))
    return {row["team_name"]: row["team_id"] for row in teams}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help="De-vig the conditional Polymarket snapshot into market_odds_{tag}.csv",
    )
    parser.add_argument(
        "--tag",
        default="conditional",
        metavar="TAG",
        help="Output subdirectory tag for the conditional run (default: 'conditional'). "
             "Use e.g. 'conditional_r32' to preserve earlier conditional outputs.",
    )
    args = parser.parse_args()

    if args.conditional:
        cpaths = config.conditional_paths(args.tag)
        snapshot = cpaths.polymarket_snapshot
        teams_csv = config.TEAMS_CONDITIONAL_CSV
        output = cpaths.market_odds_csv
    else:
        snapshot = config.POLYMARKET_SNAPSHOT
        teams_csv = config.TEAMS_CSV
        output = config.MARKET_ODDS_CSV

    payload = json.load(open(snapshot))[0]
    team_id_by_name = load_team_lookup(teams_csv)

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

    with output.open("w", newline="") as f:
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
        f"Wrote {len(rows)} rows to {output} "
        f"(raw vig = {(total - 1) * 100:.2f}%; skipped {skipped or 'none'})"
    )


if __name__ == "__main__":
    main()
