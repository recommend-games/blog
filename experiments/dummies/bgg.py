# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import csv
import logging
import os.path
import sys

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from git import Repo
from scipy.optimize import minimize

from utils import dfs_from_repo

LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
def bayes(avg_rating, num_rating, dummy_value, num_dummy):
    return (avg_rating * num_rating + dummy_value * num_dummy) / (
        num_rating + num_dummy
    )


def target_mse(num_dummy, dummy_value, data):
    return np.linalg.norm(
        data.bayes_rating
        - bayes(data.avg_rating, data.num_votes, dummy_value, num_dummy)
    )


def process_games(games, x0=np.array([1000]), dummy_value=5.5):
    result = minimize(
        fun=lambda x: target_mse(
            num_dummy=x[0],
            dummy_value=dummy_value,
            data=games[
                games.bayes_rating.notna()
                & games.avg_rating.notna()
                & games.num_votes.notna()
            ],
        ),
        x0=x0,
        method="Nelder-Mead",
        options={
            "xatol": 1e-12,
            "maxiter": 10_000,
            "maxfev": 10_000,
            "disp": True,
        },
    )

    num_votes_total = games.num_votes.sum()
    avg_rating = (games.avg_rating * games.num_votes).sum() / num_votes_total

    return {
        "num_games": len(games),
        "num_games_ranked": int(games.bayes_rating.notna().sum()),
        "num_votes_total": int(num_votes_total),
        "avg_rating": avg_rating,
        "num_votes_dummy": result.x[0],
        "min_mse": result.fun,
        # "result": result,
    }


# %%
def process_repo(repo, directories, files):
    for data in dfs_from_repo(repo=repo, directories=directories, files=files):
        df = data["data_frame"]
        commit = data["commit"]
        blob = data["blob"]

        try:
            result = process_games(df)
        except Exception:
            LOGGER.exception("Unable to process <%s>", commit)
            continue

        result["commit"] = str(commit)
        result["file_name"] = blob.path
        result["datetime"] = str(commit.authored_datetime)

        yield result


# %%
def process_repos(repos, directories, files):
    for repo in repos:
        LOGGER.info("Processing %s", repo)
        yield from process_repo(repo=repo, directories=directories, files=files)


# %%
repos = (
    Repo("~/Workspace/board-game-data"),
    Repo("~/Recommend.Games/_archived/board-game-data-2020-01"),
    Repo("~/Recommend.Games/_archived/ludoj"),
    Repo("~/Recommend.Games/_archived/ludoj-data-old"),
    Repo("~/Recommend.Games/_archived/ludoj-data-archived"),
    Repo("~/Recommend.Games/_archived/ludoj-scraper-archived"),
)

# %%
rows = process_repos(
    repos=repos,
    directories=("scraped", "results"),
    files=("bgg_GameItem.jl", "bgg_GameItem.csv", "bgg.csv"),
)

# %%
out_file = Path() / "results.csv"
first_row = next(rows)
with out_file.open("w", newline="") as out:
    writer = csv.DictWriter(out, first_row.keys())
    writer.writeheader()
    writer.writerow(first_row)
    writer.writerows(rows)
