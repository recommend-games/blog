# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from gini import gini_report
from gini.data import scan_rankings

jupyter_black.load()
sns.set_style("dark")

# %%
plot_dir = (Path(".") / "plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
plot_dir

# %%
rankings_dir = Path("../../../bgg-ranking-historicals").resolve()
latest_file = max(rankings_dir.glob("*.csv"))
latest_file

# %%
df = (
    scan_rankings(
        latest_file,
        additional_columns={"Year": "year"},
    )
    .sort("num_ratings")
    .collect()
)
df.shape

# %%
df.tail(5)

# %%
num_ratings = df["num_ratings"]
num_ratings.shape

# %%
num_games, linear, share, gini_coefficient = gini_report(num_ratings, print_report=True)

# %%
_, ax = plt.subplots(figsize=(6, 4))
sns.lineplot(
    x=range(num_games),
    y=num_ratings,
    color="purple",
    lw=3,
    ax=ax,
)
ax.set_title("Number of ratings")
ax.set_ylabel(None)
ax.set_xticklabels([])
plt.tight_layout()
plt.savefig(plot_dir / "num_ratings.png")
plt.savefig(plot_dir / "num_ratings.svg")
plt.show()

# %%
_, ax = plt.subplots(figsize=(6, 6))
ax.fill_between(x=linear, y1=share, y2=linear, color="thistle")
sns.lineplot(
    x=(0, 1),
    y=(0, 1),
    color="purple",
    lw=1,
    ax=ax,
)
sns.lineplot(
    x=linear,
    y=share,
    color="purple",
    lw=3,
    ax=ax,
)
ax.set_title("Share of ratings & Gini coefficient")
ax.set_ylabel(None)
ax.text(
    x=0.55,
    y=0.45,
    s=f"Gini coefficient: {gini_coefficient:.3f}",
    color="purple",
    fontsize=20,
    ha="center",
    va="center",
    rotation=45,
)
plt.tight_layout()
plt.savefig(plot_dir / "gini_coefficient.png")
plt.savefig(plot_dir / "gini_coefficient.svg")
plt.show()

# %%
year_from = 1990
year_to = 2022
_, ax = plt.subplots(figsize=(6, 4))
sns.histplot(
    df.filter(pl.col("year").is_between(year_from, year_to))["year"],
    bins=year_to - year_from + 1,
    color="purple",
)
ax.set_title("Number of games released")
plt.tight_layout()
plt.savefig(plot_dir / "games_per_year.png")
plt.savefig(plot_dir / "games_per_year.svg")
plt.show()

# %%
for year in range(year_from, year_to + 1):
    print(f"*** Games released in {year} ***")
    gini_report(df.filter(pl.col("year") == year)["num_ratings"], print_report=True)
    print()
