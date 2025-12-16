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
    "avg_rating",
    "bayes_rating",
    "num_votes",
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
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20

output_notebook()

# %%
# Prepare data for Bokeh: filter, convert to pandas, and scale marker sizes
bokeh_df = (
    plot_df.drop_nulls(["p_deterministic", "complexity", "num_all_matches"])
).to_pandas()

# Scale marker size based on number of matches (num_all_matches)
matches = bokeh_df["num_all_matches"].astype("float64")
if matches.max() > matches.min():
    bokeh_df["size"] = 6 + (matches - matches.min()) * (20 - 6) / (
        matches.max() - matches.min()
    )
else:
    bokeh_df["size"] = 10.0

# Ensure game_type exists (will be filled later in the pipeline)
if "game_type" not in bokeh_df.columns:
    bokeh_df["game_type"] = "Unknown"

game_types = sorted(bokeh_df["game_type"].unique().tolist())
# Use up to 20 distinct colours; if there are more types, colours will repeat
palette = Category20[20] if len(game_types) > 2 else Category20[3]

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

p.circle(
    x="p_deterministic",
    y="complexity",
    size="size",
    source=source,
    fill_alpha=0.7,
    line_color=None,
    color=color_mapping,
    legend_field="game_type",
)

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
p.legend.location = "bottom_right"
p.legend.click_policy = "hide"

show(p)

# %%
plot_df.sort("std_dev", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("std_dev", descending=False, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=False, nulls_last=True).head(20)
