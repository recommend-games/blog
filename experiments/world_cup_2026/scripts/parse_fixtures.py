"""Parse the 12 Wikipedia per-group HTML snapshots into fifa_fixtures.csv.

Reads world_cup_2026/data/raw/wikipedia_2026_world_cup_group_{A..L}.html and
writes world_cup_2026/data/raw/fifa_fixtures.csv with one row per group-stage
fixture (6 matches per group × 12 groups = 72 rows).

Each Wikipedia "footballbox" wraps a single match. We extract the ISO date
from the <span class="bday"> element, the kickoff time from <div class="ftime">,
the home/away teams from the fevent <th> cells, and the stadium/city from the
<div itemprop="location"> block. round_number is derived by sorting matches
within each group chronologically and pairing them (matches 1-2 = round 1,
matches 3-4 = round 2, matches 5-6 = round 3).
"""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT = RAW_DIR / "fifa_fixtures.csv"

GROUP_LETTERS = "ABCDEFGHIJKL"

FIELDS = [
    "group",
    "round_number",
    "match_label",
    "date",
    "time",
    "home_team",
    "away_team",
    "venue",
    "city",
]

ANCHOR_RE = re.compile(
    r'<div itemscope=""\s+itemtype="http(?:&#58;|:)//schema\.org/SportsEvent"',
    re.IGNORECASE,
)


def clean(s: str) -> str:
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.DOTALL)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.DOTALL)
    s = re.sub(r'<span class="bday[^"]*"[^>]*>.*?</span>', "", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def anchor_text(s: str) -> str:
    m = re.search(r"<a [^>]*>(.*?)</a>", s, re.DOTALL)
    return clean(m.group(1) if m else s)


def parse_block(group: str, block: str) -> dict:
    date_m = re.search(r'<span class="bday[^"]*">([^<]+)</span>', block)
    time_m = re.search(r'<div class="ftime">(.*?)</div>', block, re.DOTALL)
    label_m = re.search(r'<th class="fscore">(.*?)</th>', block, re.DOTALL)
    home_m = re.search(r'<th class="fhome"[^>]*>(.*?)</th>', block, re.DOTALL)
    away_m = re.search(r'<th class="faway"[^>]*>(.*?)</th>', block, re.DOTALL)
    loc_m = re.search(r'<div itemprop="location"[^>]*>(.*?)</div>', block, re.DOTALL)

    venue, city = "", ""
    if loc_m:
        loc_text = clean(loc_m.group(1))
        if "," in loc_text:
            venue_part, city_part = loc_text.split(",", 1)
            venue, city = venue_part.strip(), city_part.strip()
        else:
            venue = loc_text

    return {
        "group": group,
        "round_number": 0,  # filled after sorting
        "match_label": clean(label_m.group(1)) if label_m else "",
        "date": date_m.group(1).strip() if date_m else "",
        "time": clean(time_m.group(1)) if time_m else "",
        "home_team": anchor_text(home_m.group(1)) if home_m else "",
        "away_team": anchor_text(away_m.group(1)) if away_m else "",
        "venue": venue,
        "city": city,
    }


def parse_group(group: str, path: Path) -> list[dict]:
    text = path.read_text()
    anchors = [m.start() for m in ANCHOR_RE.finditer(text)]
    if len(anchors) != 6:
        raise RuntimeError(f"Group {group}: expected 6 matches, found {len(anchors)}")
    fixtures = []
    for i, pos in enumerate(anchors):
        end = anchors[i + 1] if i + 1 < len(anchors) else len(text)
        fixtures.append(parse_block(group, text[pos:end]))
    fixtures.sort(key=lambda f: (f["date"], f["time"], f["match_label"]))
    for i, f in enumerate(fixtures):
        f["round_number"] = (i // 2) + 1
    return fixtures


def main() -> None:
    rows: list[dict] = []
    for g in GROUP_LETTERS:
        rows.extend(parse_group(g, RAW_DIR / f"wikipedia_2026_world_cup_group_{g}.html"))
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
