from collections import defaultdict
import logging
import math
from pathlib import Path
from typing import Iterable
import numpy as np
import polars as pl
import polars.selectors as cs

LOGGER = logging.getLogger(__name__)


def process_game_data(rankings_data: pl.DataFrame) -> pl.DataFrame:
    rank_columns = rankings_data.select(cs.ends_with("_rank")).columns
    columns_map = {i: col[:-5] for i, col in enumerate(rank_columns)}

    return (
        rankings_data.filter(pl.any_horizontal(cs.ends_with("_rank").is_not_null()))
        .with_columns(cs.ends_with("_rank") / cs.ends_with("_rank").max())
        .fill_null(math.inf)
        .select(
            bgg_id=pl.col("id").cast(pl.Int64),
            name="name",
            num_ratings=pl.col("usersrated").cast(pl.Int64),
            game_type=pl.concat_list(rank_columns).list.arg_min().replace(columns_map),
        )
    )


def load_latent_vectors(path: str | Path, bgg_ids: Iterable[int]) -> np.ndarray:
    path = Path(path).resolve()
    LOGGER.info("Loading latent vectors from <%s>", path)

    with path.open("rb") as f:
        files = np.load(file=f)
        items_labels = files["items_labels"]
        items_factors = files["items_factors"]

    items_indexes = defaultdict(
        lambda: -1,
        zip(items_labels, range(len(items_labels))),
    )
    idxs = np.array([items_indexes[bgg_id] for bgg_id in bgg_ids])
    # TODO: Filter out idx -1
    latent_vectors = items_factors[:, idxs].T
    LOGGER.info("Loaded latent vectors with shape %dx%d", *latent_vectors.shape)

    return latent_vectors
