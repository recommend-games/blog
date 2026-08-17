"""Per-fixture score predictions for the group stage.

Walks the 72 group fixtures, looks up the cached Poisson lambdas for each,
and derives the analytical match outcomes: lambdas (expected goals),
win/draw/loss split, the modal scoreline and the top five most-likely
scorelines. No Monte Carlo sampling needed.
"""

from __future__ import annotations

import argparse
import csv

import polars as pl

from world_cup_2026 import config, load_data, score_predictions
from world_cup_2026.poisson_model import lambdas_for_rounded_diff


def format_top(scores: list[tuple[int, int, float]]) -> str:
    return "; ".join(f"{i}-{j} ({p * 100:.1f}%)" for i, j, p in scores)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help=(
            "Use refreshed Elo (teams_conditional.csv) and flag already-played "
            "matches with their actual score; write to outputs/{tag}/"
        ),
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
        teams = load_data.load_teams(cpaths.teams_csv)
        output = cpaths.outputs / "group_score_predictions.csv"
        actual = {
            r["match_id"]: (r["home_goals"], r["away_goals"])
            for r in load_data.load_results().iter_rows(named=True)
        }
    else:
        teams = load_data.load_teams()
        output = config.OUTPUTS / "group_score_predictions.csv"
        actual = {}

    group_matches = load_data.load_group_matches()

    by_slot = {row["group_slot"]: row for row in teams.iter_rows(named=True)}
    elo = {s: int(r["elo"]) for s, r in by_slot.items()}
    host_country = {s: r["host_country"] or "" for s, r in by_slot.items()}

    rows = []
    for row in group_matches.sort("match_id").iter_rows(named=True):
        sa, sb = row["team_a_slot"], row["team_b_slot"]
        ha = config.HOST_ADVANTAGE if host_country[sa] == row["venue_country"] else 0
        hb = config.HOST_ADVANTAGE if host_country[sb] == row["venue_country"] else 0
        elo_diff = elo[sa] - elo[sb] + ha - hb
        lam_a, lam_b = lambdas_for_rounded_diff(round(elo_diff))

        grid = score_predictions.score_grid(lam_a, lam_b)
        p_a, p_d, p_b = score_predictions.outcome_probs(grid)
        ms_i, ms_j, ms_p = score_predictions.modal_score(grid)
        top5 = score_predictions.top_n_scores(grid, n=5)

        record = {
            "match_id": row["match_id"],
            "group": row["group"],
            "round_number": row["round_number"],
            "venue_country": row["venue_country"],
            "team_a_id": by_slot[sa]["team_id"],
            "team_a_name": by_slot[sa]["team_name"],
            "team_b_id": by_slot[sb]["team_id"],
            "team_b_name": by_slot[sb]["team_name"],
            "elo_diff": elo_diff,
            "expected_goals_a": round(lam_a, 3),
            "expected_goals_b": round(lam_b, 3),
            "p_team_a_wins": round(p_a, 4),
            "p_draw": round(p_d, 4),
            "p_team_b_wins": round(p_b, 4),
            "most_likely_score": f"{ms_i}-{ms_j}",
            "most_likely_score_prob": round(ms_p, 4),
            "top_5_scores": format_top(top5),
        }
        if args.conditional:
            played = row["match_id"] in actual
            record["played"] = played
            record["actual_score"] = (
                f"{actual[row['match_id']][0]}-{actual[row['match_id']][1]}"
                if played
                else ""
            )
        rows.append(record)

    df = pl.DataFrame(rows)
    df.write_csv(output)
    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
