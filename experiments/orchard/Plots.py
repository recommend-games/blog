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
import warnings
import polars as pl
import jupyter_black
import seaborn as sns
from orchard.game import OrchardGame, OrchardGameConfig

jupyter_black.load()
warnings.filterwarnings("ignore")

# %%
# Original Orchard (1986)
config = OrchardGameConfig(
    num_trees=4,
    fruits_per_tree=10,
    fruits_per_basket_roll=2,
    raven_steps=9,
)
# First Orchard (2009)
# config = OrchardGameConfig(
#     num_trees=4,
#     fruits_per_tree=4,
#     fruits_per_basket_roll=1,
#     raven_steps=6,
# )
config

# %%
results = OrchardGame.run_games(config=config, num_games=100_000, random_seed=42)
results.shape

# %%
results.cast(pl.Int64).describe()

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
    # element="step",
)
