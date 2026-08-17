"""Blow-out rate analysis for World Cup group stages.

Computes the share of group-stage matches won by 3+ goals for each
32-team World Cup (1998–2022) using the martj42 international-results
dataset, then appends the 2026 figure from this project's results.csv.

Reads:
  <path/to/martj42/results.csv>   (supplied via --results)
  data/processed/results.csv      (this project's played scorelines)
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from world_cup_2026 import config

EDITIONS = [1998, 2002, 2006, 2010, 2014, 2018, 2022]
GROUP_MATCHES_PER_EDITION = 48  # 8 groups × 6 matches in the 32-team era


def _blowout_rate(rows: list[dict], year: int) -> tuple[int, int]:
    """Return (n_blowouts, n_matches) for the group stage of the given year."""
    wc_rows = sorted(
        (r for r in rows if r["tournament"] == "FIFA World Cup" and r["date"][:4] == str(year)),
        key=lambda r: r["date"],
    )
    group_stage = wc_rows[:GROUP_MATCHES_PER_EDITION]
    blowouts = sum(
        1 for r in group_stage
        if r["home_score"] not in ("", "NA") and r["away_score"] not in ("", "NA")
        and abs(int(r["home_score"]) - int(r["away_score"])) >= 3
    )
    return blowouts, len(group_stage)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        required=True,
        metavar="PATH",
        help="Path to the martj42 international_results/results.csv",
    )
    args = parser.parse_args()

    with open(args.results, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    print(f"{'Edition':<10} {'Blow-outs':>10}  {'Rate':>6}")
    total_b, total_m = 0, 0
    for year in EDITIONS:
        b, m = _blowout_rate(rows, year)
        total_b += b
        total_m += m
        print(f"{year:<10} {b}/{m:>2}         {b/m*100:>5.1f}%")
    print(f"{'Average':<10} {total_b}/{total_m}      {total_b/total_m*100:>5.1f}%")

    results_2026 = config.RESULTS_CSV
    if results_2026.exists():
        with open(results_2026, newline="", encoding="utf-8") as fh:
            r2026 = list(csv.DictReader(fh))
        group = [r for r in r2026 if int(r["match_id"]) <= 72]
        b2026 = sum(
            1 for r in group
            if abs(int(r["home_goals"]) - int(r["away_goals"])) >= 3
        )
        m2026 = len(group)
        print(f"{'2026':<10} {b2026}/{m2026:>2}         {b2026/m2026*100:>5.1f}%")
    else:
        print("2026 results not found — run parse_results first.")
