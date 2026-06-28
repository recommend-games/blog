"""Score predictions for the 31 knockout fixtures.

By default (and while the group stage is still in progress) this walks a
single "favourites advance" *modal* bracket: each slot is filled by the
most-likely team and each tie by the Elo favourite.

  - 1X / 2X sources -> max p_finish_1st / p_finish_2nd in group X
  - 3<pool> sources -> max p_finish_3rd across groups in the pool
  - W<N> sources    -> predicted winner of match N (propagated from earlier)

Per match we compute the Poisson score grid (90 minutes), the win/draw/loss
split, the modal score, the top five scorelines, and the probability that
team A advances. For ties in regulation the advancing team is drawn from
the Elo expected score s_A (matching the simulator's tie-break in plan §9):

  p_team_a_advances = p_team_a_wins_90 + p_draw_90 * s_A

In `--conditional` mode the bracket follows reality where it is known:
once the whole group stage is in results.csv, the R32 fixtures are resolved
from the *actual* final standings (using the same group_stage + qualifiers
code as the simulator), and any played knockout match propagates its
*actual* winner. Beyond the played front it reverts to the modal favourite.
Conditional output carries `bracket_basis`, `played`, `actual_score` and
`actual_winner` columns; the model's `predicted_winner` is always reported
alongside so prediction and reality sit side by side.
"""

from __future__ import annotations

import argparse

import polars as pl

from world_cup_2026 import config, group_stage, load_data, qualifiers, score_predictions
from world_cup_2026.poisson_model import elo_expected_score, lambdas_for_rounded_diff


def format_top(scores: list[tuple[int, int, float]]) -> str:
    return "; ".join(f"{i}-{j} ({p * 100:.1f}%)" for i, j, p in scores)


