import argparse
import logging
import sys
from dataclasses import replace
from pathlib import Path

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
        default=".",
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
        default="./effect_plots",
    )
    parser.add_argument(
        "--verbose",
        action="count",
        default=0,
        help="Verbosity level (repeat for more verbosity)",
    )
    return parser.parse_args()


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

    for game in REVIEWS:
        game = replace(
            game,
            days_before=args.days_before,
            days_after=args.days_after,
        )
        print(game)

        process_game(
            rating_data=data,
            game=game,
            plot_dir=plot_dir,
            threshold_rmse_slsqp=args.threshold_rmse_slsqp,
            y_label="Num Collections" if args.mode == "collections" else "Num Ratings",
        )


if __name__ == "__main__":
    main()
