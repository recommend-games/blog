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
import seaborn as sns
from matplotlib import pyplot as plt
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
num_ratings = (
    scan_rankings(latest_file)
    .select("num_ratings")
    .sort("num_ratings")
    .collect()["num_ratings"]
)
num_ratings.shape

# %%
num_ratings.tail()

# %%
_, ax = plt.subplots(figsize=(6, 6))
sns.lineplot(
    x=range(len(num_ratings)),
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
linear = np.linspace(0, 1, len(num_ratings))
share = num_ratings.cum_sum() / num_ratings.sum()
gini_coefficient = 2 * (linear - share).mean()

ax.fill_between(x=linear, y1=share, y2=linear, color="thistle")
sns.lineplot(
    x=linear,
    y=linear,
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
