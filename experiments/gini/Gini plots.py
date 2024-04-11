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
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt

jupyter_black.load()
sns.set_style("dark")

# %%
plot_dir = (Path(".") / "plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
plot_dir

# %%
gini = pl.read_csv("gini.csv", dtypes={"date": pl.Date})
gini.shape

# %%
gini.head()

# %%
gini.tail()

# %%
_, ax = plt.subplots(figsize=(6, 6))
sns.lineplot(
    x=gini["date"],
    y=gini["gini"],
    color="purple",
    lw=3,
    ax=ax,
)
ax.set_title("Gini coefficient over time")
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()
plt.savefig(plot_dir / "gini_coefficient_over_time.png")
plt.savefig(plot_dir / "gini_coefficient_over_time.svg")
plt.show()
