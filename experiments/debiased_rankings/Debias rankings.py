# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import date
from pathlib import Path

import jupyter_black
import polars as pl

from debiased_rankings.data import load_data
from debiased_rankings.model import debias
from debiased_rankings.plots import save_plot

jupyter_black.load()
pl.Config.set_tbl_rows(100)

this_year = date.today().year

# %%
base_dir = Path(".").resolve()
results_dir = base_dir / "results"
project_dir = base_dir.parent.parent
data_dir = project_dir.parent / "board-game-data"
base_dir, results_dir, project_dir, data_dir

# %%
data = load_data(
    path=data_dir / "scraped" / "bgg_GameItem.jl",
    min_year=1970,
    max_year=this_year,
    max_min_time=360,
)
data.shape

# %%
data.describe()

# %%
data.sample(10, seed=this_year)

# %%
experiments = {
    "age": ("age",),
    "complexity": ("complexity",),
    "min_time": ("min_time",),
    "cooperative": ("cooperative",),
    "game_type": (
        "Abstract Game",
        "Children's Game",
        "Customizable",
        "Family Game",
        "Party Game",
        "Strategy Game",
        "Thematic",
        "War Game",
    ),
    "_all": (
        "age",
        "complexity",
        "min_time",
        "cooperative",
        "Abstract Game",
        "Children's Game",
        "Customizable",
        "Family Game",
        "Party Game",
        "Strategy Game",
        "Thematic",
        "War Game",
    ),
}

# %%
for name, regressor_cols in experiments.items():
    print(f"*** *{name}*;", "columns:", ", ".join(regressor_cols), "***")
    out_dir = results_dir / name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(out_dir)
    model, exp_results = debias(
        data=data,
        target_col="avg_rating",
        regressor_cols=regressor_cols,
    )

    model_path = out_dir / "model.csv"
    with model_path.open("w") as model_file:
        model_file.write(model.summary().tables[1].as_csv())
        model_file.write("\n")

    ranking_path = out_dir / "ranking.csv"
    exp_results.sort("rank_debiased").select(
        "rank_debiased",
        "bgg_id",
        "name",
        "year",
        "rank",
        "avg_rating",
        "avg_rating_debiased",
        "avg_rating_change",
        "avg_rating_bayes_debiased",
        "rank_change",
    ).write_csv(ranking_path, float_precision=3)

# %%
plots = {
    "age": {
        "invert_x": True,
        "plot_kwargs": {"x_jitter": 0.25},
        "x_label": "Age in years",
        "title": "Age vs Rating",
    },
    "complexity": {},
    "min_time": {
        "data": data.filter(pl.col("min_time") <= 180),
        "plot_kwargs": {"x_jitter": 2.5},
        "x_label": "Minimum playing time in minutes",
        "title": "Playing time vs Rating",
    },
    "cooperative": {
        "data": data.select(
            "avg_rating",
            "num_votes",
            pl.col("cooperative").replace_strict({0: "Competitive", 1: "Cooperative"}),
        ),
        "kind": "cat",
        "x_label": "Cooperative/Competitive",
        "swap_axes": True,
    },
    "game_type": {
        "data": data.explode("game_type").filter(~pl.col("game_type").is_null()),
        "kind": "cat",
        "x_label": "Game type",
        "swap_axes": True,
    },
}

# %%
for name, plot_opts in plots.items():
    out_dir = results_dir / name
    out_dir.mkdir(parents=True, exist_ok=True)
    print(out_dir)

    plot_opts.setdefault("data", data)
    plot_opts.setdefault("x_column", name)
    plot_opts.setdefault("y_column", "avg_rating")
    plot_opts.setdefault("x_label", name.capitalize())
    plot_opts.setdefault("y_label", "Rating")
    plot_opts.setdefault("title", f"{plot_opts['x_label']} vs {plot_opts['y_label']}")
    plot_opts.setdefault("kind", "reg")
    plot_opts.setdefault("path", out_dir / "plot")
    plot_opts.setdefault("top_k", 1000)
    plot_opts.setdefault("seed", this_year)
    plot_opts.setdefault("show", True)

    if plot_opts.pop("swap_axes", False):
        plot_opts["x_column"], plot_opts["y_column"] = (
            plot_opts["y_column"],
            plot_opts["x_column"],
        )
        plot_opts["x_label"], plot_opts["y_label"] = (
            plot_opts["y_label"],
            plot_opts["x_label"],
        )

    save_plot(**plot_opts)