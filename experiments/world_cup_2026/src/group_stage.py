"""Per-simulation group-stage: compute standings and rank teams with FIFA tie-breaks.

The static group/match/team mapping is captured once in build_group_contexts()
and reused across all simulations. Per simulation, rank_group() walks the six
matches of a group, builds per-team stats, and applies the FIFA tie-break
ladder via a composite sort key (the simplified form explicitly allowed by
the plan for the first version).

Tie-break order (smaller key = better rank):
  1. points
  2. head-to-head points among the tied subset
  3. head-to-head goal difference among the tied subset
  4. head-to-head goals scored among the tied subset
  5. overall goal difference
  6. overall goals scored
  7. FIFA ranking (November 2025 snapshot, deterministic fallback)
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

import polars as pl

GROUP_LETTERS = "ABCDEFGHIJKL"


@dataclass(slots=True)
class TeamStats:
    slot: str
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def record(self, gf: int, ga: int) -> None:
        self.goals_for += gf
        self.goals_against += ga
        if gf > ga:
            self.points += 3
        elif gf == ga:
            self.points += 1


@dataclass(frozen=True, slots=True)
class GroupContext:
    group: str
    slots: tuple[str, ...]
    match_indices: tuple[int, ...]
    match_slot_a: tuple[str, ...]
    match_slot_b: tuple[str, ...]
    fifa_ranks: dict[str, int]


@dataclass(slots=True)
class GroupResult:
    group: str
    ranking: list[str]
    stats: dict[str, TeamStats]


def build_group_contexts(
    teams_df: pl.DataFrame,
    group_matches_df: pl.DataFrame,
) -> dict[str, GroupContext]:
    teams = {row["group_slot"]: row for row in teams_df.to_dicts()}
    matches = group_matches_df.to_dicts()
    contexts: dict[str, GroupContext] = {}
    for group in GROUP_LETTERS:
        slots = tuple(sorted(s for s, r in teams.items() if r["group"] == group))
        indices: list[int] = []
        slot_a: list[str] = []
        slot_b: list[str] = []
        for i, m in enumerate(matches):
            if m["group"] == group:
                indices.append(i)
                slot_a.append(m["team_a_slot"])
                slot_b.append(m["team_b_slot"])
        if len(indices) != 6:
            raise RuntimeError(f"Group {group}: expected 6 matches, got {len(indices)}")
        fifa = {s: int(teams[s]["fifa_ranking"]) for s in slots}
        contexts[group] = GroupContext(
            group=group,
            slots=slots,
            match_indices=tuple(indices),
            match_slot_a=tuple(slot_a),
            match_slot_b=tuple(slot_b),
            fifa_ranks=fifa,
        )
    return contexts


def _tiebreak_key(
    slot: str,
    tied: set[str],
    stats: dict[str, TeamStats],
    matches: list[tuple[str, str, int, int]],
    fifa_ranks: dict[str, int],
) -> tuple:
    h2h_pts = h2h_gf = h2h_ga = 0
    for sa, sb, ga, gb in matches:
        if sa not in tied or sb not in tied:
            continue
        if sa == slot:
            h2h_gf += ga
            h2h_ga += gb
            if ga > gb:
                h2h_pts += 3
            elif ga == gb:
                h2h_pts += 1
        elif sb == slot:
            h2h_gf += gb
            h2h_ga += ga
            if gb > ga:
                h2h_pts += 3
            elif ga == gb:
                h2h_pts += 1
    return (
        -h2h_pts,
        -(h2h_gf - h2h_ga),
        -h2h_gf,
        -stats[slot].goal_difference,
        -stats[slot].goals_for,
        fifa_ranks[slot],
    )


def rank_group(ctx: GroupContext, goals_a, goals_b) -> GroupResult:
    stats = {s: TeamStats(s) for s in ctx.slots}
    matches: list[tuple[str, str, int, int]] = []
    for i, sa, sb in zip(ctx.match_indices, ctx.match_slot_a, ctx.match_slot_b):
        ga = int(goals_a[i])
        gb = int(goals_b[i])
        stats[sa].record(ga, gb)
        stats[sb].record(gb, ga)
        matches.append((sa, sb, ga, gb))

    slots = sorted(ctx.slots, key=lambda s: -stats[s].points)
    ranked: list[str] = []
    for _points, group_iter in groupby(slots, key=lambda s: stats[s].points):
        tied = list(group_iter)
        if len(tied) == 1:
            ranked.append(tied[0])
        else:
            tied_set = set(tied)
            tied.sort(key=lambda s: _tiebreak_key(s, tied_set, stats, matches, ctx.fifa_ranks))
            ranked.extend(tied)
    return GroupResult(group=ctx.group, ranking=ranked, stats=stats)


def simulate_group_stage(
    contexts: dict[str, GroupContext],
    goals_a,
    goals_b,
) -> dict[str, GroupResult]:
    return {g: rank_group(ctx, goals_a, goals_b) for g, ctx in contexts.items()}
