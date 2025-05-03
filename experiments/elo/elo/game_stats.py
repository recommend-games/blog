from __future__ import annotations

import itertools
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx
import polars as pl
from tqdm import tqdm

if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger(__name__)


def game_stats(
    matches_path: Path | str,
    threshold_matches_regulars: int = 25,
) -> dict[str, int]:
    matches_path = Path(matches_path).resolve()
    LOGGER.info("Reading matches from %s", matches_path)

    data = pl.read_ipc(matches_path, memory_map=False)
    num_all_matches = len(data)

    graph = nx.Graph()
    for player_ids in tqdm(data["player_ids"]):
        graph.add_edges_from(itertools.combinations(player_ids, 2))
    num_all_players = graph.number_of_nodes()
    largest_community = max(nx.connected_components(graph), key=len)
    num_players = len(largest_community)

    data = data.filter(
        pl.col("player_ids").list.eval(pl.element().is_in(largest_community)).list.any()
    )
    num_matches = len(data)

    result = (
        data.lazy()
        .select(pl.col("player_ids").explode().value_counts())
        .unnest("player_ids")
        .select(
            num_matches_max=pl.col("count").max(),
            num_regular_players=(pl.col("count") >= threshold_matches_regulars).sum(),
        )
        .collect()
        .to_dicts()[0]
    )

    result["num_all_matches"] = num_all_matches
    result["num_matches"] = num_matches
    result["num_all_players"] = num_all_players
    result["num_players"] = num_players

    return result
