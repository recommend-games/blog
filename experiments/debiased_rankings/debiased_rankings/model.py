from typing import Iterable
import numpy as np
import polars as pl
from statsmodels import api as sm


def debias(
    data: pl.DataFrame,
    *,
    target_col: str,
    regressor_cols: Iterable[str],
    votes_col: str = "num_votes",
    rating_dummies: float = 5.5,
) -> tuple[sm.regression.linear_model.RegressionResults, pl.DataFrame]:
    endog = data[target_col].to_pandas()
    exog = sm.add_constant(data.select(*regressor_cols).to_pandas())
    model = sm.OLS(endog=endog, exog=exog).fit()
    influence = model.get_influence()
    target_debiased = influence.resid + np.mean(endog)

    num_dummies = data.select(pl.col(votes_col).sum()).item() / 10_000

    return (
        model,
        data.with_columns(pl.Series(f"{target_col}_debiased", target_debiased))
        .with_columns(
            (
                (
                    pl.col(f"{target_col}_debiased") * pl.col(votes_col)
                    + rating_dummies * num_dummies
                )
                / (pl.col(votes_col) + num_dummies)
            ).alias(f"{target_col}_bayes_debiased")
        )
        .with_columns(
            rank_debiased=pl.col(f"{target_col}_bayes_debiased").rank(
                method="min",
                descending=True,
            )
        )
        .with_columns(
            (pl.col(f"{target_col}_debiased") - pl.col(target_col)).alias(
                f"{target_col}_change",
            ),
            rank_change=pl.col("rank") - pl.col("rank_debiased"),
        ),
    )
