"""Knockout-stage simulation: R32 through FINAL.

build_knockout_context() pulls the static knockout bracket and per-team
metadata (Elo, host country) once from the loaded DataFrames. Per simulation,
simulate_knockout() walks the 31 knockout matches in match_id order, sampling
90-minute goals via the cached Poisson model and resolving extra time /
penalties by drawing the advancing team from the Elo expected score.

Source resolution at runtime:
  R32 (matches 73-88)  - looked up from the r32_resolution dict supplied by
                          qualifiers.select_qualifiers
  R16+ (matches 89-104) - the team_a_source / team_b_source are always W<N>;
                          resolved from the running winners dict
"""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from . import config
from .poisson_model import elo_expected_score, lambdas_for_rounded_diff


@dataclass(frozen=True, slots=True)
class KnockoutMatchSpec:
    match_id: int
    stage: str
    team_a_source: str
    team_b_source: str
    venue_country: str


@dataclass(frozen=True, slots=True)
class KnockoutContext:
    matches: tuple[KnockoutMatchSpec, ...]
    elo: dict[str, int]
    host_country: dict[str, str]


def build_knockout_context(
    knockout_slots: pl.DataFrame,
    teams: pl.DataFrame,
) -> KnockoutContext:
    matches = tuple(
        KnockoutMatchSpec(
            match_id=row["match_id"],
            stage=row["stage"],
            team_a_source=row["team_a_source"],
            team_b_source=row["team_b_source"],
            venue_country=row["venue_country"],
        )
        for row in knockout_slots.sort("match_id").iter_rows(named=True)
    )
    elo = {row["group_slot"]: int(row["elo"]) for row in teams.iter_rows(named=True)}
    host_country = {
        row["group_slot"]: row["host_country"] or ""
        for row in teams.iter_rows(named=True)
    }
    return KnockoutContext(matches=matches, elo=elo, host_country=host_country)


def simulate_knockout(
    r32_resolution: dict[int, tuple[str, str]],
    ctx: KnockoutContext,
    rng,
    host_advantage: int = config.HOST_ADVANTAGE,
) -> dict[int, str]:
    winners: dict[int, str] = {}
    for m in ctx.matches:
        if m.match_id in r32_resolution:
            ta, tb = r32_resolution[m.match_id]
        else:
            ta = winners[int(m.team_a_source[1:])]
            tb = winners[int(m.team_b_source[1:])]

        ha = host_advantage if ctx.host_country[ta] == m.venue_country else 0
        hb = host_advantage if ctx.host_country[tb] == m.venue_country else 0
        elo_diff = ctx.elo[ta] - ctx.elo[tb] + ha - hb

        lam_a, lam_b = lambdas_for_rounded_diff(round(elo_diff))
        ga = int(rng.poisson(lam_a))
        gb = int(rng.poisson(lam_b))

        if ga > gb:
            winners[m.match_id] = ta
        elif gb > ga:
            winners[m.match_id] = tb
        else:
            p_a = elo_expected_score(elo_diff)
            winners[m.match_id] = ta if rng.random() < p_a else tb
    return winners
