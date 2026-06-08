"""Monte Carlo loop and probability outputs.

run_simulation() loads the static data once, precomputes per-fixture
Poisson lambdas for the 72 group matches, samples all group-stage goals in
one vectorised numpy call, then per simulation walks
group_stage -> qualifiers -> knockout and updates a numpy-backed accumulator.

The accumulator tracks per-team counts for:
  - group finish positions (1st/2nd/3rd/4th)
  - furthest stage reached (R32 / R16 / QF / SF / FINAL / WINNER)

write_outputs() turns those counts into the three CSVs from the plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import polars as pl
from tqdm.auto import tqdm

from . import config, group_stage, knockout, load_data, qualifiers
from .poisson_model import lambdas_for_rounded_diff


@dataclass
class Accumulator:
    slots: list[str]
    idx: dict[str, int] = field(init=False)
    finish_1st: np.ndarray = field(init=False)
    finish_2nd: np.ndarray = field(init=False)
    finish_3rd: np.ndarray = field(init=False)
    finish_4th: np.ndarray = field(init=False)
    reach_r32: np.ndarray = field(init=False)
    reach_r16: np.ndarray = field(init=False)
    reach_qf: np.ndarray = field(init=False)
    reach_sf: np.ndarray = field(init=False)
    reach_final: np.ndarray = field(init=False)
    winner: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.idx = {s: i for i, s in enumerate(self.slots)}
        n = len(self.slots)
        zeros = lambda: np.zeros(n, dtype=np.int64)
        self.finish_1st = zeros()
        self.finish_2nd = zeros()
        self.finish_3rd = zeros()
        self.finish_4th = zeros()
        self.reach_r32 = zeros()
        self.reach_r16 = zeros()
        self.reach_qf = zeros()
        self.reach_sf = zeros()
        self.reach_final = zeros()
        self.winner = zeros()

    def update(
        self,
        group_results: dict[str, group_stage.GroupResult],
        qualified_slots: set[str],
        winners: dict[int, str],
    ) -> None:
        bucket = [self.finish_1st, self.finish_2nd, self.finish_3rd, self.finish_4th]
        for res in group_results.values():
            for pos, slot in enumerate(res.ranking):
                bucket[pos][self.idx[slot]] += 1
        for slot in qualified_slots:
            self.reach_r32[self.idx[slot]] += 1
        for mid, slot in winners.items():
            i = self.idx[slot]
            if mid <= 88:
                self.reach_r16[i] += 1
            elif mid <= 96:
                self.reach_qf[i] += 1
            elif mid <= 100:
                self.reach_sf[i] += 1
            elif mid <= 102:
                self.reach_final[i] += 1
            elif mid == 104:
                self.winner[i] += 1


def _precompute_group_lambdas(
    teams: pl.DataFrame,
    group_matches: pl.DataFrame,
    host_advantage: int,
) -> tuple[np.ndarray, np.ndarray]:
    elo = {row["group_slot"]: int(row["elo"]) for row in teams.iter_rows(named=True)}
    host = {
        row["group_slot"]: row["host_country"] or ""
        for row in teams.iter_rows(named=True)
    }
    n = group_matches.height
    lambdas_a = np.zeros(n)
    lambdas_b = np.zeros(n)
    for i, row in enumerate(group_matches.iter_rows(named=True)):
        sa, sb = row["team_a_slot"], row["team_b_slot"]
        ha = host_advantage if host[sa] == row["venue_country"] else 0
        hb = host_advantage if host[sb] == row["venue_country"] else 0
        d = elo[sa] - elo[sb] + ha - hb
        la, lb = lambdas_for_rounded_diff(round(d))
        lambdas_a[i] = la
        lambdas_b[i] = lb
    return lambdas_a, lambdas_b


def run_simulation(
    n_simulations: int = config.N_SIMULATIONS,
    seed: int = config.SEED,
    show_progress: bool = True,
) -> tuple[Accumulator, pl.DataFrame]:
    teams = load_data.load_teams()
    group_matches = load_data.load_group_matches()
    knockout_slots = load_data.load_knockout_slots()
    third_place_lookup = load_data.load_third_place_lookup()

    group_ctx = group_stage.build_group_contexts(teams, group_matches)
    ko_ctx = knockout.build_knockout_context(knockout_slots, teams)
    third_place_dict, r32_specs = qualifiers.precompute_qualifier_data(
        third_place_lookup, knockout_slots
    )
    fifa_ranks = {
        row["group_slot"]: int(row["fifa_ranking"])
        for row in teams.iter_rows(named=True)
    }
    slots = sorted(teams["group_slot"].to_list())

    lambdas_a, lambdas_b = _precompute_group_lambdas(
        teams, group_matches, config.HOST_ADVANTAGE
    )

    rng = np.random.default_rng(seed)
    all_goals_a = rng.poisson(lambdas_a, size=(n_simulations, len(lambdas_a)))
    all_goals_b = rng.poisson(lambdas_b, size=(n_simulations, len(lambdas_b)))

    acc = Accumulator(slots=slots)
    iterator = range(n_simulations)
    if show_progress:
        iterator = tqdm(iterator, desc=f"Simulating {n_simulations:,} tournaments")
    for sim_idx in iterator:
        group_results = group_stage.simulate_group_stage(
            group_ctx, all_goals_a[sim_idx], all_goals_b[sim_idx]
        )
        r32_resolution, qualified_slots = qualifiers.select_qualifiers(
            group_results, third_place_dict, r32_specs, fifa_ranks
        )
        winners = knockout.simulate_knockout(r32_resolution, ko_ctx, rng)
        acc.update(group_results, qualified_slots, winners)
    return acc, teams


def write_outputs(
    acc: Accumulator,
    teams: pl.DataFrame,
    n_simulations: int,
    output_dir: Path = config.OUTPUTS,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    n = float(n_simulations)
    by_slot = {row["group_slot"]: row for row in teams.iter_rows(named=True)}

    team_rows = []
    for i, slot in enumerate(acc.slots):
        t = by_slot[slot]
        p_winner = acc.winner[i] / n
        p_qualify = acc.reach_r32[i] / n
        team_rows.append(
            {
                "team_id": t["team_id"],
                "team_name": t["team_name"],
                "group": t["group"],
                "elo": t["elo"],
                "fifa_ranking": t["fifa_ranking"],
                "p_group_winner": acc.finish_1st[i] / n,
                "p_qualify_group": p_qualify,
                "p_reach_r32": p_qualify,
                "p_reach_r16": acc.reach_r16[i] / n,
                "p_reach_qf": acc.reach_qf[i] / n,
                "p_reach_sf": acc.reach_sf[i] / n,
                "p_reach_final": acc.reach_final[i] / n,
                "p_winner": p_winner,
                "implied_decimal_odds": (1.0 / p_winner) if p_winner > 0 else float("nan"),
            }
        )
    team_df = pl.DataFrame(team_rows)
    team_df = team_df.with_columns(
        pl.col("elo").rank("ordinal", descending=True).cast(pl.Int64).alias("elo_rank"),
        pl.col("p_winner").rank("ordinal", descending=True).cast(pl.Int64).alias(
            "title_probability_rank"
        ),
    ).with_columns(
        (pl.col("elo_rank") - pl.col("title_probability_rank")).alias("rank_difference")
    )
    team_df.sort("p_winner", descending=True).write_csv(
        output_dir / "team_probabilities.csv"
    )

    group_rows = []
    for i, slot in enumerate(acc.slots):
        t = by_slot[slot]
        p_qualify = acc.reach_r32[i] / n
        group_rows.append(
            {
                "group": t["group"],
                "team_id": t["team_id"],
                "team_name": t["team_name"],
                "p_finish_1st": acc.finish_1st[i] / n,
                "p_finish_2nd": acc.finish_2nd[i] / n,
                "p_finish_3rd": acc.finish_3rd[i] / n,
                "p_finish_4th": acc.finish_4th[i] / n,
                "p_qualify": p_qualify,
                "p_eliminated": 1.0 - p_qualify,
            }
        )
    pl.DataFrame(group_rows).sort(["group", "p_qualify"], descending=[False, True]).write_csv(
        output_dir / "group_probabilities.csv"
    )

    snapshot_date_path = config.DATA_RAW / "elo_snapshot_date.txt"
    elo_snapshot_date = (
        snapshot_date_path.read_text().strip() if snapshot_date_path.exists() else ""
    )
    pl.DataFrame(
        [
            {
                "n_simulations": n_simulations,
                "seed": config.SEED,
                "elo_snapshot_date": elo_snapshot_date,
                "total_goals": config.TOTAL_GOALS,
                "host_advantage": config.HOST_ADVANTAGE,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    ).write_csv(output_dir / "simulation_summary.csv")
