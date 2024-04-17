import numpy as np
import polars as pl


def gini_report(
    num_ratings: pl.Series,
    *,
    print_report: bool = False,
) -> tuple[int, np.ndarray, pl.Series, float]:
    num_games = len(num_ratings)
    sum_ratings = num_ratings.sum()
    linear = np.linspace(0, 1, num_games)
    share = num_ratings.cum_sum() / sum_ratings
    gini_coefficient = 2 * (linear - share).mean()
    share_1pct = 1 - share[int(num_games * 0.99)]
    bottom_1pct = (share <= 0.01).mean() or 0
    assert isinstance(bottom_1pct, float)

    if print_report:
        print(f"Total number of ranked games: {num_games:,d}")
        print(f"Total number of ratings: {sum_ratings:,d}")
        print(f"Overall Gini coefficient: {gini_coefficient:.3f}")
        print(f"Share of the top 1% ({num_games*.01:.0f} games): {share_1pct:.1%}")
        print(f"The bottom {bottom_1pct:.1%} games account for 1% of all ratings")

    return num_games, linear, share, gini_coefficient
