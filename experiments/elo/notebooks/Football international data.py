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
import polars as pl
import seaborn as sns
from elo.game_stats import _optimal_k_and_elo_ratings
from pathlib import Path
from matplotlib import pyplot as plt

jupyter_black.load()
sns.set_style("dark")

seed = 13
elo_scale = 400

# %%
data_dir = Path.home() / "Workspace" / "international_results"
arrow_dir = Path("../results/arrow/matches").resolve()
arrow_dir.mkdir(parents=True, exist_ok=True)
result_dir = Path("../csv/football").resolve()
result_dir.mkdir(parents=True, exist_ok=True)
plot_dir = Path("../plots/football").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
data_dir, arrow_dir, result_dir, plot_dir

# %% [markdown]
# # General EDA
#
# ## Matches

# %%
matches = (
    pl.scan_csv(data_dir / "results.csv", null_values="NA")
    .select(
        pl.col("date").str.to_date("%Y-%m-%d"),
        "home_team",
        "away_team",
        "home_score",
        "away_score",
    )
    .with_columns(pl.col(pl.String).cast(pl.Categorical))
    .drop_nulls()
    .sort("date", maintain_order=True)
    .collect()
)
matches.shape

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %%
matches.lazy().with_columns(
    outcome=pl.when(pl.col("home_score") == pl.col("away_score"))
    .then(0)
    .when(pl.col("home_score") > pl.col("away_score"))
    .then(1)
    .when(pl.col("home_score") < pl.col("away_score"))
    .then(2)
    .otherwise(None),
).drop_nulls().select(
    num_players=2,
    player_ids=pl.when(pl.col("outcome") == 2)
    .then(pl.concat_list("away_team", "home_team"))
    .otherwise(pl.concat_list("home_team", "away_team")),
    places=pl.when(pl.col("outcome") == 0).then([1, 1]).otherwise([1, 2]),
    payoffs=pl.when(pl.col("outcome") == 0).then([0.5, 0.5]).otherwise([1, 0]),
).sink_ipc(
    path=arrow_dir / "football_international.arrow",
)

# %% [markdown]
# ## Teams

# %%
teams = (
    matches.lazy()
    .unpivot(
        on=["home_team", "away_team"],
        value_name="team_name",
        index="date",
    )
    .group_by("team_name")
    .agg(
        num_matches=pl.len(),
        first_match=pl.min("date"),
        last_match=pl.max("date"),
    )
    .collect()
)
teams.shape

# %%
teams.sample(10, seed=seed)

# %%
teams.describe()

# %% [markdown]
# # Elo ratings

# %%
elo_k, elo_scale, two_player_only, elo_ratings = _optimal_k_and_elo_ratings(
    data=pl.scan_ipc(arrow_dir / "football_international.arrow"),
    elo_scale=elo_scale,
)
elo_k, len(elo_ratings)

# %%
elo_df = (
    pl.DataFrame(
        {
            "team_name": pl.Series(elo_ratings.keys(), dtype=pl.Categorical),
            "elo": elo_ratings.values(),
        }
    )
    .join(teams, on="team_name", how="left")
    .sort("elo", descending=True, nulls_last=True)
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
    result_dir / f"elo_ranking_international.csv",
    datetime_format="%+",
    float_precision=3,
)

# %% [markdown]
# ## Rating distribution

# %%
_, ax = plt.subplots()
sns.kdeplot(elo_ratings.values(), ax=ax)
ax.legend([])
ax.grid(True)
ax.set_title(f"Elo ratings distribution of football national teams")
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()
plt.savefig(plot_dir / "elo_distribution_international.png")
plt.savefig(plot_dir / "elo_distribution_international.svg")
plt.show()
