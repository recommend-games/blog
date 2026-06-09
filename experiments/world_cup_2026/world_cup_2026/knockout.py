"""Knockout-stage simulation: R32 through FINAL.

build_knockout_context() pulls the static knockout bracket and per-team
metadata (Elo, host country) once from the loaded DataFrames. Per simulation,
simulate_knockout() walks the five knockout stages in order, batching the
Poisson goal sampling and the extra-time coin flip for every match in a
stage into single rng calls, then determines winners. Sampling has to be
sequential across stages because R16 team-pairs depend on R32 winners.

Source resolution at runtime:
  R32 (matches 73-88)  - looked up from the r32_resolution dict supplied by
                          qualifiers.select_qualifiers
  R16+ (matches 89-104) - the team_a_source / team_b_source are always W<N>;
                          resolved from the running winners dict
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl

from . import config
from .poisson_model import lambdas_for_rounded_diff

STAGE_ORDER = ("R32", "R16", "QF", "SF", "FINAL")


@dataclass(frozen=True, slots=True)
class KnockoutContext:
    matches_by_stage: dict[str, tuple[tuple[int, str, str, str], ...]]
    elo: dict[str, int]
    host_country: dict[str, str]


def build_knockout_context(
    knockout_slots: pl.DataFrame,
    teams: pl.DataFrame,
) -> KnockoutContext:
    by_stage: dict[str, list[tuple[int, str, str, str]]] = {s: [] for s in STAGE_ORDER}
    for row in knockout_slots.sort("match_id").iter_rows(named=True):
        by_stage[row["stage"]].append(
            (
                row["match_id"],
                row["team_a_source"],
                row["team_b_source"],
                row["venue_country"],
            )
        )
    matches_by_stage = {s: tuple(by_stage[s]) for s in STAGE_ORDER}
    elo = {row["group_slot"]: int(row["elo"]) for row in teams.iter_rows(named=True)}
    host_country = {
        row["group_slot"]: row["host_country"] or ""
        for row in teams.iter_rows(named=True)
    }
    return KnockoutContext(
        matches_by_stage=matches_by_stage, elo=elo, host_country=host_country
    )


def simulate_knockout(
    r32_resolution: dict[int, tuple[str, str]],
    ctx: KnockoutContext,
    rng,
    host_advantage: int = config.HOST_ADVANTAGE,
) -> dict[int, str]:
    winners: dict[int, str] = {}
    elo = ctx.elo
    host_country = ctx.host_country
    poisson = rng.poisson

    for stage in STAGE_ORDER:
        for mid, src_a, src_b, venue in ctx.matches_by_stage[stage]:
            if stage == "R32":
                ta, tb = r32_resolution[mid]
            else:
                ta = winners[int(src_a[1:])]
                tb = winners[int(src_b[1:])]
            ha = host_advantage if host_country[ta] == venue else 0
            hb = host_advantage if host_country[tb] == venue else 0
            d = elo[ta] - elo[tb] + ha - hb
            lam_a, lam_b = lambdas_for_rounded_diff(round(d))
            ga = int(poisson(lam_a))
            gb = int(poisson(lam_b))
            if ga > gb:
                winners[mid] = ta
            elif gb > ga:
                winners[mid] = tb
            else:
                p_a = 1.0 / (1.0 + 10.0 ** (-d / 400.0))
                winners[mid] = ta if rng.random() < p_a else tb
    return winners
