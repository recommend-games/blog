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

game_ids = ("snooker", "tennis_wta", "football_international")
names = ("Snooker", "Tennis (WTA)", "Football (men's national teams)")
colors = ("darkred", "darkorange", "darkgreen")
color_palette = dict(zip(names, colors))

threshold_regular = 25

# %%
player_stats_dir = Path("../csv/player_stats/").resolve()
plot_dir = Path("../plots/").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
player_stats_dir, plot_dir

# %%
df = (
    pl.scan_csv(
        [player_stats_dir / f"{game_id}.csv" for game_id in game_ids],
        include_file_paths="file_path",
    )
    .filter(pl.col("num_matches") >= threshold_regular)
    .select(
        pl.col("elo_rating").alias("Elo rating"),
        pl.col("file_path")
        .str.extract(r"^.*/(.*)\.csv", 1)
        .replace(game_ids, names)
        .alias("Game"),
    )
    .collect()
)
df.shape

# %%
clip = df.select(
    min=pl.quantile("Elo rating", 0.001),
    max=pl.quantile("Elo rating", 0.999),
).row(0)
clip

# %%
_, ax = plt.subplots()
sns.kdeplot(
    data=df,
    x="Elo rating",
    hue="Game",
    palette=color_palette,
    common_norm=False,
    clip=clip,
    ax=ax,
)
ax.grid(True)
ax.set_title("Elo ratings distributions")
plt.tight_layout()
path_suffix = "_".join(sorted(game_ids))
plt.savefig(plot_dir / f"elo_distribution_{path_suffix}.png")
plt.savefig(plot_dir / f"elo_distribution_{path_suffix}.svg")
plt.show()
