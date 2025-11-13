# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from datetime import date, timedelta
from elo.optimal_k import approximate_optimal_k
from elo.elo_ratings import TwoPlayerElo
from pathlib import Path
from matplotlib import pyplot as plt
from tqdm import tqdm

jupyter_black.load()
pl.Config.set_tbl_rows(200)
sns.set_style("dark")

association = "atp"
seed = 13
elo_scale = 400

# %%
data_dir = Path.home() / "Workspace" / f"tennis_{association}"
result_dir = Path("../csv/tennis").resolve()
result_dir.mkdir(parents=True, exist_ok=True)
plot_dir = Path("../plots/tennis").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
data_dir, result_dir, plot_dir

# %% [markdown]
# # General EDA

# %% [markdown]
# ## Matches

# %%
files = data_dir.rglob(f"{association}_matches_[!d]*.csv")
matches = (
    pl.scan_csv(list(files))
    .select(
        "tourney_id",
        pl.col("tourney_date").cast(pl.String).str.to_date("%Y%m%d"),
        "match_num",
        "winner_id",
        "loser_id",
    )
    .drop_nulls()
    .sort("tourney_date", "match_num")
    .collect()
)
matches.shape

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %% [markdown]
# ## Players

# %%
match_info = (
    matches.lazy()
    .unpivot(
        on=["winner_id", "loser_id"],
        value_name="player_id",
        index="tourney_date",
    )
    .group_by("player_id")
    .agg(
        num_matches=pl.len(),
        first_tourney=pl.min("tourney_date"),
        last_tourney=pl.max("tourney_date"),
    )
)
players = (
    pl.scan_csv(data_dir / f"{association}_players.csv")
    .select(
        "player_id",
        name=pl.concat_str("name_first", "name_last", separator=" ", ignore_nulls=True),
    )
    .drop_nulls()
    .join(match_info, on="player_id", how="left")
    .collect()
)
players.shape

# %%
players.sample(10, seed=seed)

# %%
players.describe()

# %% [markdown]
# # Elo ratings

# %%
matches_array = matches.select("winner_id", "loser_id").to_numpy()
matches_array.shape

# %%
elo_k = approximate_optimal_k(
    matches=matches_array,
    two_player_only=True,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
elo_k

# %%
elo = TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
elo.update_elo_ratings_batch(matches=matches_array, progress_bar=True)

# %%
elo_df = (
    pl.DataFrame(
        {
            "player_id": elo.elo_ratings.keys(),
            "elo": elo.elo_ratings.values(),
        }
    )
    .join(players, on="player_id", how="left")
    .sort("elo", descending=True)
)
elo_df.shape

# %%
elo_df.describe()

# %%
elo_df.head(10)

# %%
elo_df.tail(10)

# %%
elo_df.write_csv(
    result_dir / f"elo_ranking_{association}.csv",
    datetime_format="%+",
    float_precision=3,
)

# %% [markdown]
# ## Rating distribution

# %%
_, ax = plt.subplots()
sns.kdeplot(
    elo.elo_ratings.values(),
    clip=(-elo_scale / 2, elo_scale / 2),
    ax=ax,
)
ax.legend([])
ax.grid(True)
ax.set_title(f"Elo ratings distribution of {association.upper()} players")
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()
plt.savefig(plot_dir / f"elo_distribution_{association}.png")
plt.savefig(plot_dir / f"elo_distribution_{association}.svg")
plt.show()
