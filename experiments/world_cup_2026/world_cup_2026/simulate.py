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

import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
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


def _simulate_chunk(
    chunk_size: int,
    child_seed,
    slots: list[str],
    group_ctx: dict[str, group_stage.GroupContext],
    ko_ctx: knockout.KnockoutContext,
    third_place_dict: qualifiers.ThirdPlaceLookup,
    r32_specs: qualifiers.R32Specs,
    fifa_ranks: dict[str, int],
    lambdas_a: np.ndarray,
    lambdas_b: np.ndarray,
    fixed_mask: np.ndarray | None = None,
    fixed_a: np.ndarray | None = None,
    fixed_b: np.ndarray | None = None,
    fixed_ko_winners: dict[int, str] | None = None,
    show_progress: bool = False,
) -> Accumulator:
    rng = np.random.default_rng(child_seed)
    goals_a = rng.poisson(lambdas_a, size=(chunk_size, len(lambdas_a)))
    goals_b = rng.poisson(lambdas_b, size=(chunk_size, len(lambdas_b)))

    # Pin already-played matches to their actual scoreline in every simulation;
    # the standings, tie-breaks and qualification then fall out as normal.
    if (
        fixed_mask is not None
        and fixed_a is not None
        and fixed_b is not None
        and fixed_mask.any()
    ):
        goals_a[:, fixed_mask] = fixed_a
        goals_b[:, fixed_mask] = fixed_b

    acc = Accumulator(slots=slots)
    iterator = range(chunk_size)
    if show_progress:
        iterator = tqdm(iterator, desc=f"Simulating {chunk_size:,} tournaments")
    for sim_idx in iterator:
        group_results = group_stage.simulate_group_stage(
            group_ctx, goals_a[sim_idx], goals_b[sim_idx]
        )
        r32_resolution, qualified_slots = qualifiers.select_qualifiers(
            group_results, third_place_dict, r32_specs, fifa_ranks
        )
        winners = knockout.simulate_knockout(
            r32_resolution, ko_ctx, rng, fixed_winners=fixed_ko_winners
        )
        acc.update(group_results, qualified_slots, winners)
    return acc


def _merge_accumulators(parts: list[Accumulator], slots: list[str]) -> Accumulator:
    merged = Accumulator(slots=slots)
    for acc in parts:
        merged.finish_1st += acc.finish_1st
        merged.finish_2nd += acc.finish_2nd
        merged.finish_3rd += acc.finish_3rd
        merged.finish_4th += acc.finish_4th
        merged.reach_r32 += acc.reach_r32
        merged.reach_r16 += acc.reach_r16
        merged.reach_qf += acc.reach_qf
        merged.reach_sf += acc.reach_sf
        merged.reach_final += acc.reach_final
        merged.winner += acc.winner
    return merged


