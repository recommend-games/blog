import argparse
import dataclasses
import json
import logging
import sys
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

import numpy as np
import polars as pl

from synthetic_control.data import REVIEWS
from synthetic_control.plots import process_game

LOGGER = logging.getLogger(__name__)


def arg_parse():
    parser = argparse.ArgumentParser(description="Synthetic Control")
    parser.add_argument(
        "--mode",
        type=str,
        choices=("collections", "ratings"),
        default="collections",
        help="Mode to run the experiment in",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory to read the data from",
    )
    parser.add_argument(
        "--days-before",
        type=int,
        default=90,
    )
    parser.add_argument(
        "--days-after",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--threshold-rmse-slsqp",
        type=float,
        default=0.03,
        help="Threshold of normalised RMSE to use SLSQP model, else use ridge regression",
    )
    parser.add_argument(
        "--plot-dir",
        type=str,
        default="./results",
    )
    parser.add_argument(
        "--results-path",
        type=str,
        default="./results/results.json",
        help="Path to save the results to",
    )
    parser.add_argument(
        "--verbose",
        action="count",
        default=0,
        help="Verbosity level (repeat for more verbosity)",
    )
    return parser.parse_args()


def _default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, np.int_):
        return int(obj)
    raise TypeError("Type not serializable")


def main():
    args = arg_parse()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    LOGGER.info(args)

    data_dir = Path(args.data_dir).resolve()
    data_file = (
        "num_collections.csv" if args.mode == "collections" else "num_ratings.csv"
    )
    data_path = data_dir / data_file
    data = pl.scan_csv(data_path)

    plot_dir = Path(args.plot_dir).resolve()
    plot_dir.mkdir(parents=True, exist_ok=True)

    results_path = Path(args.results_path).resolve()
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results = []

    for game in REVIEWS:
        game = replace(
            game,
            days_before=args.days_before,
            days_after=args.days_after,
        )
        print(game)

        result = process_game(
            rating_data=data,
            game=game,
            plot_dir=plot_dir,
            threshold_rmse_slsqp=args.threshold_rmse_slsqp,
            y_label="Num Collections" if args.mode == "collections" else "Num Ratings",
        )
        relative_plot_path = Path(result.plot_path).relative_to(
            results_path.parent,
            walk_up=True,
        )
        results.append(replace(result, plot_path=relative_plot_path))

    results_dict = [dataclasses.asdict(result) for result in results]
    with results_path.open("w") as file:
        json.dump(
            results_dict,
            file,
            indent=4,
            default=_default,
        )


if __name__ == "__main__":
    main()
