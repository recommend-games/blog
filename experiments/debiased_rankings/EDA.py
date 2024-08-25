# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import date
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
import statsmodels.api as sm
from sklearn.preprocessing import MultiLabelBinarizer

jupyter_black.load()
pl.Config.set_tbl_rows(100)

seed = 23
this_year = date.today().year

# %%
base_dir = Path(".").resolve()
project_dir = base_dir.parent.parent
rankings_dir = project_dir.parent / "bgg-ranking-historicals"
data_dir = project_dir.parent / "board-game-data"
base_dir, project_dir, rankings_dir, data_dir

# %%
games = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl")
    .filter(pl.col("year") >= 1970)
    .filter(pl.col("year") <= this_year)
    .filter(pl.col("min_time") <= 360)
    .filter(pl.col("complexity").is_not_null())
    .filter(pl.col("rank").is_not_null())
    .filter(pl.col("bgg_id") != 91313)  # Video game
    .select(
        "bgg_id",
        "name",
        "year",
        "rank",
        "num_votes",
        "avg_rating",
        "bayes_rating",
        "complexity",
        "min_time",
        pl.col("cooperative").fill_null(False).cast(pl.Int8),
        pl.col("game_type").fill_null([]),
    )
    .with_columns(age=this_year - pl.col("year"))
    .collect()
)
games.shape

# %%
games.describe()

# %%
games.sample(10, seed=seed)

# %%
mlb = MultiLabelBinarizer()
game_types_transformed = mlb.fit_transform(games["game_type"])
game_types_transformed.shape

# %%
game_types = pl.DataFrame(
    data=game_types_transformed.astype(np.int8),
    schema=list(mlb.classes_),
)
game_types.describe()

# %%
data = pl.concat([games, game_types], how="horizontal")
data.shape

# %%
data.sample(10, seed=seed)

# %%
endog = data["avg_rating"].to_pandas()
exog = sm.add_constant(
    data.select(
        "age",
        "complexity",
        "min_time",
        "cooperative",
        "Abstract Game:4666",
        "Children's Game:4665",
        "Customizable:4667",
        "Family Game:5499",
        "Party Game:5498",
        "Strategy Game:5497",
        "Thematic:5496",
        "War Game:4664",
    ).to_pandas()
)
model = sm.OLS(endog=endog, exog=exog).fit()

# %%
model.summary().tables[1]

# %%
influence = model.get_influence()
rating_debiased = influence.resid + np.mean(endog)

# %%
rating_dummies = 5.5
num_dummies = data.select(pl.col("num_votes").sum()).item() / 10_000

data = (
    data.with_columns(
        pl.Series("avg_rating_debiased", rating_debiased),
    )
    .with_columns(
        bayes_rating_debiased=(
            pl.col("avg_rating_debiased") * pl.col("num_votes")
            + rating_dummies * num_dummies
        )
        / (pl.col("num_votes") + num_dummies),
    )
    .with_columns(
        rank_debiased=pl.col("bayes_rating_debiased").rank(
            method="min",
            descending=True,
        )
    )
    .with_columns(
        avg_rating_change=pl.col("avg_rating") - pl.col("avg_rating_debiased"),
        bayes_rating_change=pl.col("bayes_rating") - pl.col("bayes_rating_debiased"),
        rank_change=pl.col("rank") - pl.col("rank_debiased"),
    )
    .sort("rank_debiased")
)

data.shape

# %%
data.head(100)

# %%
data.sort("bayes_rating_change").head(10)
