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
from matplotlib import pyplot as plt
from pathlib import Path

jupyter_black.load()
sns.set_style("dark")

seed = 13

# %%
data_path = Path("../csv/p_deterministic.csv").resolve()
plot_dir = Path("../plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
data_path, plot_dir

# %%
results = pl.read_csv(data_path)
results.shape

# %%
results.sample(10, seed=seed)

# %%
results.group_by("players_per_match").agg(pl.len()).sort("players_per_match")

# %%
plot_data = results.filter(pl.col("p_deterministic") <= 0.9).select(
    "p_deterministic",
    pl.col("elo_k").alias("k*"),
    pl.col("std_dev").alias("σ"),
    pl.col("players_per_match").cast(pl.String).alias("players per match"),
)
plot_data.shape

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="k*",
    hue="players per match",
)
ax.grid(True)
ax.set_title("p_deterministic vs k*")
plt.tight_layout()
plt.savefig(plot_dir / "p_deterministic_vs_k_star.png")
plt.savefig(plot_dir / "p_deterministic_vs_k_star.svg")
plt.show()

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="σ",
    hue="players per match",
)
ax.grid(True)
ax.set_title("p_deterministic vs σ")
plt.tight_layout()
plt.savefig(plot_dir / "p_deterministic_vs_sigma.png")
plt.savefig(plot_dir / "p_deterministic_vs_sigma.svg")
plt.show()

# %%
plot_data = (
    results.filter(pl.col("p_deterministic") <= 0.9)
    .filter(pl.col("elo_k") > 0)
    .filter(pl.col("std_dev") > 0)
    .select(
        "p_deterministic",
        pl.col("elo_k").log().alias("log(k*)"),
        pl.col("std_dev").log().alias("log(σ)"),
        pl.col("players_per_match").cast(pl.String).alias("players per match"),
    )
)
plot_data.shape

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="log(k*)",
    hue="players per match",
)
ax.grid(True)
ax.set_title("p_deterministic vs log(k*)")
plt.tight_layout()
plt.savefig(plot_dir / "p_deterministic_vs_log_k_star.png")
plt.savefig(plot_dir / "p_deterministic_vs_log_k_star.svg")
plt.show()

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="log(σ)",
    hue="players per match",
)
ax.grid(True)
ax.set_title("p_deterministic vs log(σ)")
plt.tight_layout()
plt.savefig(plot_dir / "p_deterministic_vs_log_sigma.png")
plt.savefig(plot_dir / "p_deterministic_vs_log_sigma.svg")
plt.show()

# %%
plot_data = (
    results.filter(
        pl.col("players_per_match") == 2,
        pl.col("p_deterministic") <= 0.99,
    )
    .with_columns(pl.col("p_deterministic").round(2))
    .group_by("p_deterministic")
    .agg(pl.mean("std_dev").alias("σ"))
    .sort("p_deterministic")
)
plot_data.shape

# %%
_, ax = plt.subplots()
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="σ",
    color="purple",
)
ax.grid(True)
ax.set_title("p_deterministic vs σ")
plt.tight_layout()
plt.savefig(plot_dir / "p_deterministic_vs_sigma_two_players.png")
plt.savefig(plot_dir / "p_deterministic_vs_sigma_two_players.svg")
plt.show()
