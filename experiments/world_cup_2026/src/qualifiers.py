"""Pick the 32 R32 qualifiers from group results and resolve all R32 fixtures.

After group_stage.simulate_group_stage(), each group has a 1st/2nd/3rd/4th
ranking. select_qualifiers() takes those rankings, ranks the 12 third-placed
teams to pick the best 8, applies the precomputed third-place lookup to
slot them into the R32, and resolves every R32 source string (1X, 2X,
3<pool>) into a concrete group_slot.

The third-place lookup and R32 spec list are precomputed once by the caller
(see precompute_qualifier_data()) so the hot loop does pure dict and list
work, never a polars filter / collect.

Third-place ranking ladder (plan section 8):
  1. points
  2. overall goal difference
  3. overall goals scored
  4. FIFA ranking fallback (no H2H, since the teams played in different groups)
"""

from __future__ import annotations

import polars as pl

from .group_stage import GroupResult

ThirdPlaceLookup = dict[str, dict[int, str]]
R32Specs = tuple[tuple[int, str, str], ...]


def precompute_qualifier_data(
    third_place_lookup: pl.DataFrame,
    knockout_slots: pl.DataFrame,
) -> tuple[ThirdPlaceLookup, R32Specs]:
    lookup: ThirdPlaceLookup = {}
    match_id_cols = [c for c in third_place_lookup.columns if c != "qualified_third_groups"]
    for row in third_place_lookup.iter_rows(named=True):
        lookup[row["qualified_third_groups"]] = {
            int(c): row[c] for c in match_id_cols
        }
    r32_specs = tuple(
        (row["match_id"], row["team_a_source"], row["team_b_source"])
        for row in knockout_slots.filter(pl.col("stage") == "R32")
        .sort("match_id")
        .iter_rows(named=True)
    )
    return lookup, r32_specs


def select_qualifiers(
    group_results: dict[str, GroupResult],
    third_place_lookup: ThirdPlaceLookup,
    r32_specs: R32Specs,
    fifa_ranks: dict[str, int],
) -> tuple[dict[int, tuple[str, str]], set[str]]:
    direct: dict[str, str] = {}
    thirds: dict[str, tuple[str, int, int, int]] = {}
    for group, res in group_results.items():
        direct[f"1{group}"] = res.ranking[0]
        direct[f"2{group}"] = res.ranking[1]
        third_slot = res.ranking[2]
        st = res.stats[third_slot]
        thirds[group] = (third_slot, st.points, st.goal_difference, st.goals_for)

    ranked_thirds = sorted(
        thirds.items(),
        key=lambda kv: (
            -kv[1][1],
            -kv[1][2],
            -kv[1][3],
            fifa_ranks[kv[1][0]],
        ),
    )
    key = "".join(sorted(g for g, _ in ranked_thirds[:8]))
    slot_assignments = third_place_lookup[key]
    third_slot_for_match = {mid: thirds[grp][0] for mid, grp in slot_assignments.items()}

    r32_resolution: dict[int, tuple[str, str]] = {}
    qualified_slots: set[str] = set()
    for mid, src_a, src_b in r32_specs:
        sa = direct[src_a] if src_a[0] != "3" else third_slot_for_match[mid]
        sb = direct[src_b] if src_b[0] != "3" else third_slot_for_match[mid]
        r32_resolution[mid] = (sa, sb)
        qualified_slots.add(sa)
        qualified_slots.add(sb)
    return r32_resolution, qualified_slots
