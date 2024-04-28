# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import date
import jupyter_black
import polars as pl

jupyter_black.load()
pl.Config.set_tbl_rows(200)

this_year = date.today().year

# %%
games = (
    pl.scan_csv("../../../board-game-data/scraped/bgg_GameItem.csv")
    .select("bgg_id", "name", "year", "cooperative", "compilation_of")
    .filter(pl.col("compilation_of").is_null())
    .drop("compilation_of")
    .with_columns(pl.col("cooperative").fill_null(0).cast(pl.Boolean))
    .collect()
)
games.shape

# %%
games["cooperative"].mean()

# %%
games.filter("cooperative").sort("year", nulls_last=True).head(20)

# %%
years = (
    games.filter(pl.col("year").is_not_null())
    .group_by("year")
    .agg(
        num_games=pl.len(),
        num_coops=pl.col("cooperative").sum(),
        share_coops=pl.col("cooperative").mean(),
    )
    .with_columns(num_competitives=pl.col("num_games") - pl.col("num_coops"))
    .sort("year")
)

# %%
years.filter(pl.col("year").is_between(this_year - 100, this_year))
