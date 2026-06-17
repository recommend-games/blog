"""Parse played group-stage scorelines into data/processed/results.csv.

Reads the refreshed group HTML snapshots under data/raw/conditional/ (which,
unlike the frozen pre-tournament snapshots, carry the actual scores), extracts
the scoreline from each footballbox whose <th class="fscore"> now shows a score
rather than the "Match N" label, and maps home/away team names to the canonical
match_id via the slot assignments already baked into group_matches.csv.

Output:
  data/processed/results.csv  - one row per played group match:
                                match_id, home_goals, away_goals
                                (home == team_a_slot, away == team_b_slot)

Only group matches are handled here; the knockout stage has not started. The
simulator pins every listed match to its recorded score and samples the rest,
so the resulting probabilities are conditional on the results so far.
"""

from __future__ import annotations

import csv
import re

from world_cup_2026 import config, parse_fixtures
from world_cup_2026.group_stage import GROUP_LETTERS

OUTPUT = config.RESULTS_CSV

# A played match shows its score (e.g. "2-1", en dash or hyphen) where an
# unplayed one still shows the "Match N" label.
SCORE_RE = re.compile(r"^(\d+)\s*[–‒—-]\s*(\d+)$")

FIELDS = ["match_id", "home_goals", "away_goals"]


def load_team_to_slot() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with config.TEAMS_CSV.open() as f:
        for row in csv.DictReader(f):
            mapping[row["team_name"]] = row["group_slot"]
    return mapping


def load_match_id_by_slots() -> dict[tuple[str, str], int]:
    mapping: dict[tuple[str, str], int] = {}
    with config.GROUP_MATCHES_CSV.open() as f:
        for row in csv.DictReader(f):
            mapping[(row["team_a_slot"], row["team_b_slot"])] = int(row["match_id"])
    return mapping


def main() -> None:
    team_to_slot = load_team_to_slot()
    match_id_by_slots = load_match_id_by_slots()

    rows: list[dict] = []
    for g in GROUP_LETTERS:
        path = config.DATA_RAW_CONDITIONAL / f"wikipedia_2026_world_cup_group_{g}.html"
        for fixture in parse_fixtures.parse_group(g, path):
            score_m = SCORE_RE.match(fixture["match_label"])
            if not score_m:
                continue  # not played yet
            home, away = fixture["home_team"], fixture["away_team"]
            if home not in team_to_slot or away not in team_to_slot:
                raise RuntimeError(f"Group {g}: unknown team in {home} vs {away}")
            slots = (team_to_slot[home], team_to_slot[away])
            match_id = match_id_by_slots.get(slots)
            if match_id is None:
                raise RuntimeError(
                    f"Group {g}: no group_matches row for {home} (home) vs {away} "
                    f"(away) -> slots {slots}; check home/away orientation"
                )
            rows.append(
                {
                    "match_id": match_id,
                    "home_goals": int(score_m.group(1)),
                    "away_goals": int(score_m.group(2)),
                }
            )

    rows.sort(key=lambda r: r["match_id"])
    if len({r["match_id"] for r in rows}) != len(rows):
        raise RuntimeError("duplicate match_id among played results")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} played results to {OUTPUT}")


if __name__ == "__main__":
    main()
