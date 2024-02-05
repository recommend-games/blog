import logging
import sys
from dataclasses import replace
from pathlib import Path

import polars as pl

from synthetic_control.data import REVIEWS
from synthetic_control.plots import process_game


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    plot_dir = (Path(".") / "effect_plots").resolve()
    plot_dir.mkdir(parents=True, exist_ok=True)
    rating_data = pl.scan_csv("num_ratings.csv")

    for game in REVIEWS:
        game = replace(game, days_before=90, days_after=60)
        print(game)
        process_game(
            rating_data=rating_data,
            game=game,
            plot_dir=plot_dir,
            threshold_rmse_slsqp=0.05,
        )


if __name__ == "__main__":
    main()
