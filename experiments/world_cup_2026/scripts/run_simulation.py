"""Run the Monte Carlo simulator and write the three output CSVs."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, simulate  # noqa: E402


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
    args = parser.parse_args()

    started = time.perf_counter()
    acc, teams = simulate.run_simulation(
        n_simulations=args.n_simulations,
        seed=args.seed,
        show_progress=not args.quiet,
    )
    elapsed = time.perf_counter() - started
    print(
        f"Simulated {args.n_simulations:,} tournaments in {elapsed:.1f}s "
        f"({args.n_simulations / elapsed:,.0f}/s)"
    )

    simulate.write_outputs(acc, teams, args.n_simulations)
    print(f"Wrote outputs to {config.OUTPUTS}")


if __name__ == "__main__":
    main()
