"""Build processed/third_place_lookup.csv from Wikipedia's enumeration.

The Wikipedia knockout-stage article has a section
("Combinations of matches in the round of 32") containing a wikitable
that enumerates all C(12, 8) = 495 combinations of qualifying third-placed
teams and, for each combination, which group's third-placed team is
assigned to each R32 slot.

The table layout, per row:
  - cells[0]:                  row number (1..495)
  - cells[1..12]:              12 cells indicating which groups have a
                                qualifying third-placed team (the cell
                                contains the group letter if it qualifies,
                                else empty)
  - cells[-8:]:                assignments to the 8 group winners that face
                                a third-placed team in R32, in source order
                                (1A, 1B, 1D, 1E, 1G, 1I, 1K, 1L)

Output columns: qualified_third_groups (sorted 8-letter key), then one
column per R32 match_id sorted ascending (74, 77, 79, 80, 81, 82, 85, 87),
each holding a single group letter (the group whose third-placed team
plays in that R32 fixture).
"""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUTPUT = PROC / "third_place_lookup.csv"

# Wikipedia's column order, derivable from knockout_slots.csv but small
# enough to keep explicit for clarity. Pairs (group winner letter, R32 match_id).
GROUP_WINNERS_IN_WIKI_ORDER: list[tuple[str, int]] = [
    ("A", 79),
    ("B", 85),
    ("D", 81),
    ("E", 74),
    ("G", 82),
    ("I", 77),
    ("K", 87),
    ("L", 80),
]

SORTED_MATCH_IDS = sorted(mid for _, mid in GROUP_WINNERS_IN_WIKI_ORDER)


def clean(s: str) -> str:
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.DOTALL)
    s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def main() -> None:
    text = (RAW / "wikipedia_2026_world_cup_knockout_stage.html").read_text()
    section_m = re.search(
        r'<h3[^>]*id="Combinations_of_matches_in_the_round_of_32".*?(?=<h[12])',
        text,
        re.DOTALL,
    )
    if not section_m:
        raise RuntimeError("Combinations section not found")
    table_m = re.search(
        r'<table[^>]*class="wikitable[^"]*"[^>]*>.*?</table>',
        section_m.group(0),
        re.DOTALL,
    )
    if not table_m:
        raise RuntimeError("wikitable not found in section")
    trs = re.findall(r"<tr[^>]*>(.*?)</tr>", table_m.group(0), re.DOTALL)

    rows_out = []
    for tr in trs:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.DOTALL)
        # Data rows have 21 cells (or 22 for row 1, with an extra empty cell)
        if len(cells) not in (21, 22):
            continue
        cleaned = [clean(c) for c in cells]
        qualifying = [letter for i, letter in enumerate("ABCDEFGHIJKL") if cleaned[1 + i]]
        if len(qualifying) != 8:
            raise RuntimeError(f"Expected 8 qualifying groups, got {len(qualifying)}: {cleaned}")
        assignments_in_order = cleaned[-8:]
        assignments: dict[int, str] = {}
        for (winner_grp, match_id), assignment_cell in zip(
            GROUP_WINNERS_IN_WIKI_ORDER, assignments_in_order
        ):
            m = re.fullmatch(r"3([A-L])", assignment_cell)
            if not m:
                raise RuntimeError(f"Bad assignment {assignment_cell!r} in row {cleaned[0]}")
            assignments[match_id] = m.group(1)
        assigned = sorted(assignments.values())
        if assigned != sorted(qualifying):
            raise RuntimeError(
                f"Row {cleaned[0]}: qualifying {sorted(qualifying)} != assigned {assigned}"
            )
        row = {"qualified_third_groups": "".join(sorted(qualifying))}
        for mid in SORTED_MATCH_IDS:
            row[str(mid)] = assignments[mid]
        rows_out.append(row)

    if len(rows_out) != 495:
        raise RuntimeError(f"Expected 495 rows, got {len(rows_out)}")

    fields = ["qualified_third_groups", *[str(m) for m in SORTED_MATCH_IDS]]
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"Wrote {len(rows_out)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
