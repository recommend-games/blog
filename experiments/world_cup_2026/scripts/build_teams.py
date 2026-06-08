"""Build processed/teams.csv by joining fifa_teams_groups.csv with the Elo snapshot.

Inputs:
  data/raw/fifa_teams_groups.csv   - 48 teams with group/slot/FIFA ranking
  data/raw/eloratings_teams.tsv    - eloratings.net code -> name(s) mapping
  data/raw/eloratings_world.tsv    - current Elo rating per team code

Output:
  data/processed/teams.csv         - one row per team (48 rows total)

team_id is set to the eloratings.net 2-character code. It is unique, stable
and present in the source data, so we avoid maintaining a separate FIFA
3-letter code map.
"""

from __future__ import annotations

import csv
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
PROC = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT = PROC / "teams.csv"

# Overrides: FIFA/Wikipedia team name -> eloratings.net name. Populate as
# mismatches are discovered by running the script.
NAME_OVERRIDES: dict[str, str] = {
    "Czech Republic": "Czechia",
}

FIELDS = [
    "team_id",
    "team_name",
    "elo_name",
    "group",
    "group_slot",
    "elo",
    "fifa_ranking",
    "is_host",
    "host_country",
]

HOSTS = {
    "Mexico": "Mexico",
    "Canada": "Canada",
    "United States": "USA",
}


def load_elo_name_to_code() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for line in (RAW / "eloratings_teams.tsv").read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.endswith("_loc"):
            continue
        for name in parts[1:]:
            mapping[name] = code
    return mapping


def load_elo_ratings() -> dict[str, int]:
    ratings: dict[str, int] = {}
    for line in (RAW / "eloratings_world.tsv").read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        ratings[parts[2]] = int(parts[3])
    return ratings


def main() -> None:
    name_to_code = load_elo_name_to_code()
    ratings = load_elo_ratings()

    unmatched: list[str] = []
    rows: list[dict] = []
    with (RAW / "fifa_teams_groups.csv").open() as f:
        for fifa_row in csv.DictReader(f):
            fifa_name = fifa_row["team"]
            elo_name = NAME_OVERRIDES.get(fifa_name, fifa_name)
            code = name_to_code.get(elo_name)
            if code is None:
                unmatched.append(fifa_name)
                continue
            elo = ratings.get(code)
            if elo is None:
                unmatched.append(f"{fifa_name} (code {code} has no current rating)")
                continue
            host_country = HOSTS.get(fifa_name, "")
            rows.append(
                {
                    "team_id": code,
                    "team_name": fifa_name,
                    "elo_name": elo_name,
                    "group": fifa_row["group"],
                    "group_slot": fifa_row["group_slot"],
                    "elo": elo,
                    "fifa_ranking": fifa_row["fifa_ranking_nov_2025"],
                    "is_host": "true" if host_country else "false",
                    "host_country": host_country,
                }
            )

    if unmatched:
        print(f"UNMATCHED ({len(unmatched)}): {unmatched}")
        raise SystemExit(1)

    PROC.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
