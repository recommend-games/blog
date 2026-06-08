"""Parse the 12 Wikipedia per-group HTML snapshots into fifa_teams_groups.csv.

Reads world_cup_2026/data/raw/wikipedia_2026_world_cup_group_{A..L}.html and
writes world_cup_2026/data/raw/fifa_teams_groups.csv with one row per team
(48 rows). The November 2025 FIFA ranking is captured because that is the
snapshot used at the draw, which is what FIFA's tie-break rules refer to.
"""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT = RAW_DIR / "fifa_teams_groups.csv"

GROUP_LETTERS = "ABCDEFGHIJKL"

FIELDS = [
    "group",
    "group_slot",
    "team",
    "pot",
    "confederation",
    "method_of_qualification",
    "date_of_qualification",
    "finals_appearance",
    "last_appearance",
    "previous_best",
    "fifa_ranking_nov_2025",
]


def clean(cell: str) -> str:
    cell = re.sub(r"<sup[^>]*>.*?</sup>", "", cell, flags=re.DOTALL)
    cell = re.sub(r"<style[^>]*>.*?</style>", "", cell, flags=re.DOTALL)
    cell = re.sub(r"<[^>]+>", "", cell)
    cell = html.unescape(cell)
    cell = re.sub(r"\s+", " ", cell).strip()
    return cell


def parse_group(group: str, path: Path) -> list[dict]:
    text = path.read_text()
    m = re.search(
        r'<table[^>]*class="wikitable sortable"[^>]*>.*?</table>',
        text,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(f"No wikitable sortable found in {path}")
    table = m.group(0)
    trs = re.findall(r"<tr[^>]*>.*?</tr>", table, re.DOTALL)
    # First two <tr> are the two-level header.
    rows = []
    for tr in trs[2:]:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.DOTALL)
        if len(cells) < 11:
            continue
        values = [clean(c) for c in cells]
        slot, team, pot, conf, method, date, appearance, last, best, rank_nov, _rank_jun = values[:11]
        if not slot or slot[0] != group:
            raise RuntimeError(f"Unexpected slot {slot!r} in group {group}")
        rows.append(
            {
                "group": group,
                "group_slot": slot,
                "team": team,
                "pot": pot,
                "confederation": conf,
                "method_of_qualification": method,
                "date_of_qualification": date,
                "finals_appearance": appearance,
                "last_appearance": last,
                "previous_best": best,
                "fifa_ranking_nov_2025": rank_nov,
            }
        )
    if len(rows) != 4:
        raise RuntimeError(f"Expected 4 teams in group {group}, got {len(rows)}")
    return rows


def main() -> None:
    all_rows: list[dict] = []
    for g in GROUP_LETTERS:
        path = RAW_DIR / f"wikipedia_2026_world_cup_group_{g}.html"
        all_rows.extend(parse_group(g, path))
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Wrote {len(all_rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
