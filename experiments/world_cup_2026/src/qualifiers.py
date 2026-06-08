"""Pick the 32 R32 qualifiers from group results and resolve all R32 fixtures.

After group_stage.simulate_group_stage(), each group has a 1st/2nd/3rd/4th
ranking. select_qualifiers() takes those rankings, ranks the 12 third-placed
teams to pick the best 8, applies the third_place_lookup table to slot them
into the R32, and resolves every R32 source string (1X, 2X, 3<pool>) into a
concrete group_slot.

Third-place ranking ladder (plan section 8):
  1. points
  2. overall goal difference
  3. overall goals scored
  4. FIFA ranking fallback (no H2H, since the teams played in different groups)
"""

from __future__ import annotations

import polars as pl

from .group_stage import GroupResult


def select_qualifiers(
    group_results: dict[str, GroupResult],
    third_place_lookup: pl.DataFrame,
    knockout_slots: pl.DataFrame,
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
    top_eight_groups = sorted(g for g, _ in ranked_thirds[:8])
    key = "".join(top_eight_groups)

    lookup_row = third_place_lookup.filter(
        pl.col("qualified_third_groups") == key
    ).row(0, named=True)
    third_slot_for_match: dict[int, str] = {}
    for col, value in lookup_row.items():
        if col == "qualified_third_groups":
            continue
        third_slot_for_match[int(col)] = thirds[value][0]

    r32_resolution: dict[int, tuple[str, str]] = {}
    qualified_slots: set[str] = set()
    for row in knockout_slots.filter(pl.col("stage") == "R32").iter_rows(named=True):
        mid = row["match_id"]
        sa = _resolve(row["team_a_source"], direct, third_slot_for_match, mid)
        sb = _resolve(row["team_b_source"], direct, third_slot_for_match, mid)
        r32_resolution[mid] = (sa, sb)
        qualified_slots.add(sa)
        qualified_slots.add(sb)
    return r32_resolution, qualified_slots


def _resolve(
    source: str,
    direct: dict[str, str],
    third_slot_for_match: dict[int, str],
    match_id: int,
) -> str:
    if source[0] in "12":
        return direct[source]
    if source[0] == "3":
        return third_slot_for_match[match_id]
    raise ValueError(f"Unexpected R32 source: {source!r}")
