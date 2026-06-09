"""Score predictions for the 31 knockout fixtures along the modal bracket.

For each knockout slot we resolve the most-likely team to occupy it:
  - 1X / 2X sources -> max p_finish_1st / p_finish_2nd in group X
  - 3<pool> sources -> max p_finish_3rd across groups in the pool
  - W<N> sources    -> predicted winner of match N (propagated from earlier)

Per match we compute the Poisson score grid (90 minutes), the win/draw/loss
split, the modal score, the top five scorelines, and the probability that
team A advances. For ties in regulation, the advancing team is drawn from
the Elo expected score s_A (matching the simulator's tie-break in plan §9),
so:

  p_team_a_advances = p_team_a_wins_90 + p_draw_90 * s_A

The 'predicted winner' for each match is the team with the higher advance
probability and is fed forward into later rounds. Because we always pick
the modal team, this is a single concrete bracket path, not a Monte Carlo
estimate.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import polars as pl  # noqa: E402

from src import config, load_data, score_predictions  # noqa: E402
from src.poisson_model import elo_expected_score, lambdas_for_rounded_diff  # noqa: E402

OUTPUT = config.OUTPUTS / "knockout_score_predictions.csv"
GROUP_PROBS = config.OUTPUTS / "group_probabilities.csv"


def format_top(scores: list[tuple[int, int, float]]) -> str:
    return "; ".join(f"{i}-{j} ({p * 100:.1f}%)" for i, j, p in scores)


def main() -> None:
    teams = load_data.load_teams()
    knockout = load_data.load_knockout_slots()
    grp_probs = pl.read_csv(GROUP_PROBS)

    by_slot = {row["group_slot"]: row for row in teams.iter_rows(named=True)}
    name_to_slot = {row["team_name"]: row["group_slot"] for row in teams.iter_rows(named=True)}

    # Most-likely 1st / 2nd / 3rd team per group.
    most_likely_finish: dict[str, str] = {}
    best_third_p: dict[str, float] = {}
    for group in "ABCDEFGHIJKL":
        rows = grp_probs.filter(pl.col("group") == group).rows(named=True)
        most_likely_finish[f"1{group}"] = max(rows, key=lambda r: r["p_finish_1st"])["team_name"]
        most_likely_finish[f"2{group}"] = max(rows, key=lambda r: r["p_finish_2nd"])["team_name"]
        third_best = max(rows, key=lambda r: r["p_finish_3rd"])
        most_likely_finish[f"3{group}"] = third_best["team_name"]
        best_third_p[group] = third_best["p_finish_3rd"]

    def resolve(source: str, predicted_winners: dict[int, str]) -> str:
        if source[0] == "1" or source[0] == "2":
            return most_likely_finish[source]
        if source[0] == "3":
            # Pool like "3CEFHI" -> pick the group with the highest unconditional
            # p_finish_3rd among the leading team in that group.
            best_group = max(source[1:], key=lambda g: best_third_p[g])
            return most_likely_finish[f"3{best_group}"]
        if source[0] == "W":
            return predicted_winners[int(source[1:])]
        raise ValueError(f"Unrecognised source: {source!r}")

    predicted_winners: dict[int, str] = {}
    rows: list[dict] = []
    for row in knockout.sort("match_id").iter_rows(named=True):
        team_a = resolve(row["team_a_source"], predicted_winners)
        team_b = resolve(row["team_b_source"], predicted_winners)
        slot_a = name_to_slot[team_a]
        slot_b = name_to_slot[team_b]
        elo_a = int(by_slot[slot_a]["elo"])
        elo_b = int(by_slot[slot_b]["elo"])
        ha = config.HOST_ADVANTAGE if by_slot[slot_a]["host_country"] == row["venue_country"] else 0
        hb = config.HOST_ADVANTAGE if by_slot[slot_b]["host_country"] == row["venue_country"] else 0
        elo_diff = elo_a - elo_b + ha - hb
        lam_a, lam_b = lambdas_for_rounded_diff(round(elo_diff))

        grid = score_predictions.score_grid(lam_a, lam_b)
        p_a90, p_d90, p_b90 = score_predictions.outcome_probs(grid)
        ms_i, ms_j, ms_p = score_predictions.modal_score(grid)
        top5 = score_predictions.top_n_scores(grid, n=5)

        s_a = elo_expected_score(elo_diff)
        p_a_advances = p_a90 + p_d90 * s_a
        winner = team_a if p_a_advances >= 0.5 else team_b
        predicted_winners[row["match_id"]] = winner

        rows.append(
            {
                "match_id": row["match_id"],
                "stage": row["stage"],
                "venue_country": row["venue_country"],
                "team_a_source": row["team_a_source"],
                "team_b_source": row["team_b_source"],
                "team_a_id": by_slot[slot_a]["team_id"],
                "team_a_name": team_a,
                "team_b_id": by_slot[slot_b]["team_id"],
                "team_b_name": team_b,
                "elo_a": elo_a,
                "elo_b": elo_b,
                "elo_diff": elo_diff,
                "expected_goals_a": round(lam_a, 3),
                "expected_goals_b": round(lam_b, 3),
                "p_team_a_wins_90": round(p_a90, 4),
                "p_draw_90": round(p_d90, 4),
                "p_team_b_wins_90": round(p_b90, 4),
                "p_team_a_advances": round(p_a_advances, 4),
                "most_likely_score_90": f"{ms_i}-{ms_j}",
                "most_likely_score_prob_90": round(ms_p, 4),
                "top_5_scores_90": format_top(top5),
                "predicted_winner": winner,
            }
        )

    df = pl.DataFrame(rows)
    df.write_csv(OUTPUT)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
