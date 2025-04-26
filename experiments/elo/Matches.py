# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl

jupyter_black.load()
pl.Config.set_tbl_rows(100)
seed = 13

# %%
matches = (
    pl.scan_ndjson("matches.jl")
    .drop("id", "scraped_at")
    .with_columns(pl.col("timestamp").cast(pl.Int64))
    .with_columns(
        pl.from_epoch("timestamp").dt.convert_time_zone(time_zone="UTC"),
        num_players=pl.col("players").list.len(),
    )
    .filter(pl.col("num_players") > 1)
    .filter(
        pl.col("players")
        .list.eval(pl.element().struct.field("place").is_not_null())
        .list.all()
    )
)

# %%
matches.head(10).collect()

# %%
games_info = pl.scan_ndjson("games.jl").select(
        pl.col("id").alias("game_id"),
        pl.col("name").alias("game_slug"),
        "bgg_id",
        "display_name_en",
        "games_played",
    )
games_matches = (
    matches.group_by("game_id")
    .agg(
        num_matches=pl.len(),
        min_players=pl.col("num_players").min(),
        max_players=pl.col("num_players").max(),
        first=pl.col("timestamp").min(),
        last=pl.col("timestamp").max(),
    )
)
all_games = games_info.join(games_matches, on='game_id', how='full').collect()
all_games.shape

# %%
all_games.describe()

# %%
all_games.filter(pl.col("min_players") == 2).filter(pl.col("max_players") == 2).describe()
