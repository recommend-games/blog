# -*- coding: utf-8 -*-

"""Extract rankings from Git repositories."""

import json
import logging
import os

from itertools import product

import pandas as pd

from pytility import arg_to_iter


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
