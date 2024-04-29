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
from bokeh.io import output_notebook
import jupyter_black
import polars as pl

jupyter_black.load()
output_notebook()
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
exclude = {
    24331,  # Only some co-op variants?
    9774,  # More activity than game
    6932,  # Co-op only in 2007
    12398,  # Party game, doesn't seem particularly co-op
    2726,  # Doesn't seem co-op
    22351,  # Role-play / teaching aid
    33213,  # Social simulation
    19631,  # Solo puzzle
    9637,  # Sport simulation?
    21627,  # Political simulation
    44362,  # Educational
    7893,  # Educational
    33682,  # Puzzle
}
len(exclude)

# %%
games.filter("cooperative").filter(~pl.col("bgg_id").is_in(exclude)).sort(
    "year",
    nulls_last=True,
).head(50)

# %%
years = (
    games.filter(pl.col("year").is_not_null())
    .group_by("year")
    .agg(
        num_games=pl.len(),
        num_coops=pl.col("cooperative").sum(),
        share_coops=pl.col("cooperative").mean(),
    )
    .with_columns(
        num_competitives=pl.col("num_games") - pl.col("num_coops"),
        share_competitives=1 - pl.col("share_coops"),
    )
    .sort("year")
)

# %%
years.filter(pl.col("year").is_between(this_year - 100, this_year))

# %%
years_filtered = years.filter(pl.col("year").is_between(2000, this_year))
years_filtered.plot.bar(
    x="year",
    y=["num_coops", "num_competitives"],
    stacked=True,
)

# %%
years_filtered.plot.bar(
    x="year",
    y=["share_coops", "share_competitives"],
    stacked=True,
)
