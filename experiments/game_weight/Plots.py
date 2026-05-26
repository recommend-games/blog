# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Game weight: plots

# %%
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats

jupyter_black.load()
sns.set_style("dark")

# %%
base_dir = Path(".").resolve()
data_dir = base_dir / "data"
plot_dir = base_dir / "plots"
plot_dir.mkdir(parents=True, exist_ok=True)

# %%
pairs = pl.read_csv(data_dir / "reimpl_pairs.csv")
pairs.shape

# %% [markdown]
# ## Distribution of complexity deltas

# %%
delta = pairs["delta"].to_numpy()
mean_delta = delta.mean()

_, ax = plt.subplots(figsize=(7, 4))
sns.histplot(delta, bins=60, kde=True, color="steelblue", ax=ax)
ax.axvline(0, color="white", lw=1.5, ls="--", label="no change")
ax.axvline(mean_delta, color="tomato", lw=2, label=f"mean = {mean_delta:+.3f}")
ax.set_xlabel("Complexity delta (reimplementation − original)")
ax.set_ylabel("Count")
ax.set_title("Are reimplementations rated heavier than their originals?")
ax.legend()
plt.tight_layout()
plt.savefig(plot_dir / "delta_distribution.png", dpi=150)
plt.savefig(plot_dir / "delta_distribution.svg")
plt.show()

# %% [markdown]
# ## Delta vs. year gap

# %%
gap = pairs["year_gap"].to_numpy()
slope, intercept, r, p, _ = stats.linregress(gap, delta)
x_line = np.array([gap.min(), gap.max()])

_, ax = plt.subplots(figsize=(7, 5))
ax.scatter(gap, delta, alpha=0.15, s=12, color="steelblue", rasterized=True)
ax.plot(x_line, slope * x_line + intercept, color="tomato", lw=2,
        label=f"slope = {slope:+.4f}/yr  r = {r:.3f}  p = {p:.3f}")
ax.axhline(0, color="white", lw=1, ls="--")
ax.set_xlabel("Years between original and reimplementation")
ax.set_ylabel("Complexity delta")
ax.set_title("Does the complexity gap grow with time?")
ax.legend()
plt.tight_layout()
plt.savefig(plot_dir / "delta_vs_year_gap.png", dpi=150)
plt.savefig(plot_dir / "delta_vs_year_gap.svg")
plt.show()

# %% [markdown]
# ## Mean delta by year-gap bucket

# %%
buckets = [(1, 5), (6, 10), (11, 20), (21, 50), (51, 200)]
labels, means, cis = [], [], []

for lo, hi in buckets:
    sub = pairs.filter(pl.col("year_gap").is_between(lo, hi))["delta"].to_numpy()
    if len(sub) > 5:
        se = stats.sem(sub)
        labels.append(f"{lo}–{hi}")
        means.append(sub.mean())
        cis.append(1.96 * se)

means_arr = np.array(means)
cis_arr = np.array(cis)

_, ax = plt.subplots(figsize=(7, 4))
colors = ["tomato" if m > 0 else "steelblue" for m in means_arr]
ax.bar(labels, means_arr, color=colors, alpha=0.85, zorder=2)
ax.errorbar(labels, means_arr, yerr=cis_arr, fmt="none", color="white",
            capsize=5, lw=1.5, zorder=3)
ax.axhline(0, color="white", lw=1, ls="--")
ax.set_xlabel("Year gap (original → reimplementation)")
ax.set_ylabel("Mean complexity delta")
ax.set_title("Mean complexity delta by year gap (±95% CI)")
plt.tight_layout()
plt.savefig(plot_dir / "delta_by_year_gap_bucket.png", dpi=150)
plt.savefig(plot_dir / "delta_by_year_gap_bucket.svg")
plt.show()