def _build_fixed_results(
    group_matches: pl.DataFrame,
    results: pl.DataFrame | None,
) -> tuple[np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    """Align played scorelines to the lambda/goal column order.

    Column i corresponds to group_matches row i (the same order
    _precompute_group_lambdas iterates), so the mask and value arrays are
    built off that row order. home_goals -> team_a, away_goals -> team_b.
    """
    if results is None or results.height == 0:
        return None, None, None
    score = {
        row["match_id"]: (row["home_goals"], row["away_goals"])
        for row in results.iter_rows(named=True)
    }
    match_ids = group_matches["match_id"].to_list()
    fixed_idx = [i for i, mid in enumerate(match_ids) if mid in score]
    mask = np.zeros(len(match_ids), dtype=bool)
    mask[fixed_idx] = True
    fixed_a = np.array([score[match_ids[i]][0] for i in fixed_idx], dtype=np.int64)
    fixed_b = np.array([score[match_ids[i]][1] for i in fixed_idx], dtype=np.int64)
    return mask, fixed_a, fixed_b


def _build_fixed_ko_winners(
    teams: pl.DataFrame,
    knockout_slots: pl.DataFrame,
    results: pl.DataFrame | None,
) -> dict[int, str] | None:
    """Map played knockout matches (match_id >= 73) to the advancing group_slot.

    results.winner is a team_id; the knockout engine works in group_slot space,
    so translate it here. Knockout results should be pinned cumulatively (every
    played match up to the current point) so the bracket feeding each pin is
    deterministic.
    """
    if results is None or "winner" not in results.columns:
        return None
    slot_by_team_id = {
        row["team_id"]: row["group_slot"] for row in teams.iter_rows(named=True)
    }
    ko_match_ids = set(knockout_slots["match_id"].to_list())
    fixed: dict[int, str] = {}
    for row in results.iter_rows(named=True):
        mid = row["match_id"]
        if mid <= 72:
            continue
        if mid not in ko_match_ids:
            raise RuntimeError(f"results: match_id {mid} is not a knockout fixture")
        slot = slot_by_team_id.get(row["winner"])
        if slot is None:
            raise RuntimeError(
                f"results: unknown winner team_id {row['winner']!r} for match {mid}"
            )
        fixed[mid] = slot
    return fixed or None


def run_simulation(
    n_simulations: int = config.N_SIMULATIONS,
    seed: int = config.SEED,
    show_progress: bool = True,
    n_workers: int | None = None,
    teams_csv: Path = config.TEAMS_CSV,
    results: pl.DataFrame | None = None,
) -> tuple[Accumulator, pl.DataFrame]:
    teams = load_data.load_teams(teams_csv)
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
    fixed_mask, fixed_a, fixed_b = _build_fixed_results(group_matches, results)
    fixed_ko_winners = _build_fixed_ko_winners(teams, knockout_slots, results)

    if n_workers is None:
        n_workers = os.cpu_count() or 1
    n_workers = max(1, min(n_workers, n_simulations))

    base, rem = divmod(n_simulations, n_workers)
    chunk_sizes = [base + (1 if i < rem else 0) for i in range(n_workers)]
    child_seeds = np.random.SeedSequence(seed).spawn(n_workers)

    if n_workers == 1:
        acc = _simulate_chunk(
            chunk_sizes[0],
            child_seeds[0],
            slots,
            group_ctx,
            ko_ctx,
            third_place_dict,
            r32_specs,
            fifa_ranks,
            lambdas_a,
            lambdas_b,
            fixed_mask,
            fixed_a,
            fixed_b,
            fixed_ko_winners,
            show_progress=show_progress,
        )
        return acc, teams

    mp_ctx = mp.get_context("spawn")
    parts: list[Accumulator] = []
    with ProcessPoolExecutor(max_workers=n_workers, mp_context=mp_ctx) as ex:
        futures = [
            ex.submit(
                _simulate_chunk,
                chunk_sizes[i],
                child_seeds[i],
                slots,
                group_ctx,
                ko_ctx,
                third_place_dict,
                r32_specs,
                fifa_ranks,
                lambdas_a,
                lambdas_b,
                fixed_mask,
                fixed_a,
                fixed_b,
                fixed_ko_winners,
                False,
            )
            for i in range(n_workers)
        ]
        iterator = as_completed(futures)
        if show_progress:
            iterator = tqdm(
                iterator,
                total=n_workers,
                desc=(
                    f"Simulating {n_simulations:,} tournaments across "
                    f"{n_workers} workers"
                ),
            )
        for fut in iterator:
            parts.append(fut.result())
    return _merge_accumulators(parts, slots), teams


def write_outputs(
    acc: Accumulator,
    teams: pl.DataFrame,
    n_simulations: int,
    output_dir: Path = config.OUTPUTS,
    elo_snapshot_date: str | None = None,
    results_snapshot_date: str = "",
    n_results_fixed: int = 0,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    n = float(n_simulations)
    by_slot = {row["group_slot"]: row for row in teams.iter_rows(named=True)}

    team_rows = []
    for i, slot in enumerate(acc.slots):
        t = by_slot[slot]
        n_wins = int(acc.winner[i])
        p_winner = n_wins / n
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
                "n_wins": n_wins,
                "p_winner": p_winner,
                "implied_decimal_odds": (1.0 / p_winner) if p_winner > 0 else float("nan"),
            }
        )
    team_df = pl.DataFrame(team_rows)
    prob_cols = [
        "p_group_winner",
        "p_qualify_group",
        "p_reach_r32",
        "p_reach_r16",
        "p_reach_qf",
        "p_reach_sf",
        "p_reach_final",
        "p_winner",
    ]
    team_df = team_df.with_columns(
        *[pl.col(c).round(5) for c in prob_cols],
        pl.col("implied_decimal_odds").round(2),
        pl.col("elo").rank("ordinal", descending=True).cast(pl.Int64).alias("elo_rank"),
    )
    team_df = team_df.sort(
        ["n_wins", "elo", "fifa_ranking"],
        descending=[True, True, False],
    ).with_columns(
        pl.when(pl.col("n_wins") > 0)
        .then(pl.int_range(1, pl.len() + 1, dtype=pl.Int64))
        .otherwise(None)
        .alias("title_probability_rank"),
    ).with_columns(
        (pl.col("elo_rank") - pl.col("title_probability_rank")).alias("rank_difference"),
    )
    team_df.write_csv(output_dir / "team_probabilities.csv")

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
    group_df = pl.DataFrame(group_rows)
    group_prob_cols = [
        "p_finish_1st",
        "p_finish_2nd",
        "p_finish_3rd",
        "p_finish_4th",
        "p_qualify",
        "p_eliminated",
    ]
    group_df = group_df.with_columns(
        *[pl.col(c).round(5) for c in group_prob_cols]
    ).sort(["group", "p_qualify"], descending=[False, True])
    group_df.write_csv(output_dir / "group_probabilities.csv")

    if elo_snapshot_date is None:
        snapshot_date_path = config.DATA_RAW / "elo_snapshot_date.txt"
        elo_snapshot_date = (
            snapshot_date_path.read_text().strip()
            if snapshot_date_path.exists()
            else ""
        )
    pl.DataFrame(
        [
            {
                "n_simulations": n_simulations,
                "seed": config.SEED,
                "elo_snapshot_date": elo_snapshot_date,
                "results_snapshot_date": results_snapshot_date,
                "n_results_fixed": n_results_fixed,
                "total_goals": config.TOTAL_GOALS,
                "host_advantage": config.HOST_ADVANTAGE,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    ).write_csv(output_dir / "simulation_summary.csv")
