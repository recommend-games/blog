# -*- coding: utf-8 -*-

"""Extract rankings from Git repositories."""

import json
import logging
import os

from itertools import product

import numpy as np
import pandas as pd

from pytility import arg_to_iter
from scipy.optimize import minimize


LOGGER = logging.getLogger(__name__)


def format_from_path(path):
    """ get file extension """
    try:
        _, ext = os.path.splitext(path)
        return ext.lower()[1:] if ext else None
    except Exception:
        pass
    return None


def _df_from_jl(rows):
    if isinstance(rows, str):
        with open(rows) as file:
            return _df_from_jl(file)

    return pd.DataFrame.from_records(map(json.loads, rows))


def dfs_from_repo(repo, directories, files):
    """Load data from Git repo."""

    LOGGER.info("Loading data from %s...", repo)
    for directory, file in product(arg_to_iter(directories), arg_to_iter(files)):
        path = os.path.join(directory, file)
        LOGGER.info("Looking for all versions of <%s>...", path)
        for commit in repo.iter_commits(paths=path):
            try:
                blob = commit.tree / directory / file
            except Exception:
                LOGGER.exception("Path <%s> not found in commit <%s>...", path, commit)
                continue

            LOGGER.info(
                'Found <%s> from commit <%s>: "%s" (%s)',
                blob,
                commit,
                commit.message.strip(),
                commit.authored_datetime,
            )

            file_format = format_from_path(blob.name)

            try:
                data_frame = (
                    pd.read_csv(blob.data_stream)
                    if file_format == "csv"
                    else _df_from_jl(blob.data_stream.read().splitlines())
                    if file_format in ("jl", "jsonl")
                    else None
                )
            except Exception:
                LOGGER.exception("There are a problem loading <%s>...", blob)
                data_frame = None

            if data_frame is not None and not data_frame.empty:
                yield {
                    "data_frame": data_frame,
                    "commit": commit,
                    "blob": blob,
                    "date": commit.authored_datetime,
                }


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
