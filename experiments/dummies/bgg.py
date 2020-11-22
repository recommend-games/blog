# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import csv
import logging
import sys

from pathlib import Path

from git import Repo

from utils import dfs_from_repo, process_games

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
