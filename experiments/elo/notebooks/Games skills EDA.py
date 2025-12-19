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
import json

from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    Slope,
    Span,
    CDSView,
    GroupFilter,
    Label,
    LabelSet,
    NumeralTickFormatter,
)
from bokeh.palettes import Category10

jupyter_black.load()

output_notebook()
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
def format_int_col(col: str) -> pl.Expr:
    return (
        pl.when(pl.col(col) >= 10_000)
        .then(
            (pl.col(col) // 1000).map_elements(
                lambda v: f"{v:,}k",
                return_dtype=pl.String,
            ),
        )
        .otherwise(
            pl.col(col).map_elements(
                lambda v: f"{v:,}",
                return_dtype=pl.String,
            ),
        )
    )


# %%
min_size, max_size = 5, 18
bokeh_columns = [
    "p_deterministic",
    "complexity",
    "size",
    "display_name_en",
    "year",
    "game_type",
    "rank",
    "bayes_rating",
    "num_all_matches",
    "num_regular_players",
]
bokeh_df = (
    plot_df.lazy()
    .drop_nulls(["p_deterministic", "complexity", "num_all_matches"])
    .with_columns(log_matches=pl.col("num_all_matches").clip(1).log10())
    .with_columns(
        size=min_size
        + (pl.col("log_matches") - pl.col("log_matches").min())
        * (max_size - min_size)
        / (pl.col("log_matches").max() - pl.col("log_matches").min())
    )
    .select(bokeh_columns)
    .sort("num_all_matches")
    .with_columns(
        num_all_matches=format_int_col("num_all_matches"),
        num_regular_players=format_int_col("num_regular_players"),
    )
    .collect()
)
game_types = (
    bokeh_df.group_by("game_type")
    .agg(pl.len())
    .sort(pl.col("game_type") != "Uncategorized", "len", descending=True)["game_type"]
)
bokeh_df.shape, game_types.shape

# %%
# TODO: Better selection of games (top 10 most played, top 10 highest ranked, mentioned in article)
# TODO: Could this be achieved with a CDSView instead?
label_games = [
    "Terraforming Mars",
    "Wingspan",
    "CATAN",
    "Skat",
]
labels_df = (
    bokeh_df.lazy()
    .filter(pl.col("display_name_en").is_in(label_games))
    .with_columns(label=pl.col("display_name_en"))  # text to show
    .collect()
)
label_source = ColumnDataSource(labels_df)

# %%
# Add a simple linear regression line: complexity ~ p_deterministic
x_vals = bokeh_df["p_deterministic"].to_numpy()
y_vals = bokeh_df["complexity"].to_numpy()
# Filter out any NaNs that might have slipped through
slope, intercept = np.polyfit(x_vals, y_vals, deg=1)
slope, intercept

# %%
# Use up to 10 distinct colours; if there are more types, colours will repeat
palette = Category10[10]

source = ColumnDataSource(bokeh_df)

p = figure(
    width=900,
    height=550,
    x_axis_label="Effective skill level p (p-deterministic index)",
    y_axis_label="BGG complexity",
    tools="pan,wheel_zoom,box_zoom,reset,save",
    title="Skill vs complexity for BGA games",
)

p.add_layout(
    Slope(
        gradient=slope,
        y_intercept=intercept,
        line_color="black",
        line_width=1.5,
        line_alpha=0.5,
        line_dash="dashed",
    )
)

# Median lines
median_p = bokeh_df["p_deterministic"].median()
median_c = bokeh_df["complexity"].median()

p.add_layout(
    Span(
        dimension="height",
        location=median_p,
        line_color="black",
        line_width=1.5,
        line_alpha=0.25,
        line_dash="dotted",
    )
)

p.add_layout(
    Span(
        dimension="width",
        location=median_c,
        line_color="black",
        line_width=1.5,
        line_alpha=0.25,
        line_dash="dotted",
    )
)

# Quadrant labels
x_min = bokeh_df["p_deterministic"].min()
x_max = bokeh_df["p_deterministic"].max()
y_min = bokeh_df["complexity"].min()
y_max = bokeh_df["complexity"].max()

x_left = 0.5 * (x_min + median_p)
x_right = 0.5 * (median_p + x_max)
y_bottom = y_min * 0.9
y_top = y_max

quadrant_labels = [
    (x_left, y_top, "complex but swingy"),
    (x_right, y_top, "complex and skillful"),
    (x_left, y_bottom, "simple and swingy"),
    (x_right, y_bottom, "simple but skillful"),
]

for x_q, y_q, text in quadrant_labels:
    p.add_layout(
        Label(
            x=x_q,
            y=y_q,
            text=text,
            text_align="center",
            text_baseline="middle",
            text_font_size="12pt",
            text_font_style="bold italic",
            text_alpha=0.25,
        )
    )

# One glyph per game_type with a CDSView so we can control legend order explicitly
for i, gt in enumerate(game_types):
    view = CDSView(filter=GroupFilter(column_name="game_type", group=gt))
    p.scatter(
        x="p_deterministic",
        y="complexity",
        size="size",
        marker="circle",
        source=source,
        view=view,
        fill_alpha=0.75,
        line_color=None,
        color=palette[i % len(palette)],
        legend_label=gt,
    )

p.add_layout(
    LabelSet(
        x="p_deterministic",
        y="complexity",
        text="label",
        x_offset=5,
        y_offset=5,
        text_font_size="9pt",
        text_color="black",
        text_font_style="bold",
        text_alpha=0.25,
        background_fill_color="white",
        background_fill_alpha=0.25,
        source=label_source,
    )
)

hover = HoverTool(
    tooltips=[
        ("Game", "@display_name_en (@year)"),
        ("Effective skill level p", "@p_deterministic{0%}"),
        ("Complexity", "@complexity{0.0}"),
        ("Game type", "@game_type"),
        ("BGG rank (rating)", "@rank (@bayes_rating{0.0})"),
        ("Number of matches", "@num_all_matches"),
        ("Number of players", "@num_regular_players"),
    ]
)
p.add_tools(hover)

p.legend.location = "top_left"
p.legend.click_policy = "hide"
p.xaxis.formatter = NumeralTickFormatter(format="0%")

show(p)


# %%
# Export interactive plot to JSON for embedding
plot_json_path = "../plots/skill_vs_complexity.json"
with open(plot_json_path, "w") as f:
    json.dump(json_item(p, "skill-vs-complexity"), f, indent=4)
print(f"Exported Bokeh plot JSON to {plot_json_path}")


# %%
plot_df.sort("std_dev", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("std_dev", descending=False, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("depth_to_complexity", descending=False, nulls_last=True).head(20)
