"""Parse the Wikipedia knockout-stage article into processed/knockout_slots.csv.

Reads world_cup_2026/data/raw/wikipedia_2026_world_cup_knockout_stage.html and
writes world_cup_2026/data/processed/knockout_slots.csv with one row per
knockout fixture: R32 (16), R16 (8), QF (4), SF (2), FINAL (1) = 31 matches.

Match 103 (the third-place play-off) is skipped because the simulation plan
does not model it; the final is Match 104.

Source notation is translated from Wikipedia's placeholder text:
  "Winner Group X"        -> "1X"
  "Runner-up Group X"     -> "2X"
  "3rd Group X/Y/Z/..."   -> "3XYZ..." (letters joined, slashes removed)
  "Winner Match N"        -> "W<N>"
  "Loser Match N"         -> "L<N>"
"""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUTPUT = PROC / "knockout_slots.csv"

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

STAGE_OF: dict[int, str] = {
    **{i: "R32" for i in range(73, 89)},
    **{i: "R16" for i in range(89, 97)},
    **{i: "QF" for i in range(97, 101)},
    **{i: "SF" for i in range(101, 103)},
    104: "FINAL",
}

SKIP_MATCH_IDS = {103}  # third-place play-off

FIELDS = [
    "match_id",
    "stage",
    "team_a_source",
    "team_b_source",
    "venue_country",
    "winner_to",
]

ANCHOR_RE = re.compile(
    r'<div itemscope=""\s+itemtype="http(?:&#58;|:)//schema\.org/SportsEvent"',
    re.IGNORECASE,
)


def clean(s: str) -> str:
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.DOTALL)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_source(label: str) -> str:
    s = label.strip()
    if m := re.fullmatch(r"Winner Group ([A-L])", s):
        return f"1{m.group(1)}"
    if m := re.fullmatch(r"Runner-up Group ([A-L])", s):
        return f"2{m.group(1)}"
    if m := re.fullmatch(r"3rd Group ([A-L](?:/[A-L])+)", s):
        return "3" + m.group(1).replace("/", "")
    if m := re.fullmatch(r"Winner Match (\d+)", s):
        return f"W{m.group(1)}"
    if m := re.fullmatch(r"Loser Match (\d+)", s):
        return f"L{m.group(1)}"
    raise ValueError(f"Unrecognised source: {s!r}")


def parse_block(block: str) -> dict:
    label_m = re.search(r'<th class="fscore">(.*?)</th>', block, re.DOTALL)
    home_m = re.search(r'<th class="fhome"[^>]*>(.*?)</th>', block, re.DOTALL)
    away_m = re.search(r'<th class="faway"[^>]*>(.*?)</th>', block, re.DOTALL)
    loc_m = re.search(r'<div itemprop="location"[^>]*>(.*?)</div>', block, re.DOTALL)

    if not (label_m and home_m and away_m and loc_m):
        raise RuntimeError("Missing expected sub-element in knockout block")

    match_id_m = re.search(r"\d+", clean(label_m.group(1)))
    if not match_id_m:
        raise RuntimeError(f"No match id in label {clean(label_m.group(1))!r}")
    match_id = int(match_id_m.group(0))

    home = parse_source(clean(home_m.group(1)))
    away = parse_source(clean(away_m.group(1)))

    loc = clean(loc_m.group(1))
    city = loc.split(",", 1)[1].strip() if "," in loc else loc
    if city not in CITY_TO_COUNTRY:
        raise RuntimeError(f"Unknown host city {city!r}")

    return {
        "match_id": match_id,
        "team_a_source": home,
        "team_b_source": away,
        "venue_country": CITY_TO_COUNTRY[city],
    }


def main() -> None:
    text = (RAW / "wikipedia_2026_world_cup_knockout_stage.html").read_text()
    anchors = [m.start() for m in ANCHOR_RE.finditer(text)]
    if len(anchors) != 32:
        raise RuntimeError(f"Expected 32 knockout matches, found {len(anchors)}")

    raw_rows = []
    for i, pos in enumerate(anchors):
        end = anchors[i + 1] if i + 1 < len(anchors) else len(text)
        raw_rows.append(parse_block(text[pos:end]))

    by_id = {r["match_id"]: r for r in raw_rows}
    winner_to: dict[int, int] = {}
    for r in raw_rows:
        for src in (r["team_a_source"], r["team_b_source"]):
            if src.startswith("W"):
                fed = int(src[1:])
                winner_to[fed] = r["match_id"]

    rows = []
    for match_id in sorted(by_id):
        if match_id in SKIP_MATCH_IDS:
            continue
        if match_id not in STAGE_OF:
            raise RuntimeError(f"No stage mapping for match {match_id}")
        r = by_id[match_id]
        rows.append(
            {
                "match_id": match_id,
                "stage": STAGE_OF[match_id],
                "team_a_source": r["team_a_source"],
                "team_b_source": r["team_b_source"],
                "venue_country": r["venue_country"],
                "winner_to": winner_to.get(match_id, ""),
            }
        )

    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
