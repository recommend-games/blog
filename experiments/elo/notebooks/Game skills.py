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
from pathlib import Path
from matplotlib import pyplot as plt

jupyter_black.load()
sns.set_style("dark")
pl.Config.set_tbl_rows(20)

threshold_regular = 25

# %%
csv_dir = Path("../csv").resolve()
csv_dir

# %%
p_deterministic_df = (
    pl.scan_csv(csv_dir / "p_deterministic.csv")
    .group_by(pl.col("p_deterministic").round(2))
    .agg(pl.col("std_dev").mean())
    .sort("std_dev")
)

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=p_deterministic_df.collect(),
    x="p_deterministic",
    y="std_dev",
)
ax.grid(True)

# %%
games_df = pl.scan_ndjson(csv_dir / "games.jl").select(
    pl.col("id").alias("game_id"), "bgg_id", "display_name_en"
)

# %%
game_stats_df = (
    pl.scan_csv(csv_dir / "game_stats" / "*.csv", include_file_paths="file_path")
    .filter(pl.col("threshold_matches_regulars") == threshold_regular)
    .with_columns(game_id_str=pl.col("file_path").str.extract(r"^.*/(.*)\.csv", 1))
    .select(
        "game_id_str",
        pl.col("game_id_str").str.to_integer(strict=False).alias("game_id"),
        "num_all_matches",
        "num_connected_matches",
        "num_all_players",
        "num_connected_players",
        "num_regular_players",
        "num_max_matches",
        "two_player_only",
        "elo_k",
        "std_dev",
    )
)

# %%
result = (
    games_df.join(game_stats_df, on="game_id", how="full", coalesce=True)
    .sort("std_dev", nulls_last=True)
    .join_asof(p_deterministic_df, on="std_dev", strategy="nearest")
    .select(
        pl.coalesce("game_id", "game_id_str"),
        "bgg_id",
        pl.coalesce("display_name_en", pl.col("game_id_str").str.to_titlecase()).alias(
            "name"
        ),
        "num_all_matches",
        "num_connected_matches",
        "num_all_players",
        "num_connected_players",
        "num_regular_players",
        "num_max_matches",
        "two_player_only",
        "elo_k",
        "std_dev",
        "p_deterministic",
    )
    .sort("std_dev", descending=True, nulls_last=True)
    .collect()
)
result.shape

# %%
result.filter(pl.col("num_regular_players") >= 100).head(20)

# %%
result.filter(pl.col("num_regular_players") >= 100).tail(20)

# %%
result.write_csv(csv_dir / "game_skills.csv")
