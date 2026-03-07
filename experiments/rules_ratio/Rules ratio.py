# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import json
import numpy as np
import polars as pl
import statsmodels.api as sm
from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter
from bokeh.palettes import Category10
from bokeh.transform import factor_cmap
from datetime import date
from pathlib import Path

jupyter_black.load()

output_notebook()
pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_rows(100)

seed = 13

# %%
# Filter values
min_votes = 250
min_threads = 25
min_forums = 10
min_year = 1950
max_year = date.today().year
# Additive smoothing
alpha = 0.5
beta = 0.5
# File paths
results_dir = Path("./results").resolve()
data_dir = Path("../../../board-game-data").resolve()
results_dir, data_dir

# %%
forums = (
    pl.scan_ndjson(results_dir / "*.jl")
    .unique("forum_id", keep="any")
    .select("bgg_id", "title", "num_threads")
)
games = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl", infer_schema_length=10_000)
    .remove(pl.col("compilation"))
    .select(
        "bgg_id",
        "name",
        "year",
        "rank",
        "bayes_rating",
        "num_votes",
        "complexity",
        "add_rank",
    )
    .remove(pl.col("rank").is_null())
    .remove(pl.col("num_votes") < min_votes)
    .remove(pl.col("complexity").is_null())
    .filter(pl.col("year").is_between(min_year, max_year))
)
game_types = (
    games.select("bgg_id", "add_rank")
    .explode("add_rank")
    .unnest("add_rank")
    .group_by("bgg_id")
    .agg(
        game_type=pl.col("name")
        .sort_by("rank", "bayes_rating", descending=[False, True], nulls_last=True)
        .first()
    )
)
games = (
    games.drop("add_rank")
    .join(game_types, on="bgg_id", how="left")
    .with_columns(pl.col("game_type").fill_null("Uncategorized"))
)

forums.group_by("title").agg(pl.len()).sort(
    "len",
    "title",
    descending=[True, False],
).collect()

# %%
rules_ratios = (
    forums.group_by("bgg_id")
    .agg(
        num_forums=pl.len(),
        num_threads_rules=pl.when(title="Rules").then("num_threads").otherwise(0).sum(),
        num_threads_total=pl.col("num_threads").sum(),
    )
    .remove(pl.col("num_forums") < min_forums)
    .remove(pl.col("num_threads_total") < min_threads)
    .with_columns(
        rules_ratio=(pl.col("num_threads_rules") + alpha)
        / (pl.col("num_threads_total") + alpha + beta)
    )
    .join(games, on="bgg_id", how="inner")
    .with_columns(rules_ratio_by_weight=pl.col("rules_ratio") / pl.col("complexity"))
    .collect()
)
rules_ratios.shape

# %%
# Fit Binomial GLM using smoothed proportion with frequency weights
y = rules_ratios["rules_ratio"].to_pandas()
X = sm.add_constant(rules_ratios.select("complexity").to_pandas())
w = rules_ratios["num_votes"].to_pandas() + alpha + beta

model = sm.GLM(y, X, family=sm.families.Binomial(), freq_weights=w).fit()
print(model.summary())
rr_hat = model.predict(X)

rules_ratios = (
    rules_ratios.with_columns(rr_hat=pl.Series(rr_hat))
    .with_columns(
        residual_rules_ratio=pl.col("rules_ratio") - pl.col("rr_hat"),
    )
    .sort(
        "rules_ratio",
        "residual_rules_ratio",
        "rules_ratio_by_weight",
        "num_threads_total",
        descending=[True, True, True, False],
    )
)

rules_ratios.shape

# %%
rules_ratios.sample(10, seed=seed)

# %%
rules_ratios.describe()

# %%
rules_ratios.sort("rank", descending=False).head(10)

# %%
rules_ratios.sort("num_votes", descending=True).head(10)

# %%
rules_ratios.sort("rules_ratio", descending=True).head(10)

# %%
rules_ratios.sort("rules_ratio", descending=False).head(10)

# %%
rules_ratios.sort("rules_ratio_by_weight", descending=True).head(10)

# %%
rules_ratios.sort("rules_ratio_by_weight", descending=False).head(10)

# %%
rules_ratios.sort("residual_rules_ratio", descending=True).head(10)

# %%
rules_ratios.sort("residual_rules_ratio", descending=False).head(10)

# %%
# TODO: Export results to CSV

# %%
# Bokeh scatter: complexity vs rules_ratio
min_size, max_size = 5, 18
bokeh_df = (
    rules_ratios.filter((pl.col("rank") <= 1000) | (pl.col("num_votes") >= 10_000))
    .with_columns(log_num_votes=pl.col("num_votes").clip(1).log10())
    .with_columns(
        size=min_size
        + (pl.col("log_num_votes") - pl.col("log_num_votes").min())
        * (max_size - min_size)
        / (pl.col("log_num_votes").max() - pl.col("log_num_votes").min())
    )
    .to_pandas()
)
source = ColumnDataSource(bokeh_df)
game_types_unique = sorted(bokeh_df["game_type"].unique())

p = figure(
    width=900,
    height=550,
    title="Rules ratio vs complexity",
    x_axis_label="BGG complexity",
    y_axis_label="Rules ratio (RR)",
    tools="pan,wheel_zoom,box_zoom,reset,save",
)

p.scatter(
    source=source,
    x="complexity",
    y="rules_ratio",
    size="size",
    marker="circle",
    fill_alpha=0.75,
    line_color=None,
    fill_color=factor_cmap(
        "game_type",
        palette=Category10[10],
        factors=game_types_unique,
    ),
    legend_group="game_type",
)

hover = HoverTool(
    tooltips=[
        ("Game", "@name (@year)"),
        (
            "Rules ratio (RR)",
            "@rules_ratio{0%} (@num_threads_rules / @num_threads_total)",
        ),
        ("Rules ratio by weight (RRW)", "@rules_ratio_by_weight{0%}"),
        ("Residual rules ratio (RRR)", "@residual_rules_ratio{0%}"),
        ("Complexity", "@complexity{0.0}"),
        ("BGG rank (rating)", "@rank (@bayes_rating{0.0})"),
        ("Number of ratings", "@num_votes"),
        ("Game type", "@game_type"),
    ]
)
p.add_tools(hover)

p.legend.location = "bottom_right"
p.yaxis.formatter = NumeralTickFormatter(format="0%")

show(p)

# %%
# Export interactive plot to JSON for embedding
plot_json_path = "plots/rules_ratio_vs_complexity.json"
with open(plot_json_path, "w") as f:
    json.dump(json_item(p, "rules-ratio-vs-complexity"), f, indent=4)
print(f"Exported Bokeh plot JSON to {plot_json_path}")
