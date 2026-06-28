"""Run the Monte Carlo simulator and write the three output CSVs.

By default this runs the frozen pre-tournament scenario against
data/processed/teams.csv and writes to outputs/. With --conditional it runs
the "results so far" scenario instead: refreshed Elo from teams_conditional.csv,
the played group scorelines pinned from results.csv, written to
outputs/conditional/. The two scenarios never overwrite each other.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from world_cup_2026 import config, load_data, simulate


def _read_date(path: Path) -> str:
    return path.read_text().strip() if path.exists() else ""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n",
        "--n-simulations",
        type=int,
        default=config.N_SIMULATIONS,
        help=f"Number of Monte Carlo simulations (default {config.N_SIMULATIONS:,})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=config.SEED,
        help=f"Random seed (default {config.SEED})",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Hide the progress bar",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: all available CPU cores)",
    )
    parser.add_argument(
        "--conditional",
        action="store_true",
        help=(
            "Condition on results so far: refreshed Elo (teams_conditional.csv) "
            "plus played scorelines (results.csv), written to outputs/{tag}/"
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
        teams_csv = config.TEAMS_CONDITIONAL_CSV
        results = load_data.load_results()
        output_dir = cpaths.outputs
        elo_snapshot_date = _read_date(
            cpaths.data_raw / "elo_snapshot_date.txt"
        )
        results_snapshot_date = _read_date(
            cpaths.data_raw / "results_snapshot_date.txt"
        )
        n_results_fixed = results.height
    else:
        teams_csv = config.TEAMS_CSV
        results = None
        output_dir = config.OUTPUTS
        elo_snapshot_date = None
        results_snapshot_date = ""
        n_results_fixed = 0

    started = time.perf_counter()
    acc, teams = simulate.run_simulation(
        n_simulations=args.n_simulations,
        seed=args.seed,
        show_progress=not args.quiet,
        n_workers=args.workers,
        teams_csv=teams_csv,
        results=results,
    )
    elapsed = time.perf_counter() - started
    workers = args.workers if args.workers is not None else (os.cpu_count() or 1)
    scenario = (
        f"conditional on {n_results_fixed} played results"
        if args.conditional
        else "pre-tournament"
    )
    print(
        f"Simulated {args.n_simulations:,} tournaments ({scenario}) in {elapsed:.1f}s "
        f"({args.n_simulations / elapsed:,.0f}/s) "
        f"using {workers} worker{'s' if workers != 1 else ''}"
    )

    simulate.write_outputs(
        acc,
        teams,
        args.n_simulations,
        output_dir=output_dir,
        elo_snapshot_date=elo_snapshot_date,
        results_snapshot_date=results_snapshot_date,
        n_results_fixed=n_results_fixed,
    )
    print(f"Wrote outputs to {output_dir}")


if __name__ == "__main__":
    main()
