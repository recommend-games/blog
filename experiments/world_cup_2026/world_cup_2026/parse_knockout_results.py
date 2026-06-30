"""Parse played knockout-stage matches from the Wikipedia knockout-stage HTML.

Reads:
  data/raw/{tag}/wikipedia_2026_world_cup_knockout_stage.html
  outputs/{tag}/knockout_score_predictions.csv   (team name → match_id mapping)
  data/processed/results.csv                     (existing group + knockout rows)

Appends only newly played knockout rows; group rows and already-recorded
knockout rows are never modified. The winner field encodes the team_id of
the advancing side; for AET matches the penalty shootout winner is extracted
from the scorebox text.

The knockout_score_predictions.csv must already exist (produced by the
simulate + build_knockout_score_predictions pipeline) so that team names can
be mapped to the correct match_id.

Usage (from experiments/world_cup_2026/):
  uv run wc26-parse-knockout-results [--tag TAG]
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import re
from pathlib import Path

from world_cup_2026 import config

# SportsEvent anchor shared with parse_fixtures.py
ANCHOR_RE = re.compile(
    r'<div itemscope=""\s+itemtype="http(?:&#58;|:)//schema\.org/SportsEvent"',
    re.IGNORECASE,
)

# Played matches show a real score; unplayed ones show "Match N".
SCORE_RE = re.compile(r"^(\d+)\s*[–\-]\s*(\d+)")
AET_RE = re.compile(r"a\.e\.t\.")
# Penalty aggregate "X–Y" anywhere in a string.
PEN_SCORE_RE = re.compile(r"(\d+)\s*[–\-]\s*(\d+)")

FIELDS = ["match_id", "home_goals", "away_goals", "winner"]


def _clean(s: str) -> str:
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.DOTALL)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.DOTALL)
    s = re.sub(r'<span class="bday[^"]*"[^>]*>.*?</span>', "", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _anchor_text(s: str) -> str:
    m = re.search(r"<a [^>]*>(.*?)</a>", s, re.DOTALL)
    return _clean(m.group(1) if m else s)


def _extract_pen_winner(block_text: str, home_id: str, away_id: str) -> str:
    """Return the team_id of the penalty shootout winner.

    Wikipedia renders penalty kicks as:
      "Penalties HOME_KICK_NAMES X–Y AWAY_KICK_NAMES"
    where X is home pens scored and Y is away pens scored.
    """
    idx = block_text.find("Penalties")
    if idx == -1:
        return ""
    m = PEN_SCORE_RE.search(block_text[idx:])
    if not m:
        return ""
    home_pens, away_pens = int(m.group(1)), int(m.group(2))
    if home_pens > away_pens:
        return home_id
    if away_pens > home_pens:
        return away_id
    return ""


def _load_team_name_to_id() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with config.TEAMS_CONDITIONAL_CSV.open() as f:
        for row in csv.DictReader(f):
            mapping[row["team_name"]] = row["team_id"]
    return mapping


def _load_match_lookup(
    ko_predictions_path: Path,
) -> dict[tuple[str, str], tuple[int, bool]]:
    """Return {(id_x, id_y): (match_id, x_is_team_a)} for all knockout rows.

    Bidirectional so we find the right match_id regardless of which order
    Wikipedia lists the teams (Wikipedia home/away can differ from team_a/team_b).
    """
    lookup: dict[tuple[str, str], tuple[int, bool]] = {}
    with ko_predictions_path.open() as f:
        for row in csv.DictReader(f):
            mid = int(row["match_id"])
            a, b = row["team_a_id"], row["team_b_id"]
            lookup[(a, b)] = (mid, True)
            lookup[(b, a)] = (mid, False)
    return lookup


def _load_existing_rows() -> dict[int, dict]:
    if not config.RESULTS_CSV.exists():
        return {}
    rows: dict[int, dict] = {}
    with config.RESULTS_CSV.open() as f:
        for row in csv.DictReader(f):
            rows[int(row["match_id"])] = {k: row.get(k, "") for k in FIELDS}
    return rows


def parse_played_matches(
    html: str,
    team_name_to_id: dict[str, str],
    match_lookup: dict[tuple[str, str], tuple[int, bool]],
) -> list[dict]:
    """Return results.csv rows for every played match found in the knockout HTML."""
    anchors = [m.start() for m in ANCHOR_RE.finditer(html)]
    rows: list[dict] = []

    for i, pos in enumerate(anchors):
        end = anchors[i + 1] if i + 1 < len(anchors) else len(html)
        block = html[pos:end]

        score_m = re.search(r'<th class="fscore">(.*?)</th>', block, re.DOTALL)
        home_m = re.search(r'<th class="fhome"[^>]*>(.*?)</th>', block, re.DOTALL)
        away_m = re.search(r'<th class="faway"[^>]*>(.*?)</th>', block, re.DOTALL)
        if not (score_m and home_m and away_m):
            continue

        score_text = _clean(score_m.group(1))
        sm = SCORE_RE.match(score_text)
        if not sm:
            continue  # unplayed placeholder

        wiki_home_goals = int(sm.group(1))
        wiki_away_goals = int(sm.group(2))
        home_name = _anchor_text(home_m.group(1))
        away_name = _anchor_text(away_m.group(1))

        home_id = team_name_to_id.get(home_name)
        away_id = team_name_to_id.get(away_name)
        if not home_id or not away_id:
            print(f"Warning: unknown team {home_name!r} or {away_name!r}, skipping")
            continue

        entry = match_lookup.get((home_id, away_id))
        if entry is None:
            print(f"Warning: no match_id for {home_id} vs {away_id}, skipping")
            continue
        match_id, home_is_team_a = entry

        if wiki_home_goals > wiki_away_goals:
            winner = home_id
        elif wiki_away_goals > wiki_home_goals:
            winner = away_id
        elif AET_RE.search(score_text):
            winner = _extract_pen_winner(_clean(block), home_id, away_id)
        else:
            winner = ""  # draw not possible in knockout stage

        # Store goals from team_a's perspective to match results.csv convention.
        if home_is_team_a:
            team_a_goals, team_b_goals = wiki_home_goals, wiki_away_goals
        else:
            team_a_goals, team_b_goals = wiki_away_goals, wiki_home_goals

        rows.append(
            {
                "match_id": match_id,
                "home_goals": team_a_goals,
                "away_goals": team_b_goals,
                "winner": winner,
            }
        )

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse played knockout results into data/processed/results.csv."
    )
    parser.add_argument("--tag", default="conditional_knockout")
    args = parser.parse_args()

    cpaths = config.conditional_paths(args.tag)
    html_path = cpaths.data_raw / "wikipedia_2026_world_cup_knockout_stage.html"
    ko_predictions_path = cpaths.outputs / "knockout_score_predictions.csv"

    if not html_path.exists():
        raise SystemExit(f"HTML snapshot not found: {html_path}")
    if not ko_predictions_path.exists():
        raise SystemExit(
            f"knockout_score_predictions.csv not found: {ko_predictions_path}\n"
            "Run the simulation and wc26-build-knockout-score-predictions first."
        )

    team_name_to_id = _load_team_name_to_id()
    match_lookup = _load_match_lookup(ko_predictions_path)
    existing = _load_existing_rows()

    html = html_path.read_text(errors="replace")
    parsed = parse_played_matches(html, team_name_to_id, match_lookup)

    added = 0
    for row in parsed:
        mid = row["match_id"]
        if mid in existing:
            continue
        existing[mid] = row
        added += 1

    all_rows = sorted(existing.values(), key=lambda r: int(r["match_id"]))

    if len({r["match_id"] for r in all_rows}) != len(all_rows):
        raise RuntimeError("duplicate match_id in results")

    config.RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with config.RESULTS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    n_ko = sum(1 for r in all_rows if int(r["match_id"]) > 72)
    print(
        f"Wrote {len(all_rows)} results to {config.RESULTS_CSV} "
        f"({len(all_rows) - n_ko} group, {n_ko} knockout; {added} new)"
    )


if __name__ == "__main__":
    main()
