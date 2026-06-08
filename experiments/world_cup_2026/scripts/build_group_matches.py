"""Build processed/group_matches.csv from the raw fixtures and team table.

Inputs:
  data/raw/fifa_fixtures.csv      - 72 group-stage matches (team names, city)
  data/processed/teams.csv        - team_name -> group_slot lookup

Output:
  data/processed/group_matches.csv  - one row per group-stage fixture, with
                                      slot references and venue_country
                                      (Canada/Mexico/USA), per the plan schema

match_id is taken from Wikipedia's tournament-wide "Match N" label, so group
matches occupy 1-72 and knockout matches will pick up at 73+.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUTPUT = PROC / "group_matches.csv"

CITY_TO_COUNTRY: dict[str, str] = {
    "Arlington": "USA",
    "Atlanta": "USA",
    "East Rutherford": "USA",
    "Foxborough": "USA",
    "Houston": "USA",
    "Inglewood": "USA",
    "Kansas City": "USA",
    "Miami Gardens": "USA",
    "Philadelphia": "USA",
    "Santa Clara": "USA",
    "Seattle": "USA",
    "Guadalupe": "Mexico",
    "Mexico City": "Mexico",
    "Zapopan": "Mexico",
    "Toronto": "Canada",
    "Vancouver": "Canada",
}

FIELDS = [
    "match_id",
    "stage",
    "round_number",
    "group",
    "team_a_slot",
    "team_b_slot",
    "venue_country",
]


def load_team_to_slot() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with (PROC / "teams.csv").open() as f:
        for row in csv.DictReader(f):
            mapping[row["team_name"]] = row["group_slot"]
    return mapping


def main() -> None:
    team_to_slot = load_team_to_slot()
    rows: list[dict] = []
    with (RAW / "fifa_fixtures.csv").open() as f:
        for fixture in csv.DictReader(f):
            label_m = re.search(r"\d+", fixture["match_label"])
            if not label_m:
                raise RuntimeError(f"Cannot parse match_id from {fixture['match_label']!r}")
            match_id = int(label_m.group(0))
            city = fixture["city"]
            if city not in CITY_TO_COUNTRY:
                raise RuntimeError(f"Unknown host city {city!r}")
            home, away = fixture["home_team"], fixture["away_team"]
            if home not in team_to_slot or away not in team_to_slot:
                raise RuntimeError(f"Unknown team in fixture: {home} vs {away}")
            rows.append(
                {
                    "match_id": match_id,
                    "stage": "group",
                    "round_number": int(fixture["round_number"]),
                    "group": fixture["group"],
                    "team_a_slot": team_to_slot[home],
                    "team_b_slot": team_to_slot[away],
                    "venue_country": CITY_TO_COUNTRY[city],
                }
            )
    rows.sort(key=lambda r: r["match_id"])
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
