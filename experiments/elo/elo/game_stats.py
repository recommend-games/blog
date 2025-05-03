from __future__ import annotations

import itertools
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx
import polars as pl


if TYPE_CHECKING:
    from typing import Generator, Any

LOGGER = logging.getLogger(__name__)


def game_stats(
    matches_path: Path | str,
    *,
    threshold_matches_regulars: int = 25,
    progress_bar: bool = False,
) -> dict[str, int]:
    matches_path = Path(matches_path).resolve()
    LOGGER.info("Reading matches from %s", matches_path)

    data = pl.read_ipc(matches_path, memory_map=False)
    num_all_matches = len(data)

    graph = nx.Graph()

    player_ids_col = data["player_ids"]
    if progress_bar:
        from tqdm import tqdm

        player_ids_col = tqdm(player_ids_col)

    for player_ids in player_ids_col:
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


def _games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    threshold_matches_regulars: int = 25,
    progress_bar: bool = False,
) -> Generator[dict[str, Any]]:
    games_path = Path(games_path).resolve()
    matches_dir = Path(matches_dir).resolve()

    LOGGER.info("Reading games from %s", games_path)
    LOGGER.info("Reading matches from %s", matches_dir)

    games = pl.read_ndjson(games_path)
    games_dicts = games.to_dicts()

    for game in games_dicts:
        LOGGER.info("Processing game %s", game["display_name_en"])
        game_id = game["id"]
        matches_path = matches_dir / f"{game_id}.arrow"
        if not matches_path.exists():
            LOGGER.warning("Matches file %s does not exist", matches_path)
            yield game
            continue

        stats = game_stats(
            matches_path,
            threshold_matches_regulars=threshold_matches_regulars,
            progress_bar=progress_bar,
        )
        yield game | stats

    LOGGER.info("Done.")


def games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    output_path: Path | str,
    threshold_matches_regulars: int = 25,
    progress_bar: bool = False,
):
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Writing games stats to %s", output_path)

    with output_path.open("w") as file:
        for game in _games_stats(
            games_path=games_path,
            matches_dir=matches_dir,
            threshold_matches_regulars=threshold_matches_regulars,
            progress_bar=progress_bar,
        ):
            file.write(json.dumps(game) + "\n")


def _main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    games_stats(
        games_path="games.jl",
        matches_dir="results/arrow/matches",
        output_path="games_stats.jl",
        threshold_matches_regulars=25,
        progress_bar=True,
    )


if __name__ == "__main__":
    _main()
