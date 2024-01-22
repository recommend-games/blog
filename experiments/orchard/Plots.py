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
from pathlib import Path
import polars as pl
import jupyter_black
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import ticker
from orchard.game import OrchardGame, OrchardGameConfig

jupyter_black.load()
warnings.filterwarnings("ignore")

# %%
num_games = 100_000
random_seed = 42
save_dir = Path().resolve() / "plots"
save_dir.mkdir(parents=True, exist_ok=True)
num_games, save_dir

# %% [markdown]
# # Original Orchard (1986)

# %%
config_original = OrchardGameConfig(
    num_trees=4,
    fruits_per_tree=10,
    fruits_per_basket_roll=2,
    raven_steps=9,
)
config_original

# %%
results_original = OrchardGame.run_games(
    config=config_original,
    num_games=num_games,
    random_seed=random_seed,
)
results_original.shape

# %%
results_original.cast(pl.Int64).describe()

# %%
data_original = results_original.select(
    pl.when(pl.col("win"))
    .then(pl.lit("Win"))
    .otherwise(pl.lit("Loss"))
    .alias("Outcome"),
    pl.col("round_length").alias("Game length"),
)
data_original.shape

# %%
sns.histplot(
    data=data_original,
    x="Game length",
    hue="Outcome",
    hue_order=("Win", "Loss"),
    stat="proportion",
    discrete=True,
    common_norm=True,
    multiple="stack",
)
plt.title("Orchard (1986)")
plt.tight_layout()
plt.savefig(save_dir / "game_length_original.png")
plt.show()

# %% [markdown]
# # First Orchard (2009)

# %%
config_first = OrchardGameConfig(
    num_trees=4,
    fruits_per_tree=4,
    fruits_per_basket_roll=1,
    raven_steps=6,
)
config_first

# %%
results_first = OrchardGame.run_games(
    config=config_first,
    num_games=num_games,
    random_seed=random_seed,
)
results_first.shape

# %%
results_first.cast(pl.Int64).describe()

# %%
data_first = results_first.select(
    pl.when(pl.col("win"))
    .then(pl.lit("Win"))
    .otherwise(pl.lit("Loss"))
    .alias("Outcome"),
    pl.col("round_length").alias("Game length"),
)
data_first.shape

# %%
sns.histplot(
    data=data_first,
    x="Game length",
    hue="Outcome",
    hue_order=("Win", "Loss"),
    stat="proportion",
    discrete=True,
    common_norm=True,
    multiple="stack",
)
plt.title("First Orchard (2009)")
plt.tight_layout()
plt.savefig(save_dir / "game_length_first.png")
plt.show()

# %% [markdown]
# ## Alternative raven steps

# %%
win_rates = [0.0]
for raven_steps in range(1, 11):
    print(raven_steps)
    config_alt = OrchardGameConfig(
        num_trees=4,
        fruits_per_tree=4,
        fruits_per_basket_roll=1,
        raven_steps=raven_steps,
    )
    results_alt = OrchardGame.run_games(
        config=config_alt,
        num_games=num_games,
        random_seed=random_seed,
    )
    win_rate = results_alt["win"].mean()
    print(f"{win_rate:>8.3%}")
    win_rates.append(win_rate)

# %%
sns.barplot(x=range(1, 11), y=win_rates[1:])
plt.title("First Orchard (2009)")
plt.xlabel("Raven steps")
plt.ylabel("Win rate")
plt.tight_layout()
plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
plt.savefig(save_dir / "win_rates_first.png")
plt.show()
