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
import numpy as np

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
    "avg_rating",
    "bayes_rating",
    "num_votes",
    "year",
    "complexity",
    "depth_to_complexity",
    "cooperative",
    "game_type",
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
bgg_types = (
    bgg.select("bgg_id", "add_rank")
    .explode("add_rank")
    .unnest("add_rank")
    .group_by("bgg_id")
    .agg(
        game_type=pl.col("name")
        .sort_by("rank", "bayes_rating", descending=[False, True], nulls_last=True)
        .first()
    )
)
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
    .drop("game_type")
    .join(bgg_types, how="left", on="bgg_id", coalesce=True)
    .with_columns(
        ratio=pl.col("num_all_matches").fill_null(0) / pl.col("games_played"),
        depth_to_complexity=pl.col("p_deterministic") / pl.col("complexity"),
    )
    .select(columns)
    .with_columns(
        pl.col(pl.Boolean).fill_null(False),
        pl.col("game_type").fill_null("Uncategorized"),
    )
    .collect()
)
all_games.shape

# %%
all_games.sample(10, seed=seed)

# %%
all_games.describe()

# %%
df = (
    all_games.remove(pl.col("bgg_id").is_null())
    .remove(pl.len().over("bgg_id") > 1)
    .remove(pl.col("num_regular_players") < 100)
    .remove(pl.col("is_ranking_disabled") & pl.col("cooperative"))
)
df.shape

# %%
df.sample(10, seed=seed)

# %%
df.describe()

# %%
plot_df = df.remove(pl.col("num_votes") < 1000)
plot_df.shape

# %%
sns.scatterplot(
    data=plot_df,
    x="p_deterministic",
    y="complexity",
)

# %%
sns.scatterplot(
    data=plot_df,
    x="p_deterministic",
    y="avg_rating",
)

# %%
sns.scatterplot(
    data=plot_df,
    x="p_deterministic",
    y="bayes_rating",
)

# %%
from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, Slope
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10, Category20, Set1

output_notebook()

# %%
# Prepare data for Bokeh: filter, convert to pandas, and scale marker sizes
bokeh_df = (
    plot_df.drop_nulls(["p_deterministic", "complexity", "num_all_matches"])
).to_pandas()

# Scale marker size based on number of matches (num_all_matches)
min_size, max_size = 5, 15
matches = bokeh_df["num_all_matches"].astype("float64")
log_matches = np.log10(matches.clip(lower=1))
bokeh_df["size"] = min_size + (log_matches - log_matches.min()) * (
    max_size - min_size
) / (log_matches.max() - log_matches.min())

game_types = (
    plot_df.group_by("game_type")
    .agg(pl.len())
    .sort("len", descending=True)["game_type"]
)
# Use up to 20 distinct colours; if there are more types, colours will repeat
palette = Category10[9]  # Set1[9]

source = ColumnDataSource(bokeh_df)

p = figure(
    width=900,
    height=550,
    x_axis_label="Estimated skill fraction p (p_deterministic)",
    y_axis_label="BGG complexity",
    tools="pan,wheel_zoom,box_zoom,reset,save",
    title="Estimated skill fraction vs complexity (BGA games)",
)

color_mapping = factor_cmap("game_type", palette=palette, factors=game_types)

p.scatter(
    x="p_deterministic",
    y="complexity",
    size="size",
    marker="circle",
    source=source,
    fill_alpha=0.7,
    line_color=None,
    color=color_mapping,
    legend_field="game_type",
)

# Add a simple linear regression line: complexity ~ p_deterministic
x_vals = bokeh_df["p_deterministic"].to_numpy(dtype=float)
y_vals = bokeh_df["complexity"].to_numpy(dtype=float)
# Filter out any NaNs that might have slipped through
mask = np.isfinite(x_vals) & np.isfinite(y_vals)
x_vals = x_vals[mask]
y_vals = y_vals[mask]
slope, intercept = np.polyfit(x_vals, y_vals, deg=1)
reg_line = Slope(
    gradient=float(slope),
    y_intercept=float(intercept),
    line_width=2,
    line_alpha=0.8,
)
p.add_layout(reg_line)

hover = HoverTool(
    tooltips=[
        ("Game", "@display_name_en"),
        ("Year", "@year"),
        ("Rank", "@rank"),
        ("BGG rating", "@avg_rating{0.00}"),
        ("BGG bayes rating", "@bayes_rating{0.00}"),
        ("BGA plays (games_played)", "@games_played"),
        ("Matches in Elo data", "@num_all_matches"),
        ("Regular players", "@num_regular_players"),
        ("Skill fraction p", "@p_deterministic{0.00}"),
        ("Complexity", "@complexity{0.0}"),
        ("Game type", "@game_type"),
    ]
)

p.add_tools(hover)
p.legend.location = "top_left"
# Currently hides/mutes all the dots. Desirable policy would be to only show that type.
# p.legend.click_policy = "mute"

show(p)

# %%
plot_df.sort("std_dev", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("std_dev", descending=False, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=False, nulls_last=True).head(20)
