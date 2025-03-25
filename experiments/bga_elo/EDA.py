# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Board Game Arena data

# %%
import jupyter_black
import polars as pl
import seaborn as sns
from datetime import datetime, timezone

jupyter_black.load()

seed = 13

# %% [markdown]
# ## Games

# %%
schema = {
    "id": pl.Int128,
    "name": pl.Utf8,
    "display_name_en": pl.Utf8,
    "status": pl.Utf8,
    "premium": pl.Boolean,
    "locked": pl.Boolean,
    "weight": pl.Int128,
    "priority": pl.Int128,
    "games_played": pl.Int128,
    "published_on": pl.Datetime,
    "average_duration": pl.Int128,
    "bgg_id": pl.Int128,
    "is_ranking_disabled": pl.Boolean,
}

# %%
games = (
    pl.read_ndjson("results/games.jl", schema=schema)
    .with_columns(days_online=pl.lit(datetime.now()) - pl.col("published_on"))
    .with_columns(
        games_per_day=pl.col("games_played") / pl.col("days_online").dt.total_days()
    )
)
games.shape

# %%
with pl.Config(tbl_rows=100):
    display(games.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
games.sample(10, seed=seed)

# %%
games.sort("games_played", descending=True).head(10)

# %%
games.sort("games_per_day", descending=True).head(10)

# %%
games.sort("weight", descending=True).head(10)

# %%
for k, v in games.partition_by("premium", maintain_order=False, as_dict=True).items():
    print("Premium:", *k)
    display(v.describe())

# %% [markdown]
# ## Rankings

# %%
schema = {
    "id": pl.Int64,
    "ranking": pl.Float64,
    "nbr_game": pl.Int64,
    "rank_no": pl.Int64,
    "game_id": pl.Int64,
}

# %%
rankings = (
    pl.scan_ndjson("results/rankings.jl")
    .select([pl.col(k).cast(v) for k, v in schema.items()])
    .with_columns(elo=pl.col("ranking") - 1300)
    .collect()
)
rankings.shape

# %%
rankings.sample(10, seed=seed)

# %%
with pl.Config(tbl_rows=100):
    display(rankings.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))

# %%
game_ranking_stats = rankings.group_by("game_id").agg(
    num_players=pl.len(),
    elo_mean=pl.col("elo").mean(),
    elo_std=pl.col("elo").std(),
    elo_min=pl.col("elo").min(),
    elo_p01=pl.col("elo").quantile(0.01),
    elo_p05=pl.col("elo").quantile(0.05),
    elo_p25=pl.col("elo").quantile(0.25),
    elo_p50=pl.col("elo").quantile(0.50),
    elo_p75=pl.col("elo").quantile(0.75),
    elo_p95=pl.col("elo").quantile(0.95),
    elo_p99=pl.col("elo").quantile(0.99),
    elo_max=pl.col("elo").max(),
)
game_info = (
    games.filter(~pl.col("is_ranking_disabled"))
    .filter(
        ~pl.col("name").is_in(
            ["vault", "thebrambles", "dicepyramid", "orchard", "grovesolitaire"]
        )
    )
    .select(
        "id",
        "bgg_id",
        "name",
        "display_name_en",
        "premium",
        "weight",
        "days_online",
        "games_played",
        "games_per_day",
    )
    .join(
        game_ranking_stats,
        left_on="id",
        right_on="game_id",
        how="inner",
    )
    .drop("id")
    .with_columns(games_per_player=pl.col("games_played") / pl.col("num_players"))
)
games.shape, game_ranking_stats.shape, game_info.shape

# %%
game_info.sample(10, seed=seed)

# %%
game_info.describe()

# %%
game_info.sort("games_played", descending=True).head(10)

# %%
game_info.sort("num_players", descending=True).head(10)

# %%
game_info.sort("games_per_player", descending=True).head(10)

# %%
game_info.sort("elo_std", descending=True).head(10)

# %% [markdown]
# ## Plots

# %%
most_played = (
    games.sort("games_played", descending=True)
    .head(5)
    .select("id", "display_name_en")
    .join(rankings, left_on="id", right_on="game_id", how="inner")
)
most_played.shape

# %%
sns.kdeplot(
    data=most_played.select("elo", "display_name_en").to_pandas(),
    x="elo",
    hue="display_name_en",
)
