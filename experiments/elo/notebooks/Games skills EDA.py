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

jupyter_black.load()

sns.set_style("dark")
pl.Config.set_tbl_rows(100)
pl.Config.set_tbl_width_chars(100)
pl.Config.set_fmt_str_lengths(100)

seed = 13

# %%
columns = [
    "bga_id",
    "bgg_id",
    "display_name_en",
    "games_played",
    "num_all_matches",
    "ratio",
    "num_regular_players",
    "premium",
    "is_ranking_disabled",
    "locked",
    "elo_k",
    "std_dev",
    "p_deterministic",
    "rank",
    "year",
    "complexity",
    "depth_to_complexity",
    "cooperative",
]
len(columns)

# %%
bga = pl.scan_ndjson("../csv/games.jl").rename({"id": "bga_id"})
id_mapping = pl.scan_csv("../csv/bga_bgg_map.csv")
skills = (
    pl.scan_csv("../csv/game_skills.csv")
    .with_columns(pl.col("game_id").str.to_integer(strict=False).alias("bga_id"))
    .drop_nulls("bga_id")
)
bgg = pl.scan_ndjson("~/Recommend.Games/board-game-data/scraped/bgg_GameItem.jl")
all_games = (
    bga.join(id_mapping, on="bga_id", how="left")
    .with_columns(pl.coalesce("bgg_id_right", "bgg_id").alias("bgg_id"))
    .drop("bgg_id_right", "name_right")
    .join(
        skills,
        on="bga_id",
        how="full",
        coalesce=True,
    )
    .with_columns(pl.coalesce("bgg_id", "bgg_id_right"))
    .drop("bgg_id_right", "name_right")
    .join(bgg, how="left", on="bgg_id", coalesce=True)
    .with_columns(
        ratio=pl.col("num_all_matches").fill_null(0) / pl.col("games_played"),
        depth_to_complexity=pl.col("p_deterministic") / pl.col("complexity"),
    )
    .select(columns)
    .with_columns(pl.col(pl.Boolean).fill_null(False))
    .collect()
)
all_games.shape

# %%
all_games.sample(10, seed=seed)

# %%
all_games.describe()

# %%
df = (
    all_games.remove(pl.col("num_regular_players") < 100)
    .remove(pl.col("bgg_id").is_null())
    .remove(pl.col("is_ranking_disabled") & pl.col("cooperative"))
)
df.shape

# %%
df.sample(10, seed=seed)

# %%
df.describe()

# %%
sns.scatterplot(
    data=df,
    x="p_deterministic",
    y="complexity",
)

# %%
df.sort("std_dev", descending=True, nulls_last=True).head(20)

# %%
df.sort("std_dev", descending=False, nulls_last=True).head(20)

# %%
df.sort(
    "depth_to_complexity",
    descending=True,
    nulls_last=True,
).head(20)

# %%
df.sort(
    "depth_to_complexity",
    descending=False,
    nulls_last=True,
).head(20)
