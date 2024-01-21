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
import polars as pl
import jupyter_black
import seaborn as sns
from orchard.game import OrchardGame

jupyter_black.load()

# %%
game = OrchardGame()
results = game.run_games(1_000_000)

# %%
data = results.select(
    pl.when(pl.col("win"))
    .then(pl.lit("Win"))
    .otherwise(pl.lit("Loss"))
    .alias("Outcome"),
    pl.col("round_length").alias("Game length"),
)
data.shape

# %%
sns.histplot(
    data=data,
    x="Game length",
    hue="Outcome",
    stat="proportion",
    discrete=True,
    common_norm=True,
    multiple="stack",
)