def resolve_actual_r32(
    teams: pl.DataFrame,
    group_matches: pl.DataFrame,
    knockout: pl.DataFrame,
    results: pl.DataFrame,
) -> dict[int, tuple[str, str]]:
    """Actual R32 fixtures (match_id -> (slot_a, slot_b)) from the played group
    results, reusing the simulator's own group + qualifier resolution so the
    bracket matches the simulation exactly."""
    gm = group_matches.sort("match_id")
    score = {
        row["match_id"]: (row["home_goals"], row["away_goals"])
        for row in results.iter_rows(named=True)
    }
    goals_a = [score[row["match_id"]][0] for row in gm.iter_rows(named=True)]
    goals_b = [score[row["match_id"]][1] for row in gm.iter_rows(named=True)]

    contexts = group_stage.build_group_contexts(teams, gm)
    group_results = group_stage.simulate_group_stage(contexts, goals_a, goals_b)
    third_dict, r32_specs = qualifiers.precompute_qualifier_data(
        load_data.load_third_place_lookup(), knockout
    )
    fifa_ranks = {
        row["group_slot"]: int(row["fifa_ranking"])
        for row in teams.iter_rows(named=True)
    }
    r32_resolution, _ = qualifiers.select_qualifiers(
        group_results, third_dict, r32_specs, fifa_ranks
    )
    return r32_resolution


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help=(
            "Follow the actual bracket where known (refreshed Elo, played "
            "group standings and knockout results) and the modal favourite "
            "beyond it; write to outputs/{tag}/"
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
        teams = load_data.load_teams(config.TEAMS_CONDITIONAL_CSV)
        group_probs_path = cpaths.outputs / "group_probabilities.csv"
        output = cpaths.outputs / "knockout_score_predictions.csv"
    else:
        teams = load_data.load_teams()
        group_probs_path = config.OUTPUTS / "group_probabilities.csv"
        output = config.OUTPUTS / "knockout_score_predictions.csv"

    knockout = load_data.load_knockout_slots()
    grp_probs = pl.read_csv(group_probs_path)

    by_slot = {row["group_slot"]: row for row in teams.iter_rows(named=True)}
    slot_by_team_id = {
        row["team_id"]: row["group_slot"] for row in teams.iter_rows(named=True)
    }

    # Resolve the actual bracket base + knockout results, if available.
    r32_actual: dict[int, tuple[str, str]] | None = None
    actual_ko_winner: dict[int, str] = {}  # match_id -> winning slot
    actual_ko_score: dict[int, tuple[int, int]] = {}
    if args.conditional and config.RESULTS_CSV.exists():
        results = load_data.load_results()
        group_matches = load_data.load_group_matches()
        if results.filter(pl.col("match_id") <= 72).height == group_matches.height:
            r32_actual = resolve_actual_r32(teams, group_matches, knockout, results)
        for row in results.filter(pl.col("match_id") > 72).iter_rows(named=True):
            actual_ko_winner[row["match_id"]] = slot_by_team_id[row["winner"]]
            actual_ko_score[row["match_id"]] = (row["home_goals"], row["away_goals"])

    # Modal resolution (used wholesale before the group stage completes, and for
    # every slot beyond the played front).
    most_likely_slot: dict[str, str] = {}
    best_third_p: dict[str, float] = {}
    for group in "ABCDEFGHIJKL":
        grp_rows = grp_probs.filter(pl.col("group") == group).rows(named=True)
        most_likely_slot[f"1{group}"] = slot_by_team_id[
            max(grp_rows, key=lambda r: r["p_finish_1st"])["team_id"]
        ]
        most_likely_slot[f"2{group}"] = slot_by_team_id[
            max(grp_rows, key=lambda r: r["p_finish_2nd"])["team_id"]
        ]
        third_best = max(grp_rows, key=lambda r: r["p_finish_3rd"])
        most_likely_slot[f"3{group}"] = slot_by_team_id[third_best["team_id"]]
        best_third_p[group] = third_best["p_finish_3rd"]

    advancing: dict[int, str] = {}  # match_id -> slot that goes through

    def resolve_modal(source: str) -> str:
        if source[0] in "12":
            return most_likely_slot[source]
        if source[0] == "3":
            best_group = max(source[1:], key=lambda g: best_third_p[g])
            return most_likely_slot[f"3{best_group}"]
        if source[0] == "W":
            return advancing[int(source[1:])]
        raise ValueError(f"Unrecognised source: {source!r}")

    rows: list[dict] = []
    for row in knockout.sort("match_id").iter_rows(named=True):
        mid = row["match_id"]
        if r32_actual is not None and row["stage"] == "R32":
            slot_a, slot_b = r32_actual[mid]
        elif r32_actual is not None:
            slot_a = advancing[int(row["team_a_source"][1:])]
            slot_b = advancing[int(row["team_b_source"][1:])]
        else:
            slot_a = resolve_modal(row["team_a_source"])
            slot_b = resolve_modal(row["team_b_source"])

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
        predicted_slot = slot_a if p_a_advances >= 0.5 else slot_b

        played = mid in actual_ko_winner
        if played:
            win_slot = actual_ko_winner[mid]
            if win_slot not in (slot_a, slot_b):
                raise RuntimeError(
                    f"results: winner of knockout match {mid} is not one of its "
                    f"bracket participants ({slot_a} vs {slot_b}); pin knockout "
                    f"results cumulatively so the bracket stays consistent"
                )
        else:
            win_slot = predicted_slot
        advancing[mid] = win_slot

        record = {
            "match_id": mid,
            "stage": row["stage"],
            "venue_country": row["venue_country"],
            "team_a_source": row["team_a_source"],
            "team_b_source": row["team_b_source"],
            "team_a_id": by_slot[slot_a]["team_id"],
            "team_a_name": by_slot[slot_a]["team_name"],
            "team_b_id": by_slot[slot_b]["team_id"],
            "team_b_name": by_slot[slot_b]["team_name"],
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
            "predicted_winner": by_slot[predicted_slot]["team_name"],
        }
        if args.conditional:
            record["bracket_basis"] = "actual" if r32_actual is not None else "modal"
            record["played"] = played
            record["actual_score"] = (
                f"{actual_ko_score[mid][0]}-{actual_ko_score[mid][1]}" if played else ""
            )
            record["actual_winner"] = by_slot[win_slot]["team_name"] if played else ""
        rows.append(record)

    df = pl.DataFrame(rows)
    df.write_csv(output)
    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
