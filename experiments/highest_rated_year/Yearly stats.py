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
from matplotlib import pyplot as plt
from pathlib import Path
import matplotlib
import jupyter_black
import polars as pl
import seaborn as sns
import statsmodels.api as sm

jupyter_black.load()
pl.Config.set_tbl_rows(100)
sns.set_style("dark")

# %%
this_year = date.today().year
seed = this_year

# %%
base_dir = Path(".").resolve()
plot_dir = base_dir / "plots"
plot_dir.mkdir(parents=True, exist_ok=True)
project_dir = base_dir.parent.parent
rankings_dir = project_dir.parent / "bgg-ranking-historicals"
data_dir = project_dir.parent / "board-game-data"
base_dir, plot_dir, project_dir, rankings_dir, data_dir

# %% [markdown]
# # Rankings

# %%
file_path = max(rankings_dir.glob("*.csv"))
file_path

# %%
years_from_rankings = (
    pl.scan_csv(file_path)
    .select(
        bgg_id="ID",
        name="Name",
        year="Year",
        avg_rating="Average",
        bayes_rating="Bayes average",
        num_ratings="Users rated",
    )
    .filter(pl.col("year") >= 1900)
    .filter(pl.col("year") < this_year)
    .group_by("year")
    .agg(
        num_games=pl.len(),
        avg_rating=pl.mean("avg_rating"),
        bayes_rating=pl.mean("bayes_rating"),
    )
    .with_columns(rel_num_games=pl.col("num_games") / pl.max("num_games"))
    .sort("year")
    .collect()
)
years_from_rankings.shape

# %%
years_from_rankings.filter(pl.col("year") >= 1990)

# %%
data_from_rankings = years_from_rankings.filter(pl.col("year") >= 1970)
model_from_rankings = sm.OLS(
    data_from_rankings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_rankings["year"].to_numpy()),
)
results_from_rankings = model_from_rankings.fit()
results_from_rankings.summary().tables[1]

# %%
_, ax = plt.subplots(figsize=(6, 4))
sns.regplot(
    data=data_from_rankings,
    x="year",
    y="avg_rating",
    ci=95,
    color="purple",
    scatter_kws={
        "s": data_from_rankings["rel_num_games"]
        * matplotlib.rcParams["lines.markersize"] ** 2
    },
    seed=seed,
    ax=ax,
)
ax.set_title("Yearly average ratings from ranked games")
plt.tight_layout()
plt.savefig(plot_dir / "avg_ratings_from_rankings.png")
plt.savefig(plot_dir / "avg_ratings_from_rankings.svg")
plt.show()

# %% [markdown]
# # Ratings

# %%
games = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl")
    .select("bgg_id", "name", "year")
    .filter(pl.col("year") >= 1900)
    .filter(pl.col("year") < this_year)
)
ratings = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_rating")
    .drop_nulls()
)
years_from_ratings = (
    games.join(ratings, on="bgg_id", how="inner")
    .select(
        "year",
        rating="bgg_user_rating",
    )
    .group_by("year")
    .agg(
        num_ratings=pl.len(),
        avg_rating=pl.mean("rating"),
    )
    .with_columns(rel_num_ratings=pl.col("num_ratings") / pl.max("num_ratings"))
    .sort("year")
    .collect()
)
years_from_ratings.shape

# %%
years_from_ratings.filter(pl.col("year") >= 1990)

# %%
data_from_ratings = years_from_ratings.filter(pl.col("year") >= 1970)
model_from_ratings = sm.OLS(
    data_from_ratings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_ratings["year"].to_numpy()),
)
results_from_ratings = model_from_ratings.fit()
results_from_ratings.summary().tables[1]

# %%
_, ax = plt.subplots(figsize=(6, 4))
sns.regplot(
    data=data_from_ratings,
    x="year",
    y="avg_rating",
    ci=95,
    color="purple",
    scatter_kws={
        "s": data_from_ratings["rel_num_ratings"]
        * matplotlib.rcParams["lines.markersize"] ** 2
    },
    seed=seed,
    ax=ax,
)
ax.set_title("Yearly average ratings")
plt.tight_layout()
plt.savefig(plot_dir / "avg_ratings_from_ratings.png")
plt.savefig(plot_dir / "avg_ratings_from_ratings.svg")
plt.show()
