from __future__ import annotations

import itertools
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from elo._rust import approx_optimal_k_rust, calculate_elo_ratings_rust
from elo.utils import matches_to_arrays
import networkx as nx
import polars as pl



if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Generator, Iterable

LOGGER = logging.getLogger(__name__)


def _remove_isolated_players(
    data: pl.LazyFrame,
    *,
    progress_bar: bool = False,
) -> pl.LazyFrame:
    LOGGER.info("Removing isolated players…")

    graph: nx.Graph = nx.Graph()

    player_ids_col: Iterable[Any] = data.select("player_ids").collect().to_series()
    if progress_bar:
        from tqdm import tqdm

        player_ids_col = tqdm(player_ids_col)

    for player_ids in player_ids_col:
        graph.add_edges_from(itertools.combinations(player_ids, 2))

    largest_community = max(nx.connected_components(graph), key=len)

    return data.filter(
        pl.col("player_ids")
        .list.eval(pl.element().is_in(largest_community))
        .list.any(),
    )


def _match_and_player_count(data: pl.LazyFrame) -> tuple[int, int]:
    stats = (
        data.select(
            num_matches=pl.len(),
            num_players=pl.col("player_ids").explode().n_unique(),
        )
        .collect()
        .to_dicts()[0]
    )
    return stats["num_matches"], stats["num_players"]


def _pl_to_matches(data: pl.LazyFrame) -> Iterable[dict[Any, float]]:
    match_rows = data.select("player_ids", "payoffs").collect().iter_rows(named=True)
    for row in match_rows:
        yield dict(zip(row["player_ids"], row["payoffs"]))


def _elo_distribution(
    data: pl.LazyFrame,
    *,
    elo_k: float | None = None,
    elo_scale: float = 400.0,
) -> tuple[float, float, bool, dict[int, float]]:
    two_player_only = (
        data.select(two_players=pl.col("num_players") == 2)
        .select(pl.all("two_players"))
        .collect()
        .item()
    )

    matches = _pl_to_matches(data)
    players_array, payoffs_array, row_splits_array = matches_to_arrays(matches)

    if elo_k is None:
        LOGGER.info("Calculating approximate optimal k*, this may take a while…")
        elo_k = approx_optimal_k_rust(
            players=players_array,
            payoffs=payoffs_array,
            row_splits=row_splits_array,
            two_player_only=two_player_only,
            min_elo_k=0.0,
            max_elo_k=elo_scale / 2,
            elo_scale=elo_scale,
        )

    LOGGER.info("Calculating Elo ratings with k*=%f", elo_k)

    elo_ratings = calculate_elo_ratings_rust(
        players=players_array,
        payoffs=payoffs_array,
        row_splits=row_splits_array,
        two_player_only=two_player_only,
        elo_initial=0.0,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )

    return elo_k, elo_scale, two_player_only, elo_ratings


def game_stats(
    matches_path: Path | str,
    *,
    remove_isolated_players: bool = True,
    threshold_matches_regulars: int = 25,
    progress_bar: bool = False,
) -> dict[str, int]:
    matches_path = Path(matches_path).resolve()
    LOGGER.info("Reading matches from %s", matches_path)

    data = pl.scan_ipc(matches_path, memory_map=True)
    num_all_matches, num_all_players = _match_and_player_count(data)

    if remove_isolated_players:
        data = _remove_isolated_players(
            data=data,
            progress_bar=progress_bar,
        )
    num_connected_matches, num_connected_players = _match_and_player_count(data)

    elo_k, elo_scale, two_player_only, elo_ratings = _elo_distribution(data=data)
    elo_df = pl.LazyFrame(
        data={
            "player_id": list(elo_ratings.keys()),
            "elo_rating": list(elo_ratings.values()),
        },
    )
    matches_per_player = (
        data.select(pl.col("player_ids").explode().value_counts())
        .unnest("player_ids")
        .select(player_id="player_ids", num_matches="count")
    )
    player_info = (
        matches_per_player.join(elo_df, on="player_id", how="outer")
        .fill_null(0)
        .sort("elo_rating", "num_matches", descending=True)
    )
    # TODO: Save the full Elo ratings per player somewhere?

    result = (
        player_info.filter(pl.col("num_matches") >= threshold_matches_regulars)
        .select(
            num_regular_matches=pl.sum("num_matches"),
            num_regular_players=pl.len(),
            num_max_matches=pl.max("num_matches"),
            mean=pl.mean("elo_rating"),
            std_dev=pl.std("elo_rating"),
            p00=pl.min("elo_rating"),
            p01=pl.quantile("elo_rating", 0.01),
            p05=pl.quantile("elo_rating", 0.05),
            p25=pl.quantile("elo_rating", 0.25),
            p50=pl.median("elo_rating"),
            p75=pl.quantile("elo_rating", 0.75),
            p95=pl.quantile("elo_rating", 0.95),
            p99=pl.quantile("elo_rating", 0.99),
            p100=pl.max("elo_rating"),
        )
        .collect()
        .to_dicts()[0]
    )

    return result | {
        "num_all_matches": num_all_matches,
        "num_connected_matches": num_connected_matches,
        "num_all_players": num_all_players,
        "num_connected_players": num_connected_players,
        "elo_k": elo_k,
        "elo_scale": elo_scale,
        "two_player_only": two_player_only,
        "remove_isolated_players": remove_isolated_players,
        "threshold_matches_regulars": threshold_matches_regulars,
    }


def _games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    remove_isolated_players: bool = True,
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

        try:
            stats = game_stats(
                matches_path=matches_path,
                remove_isolated_players=remove_isolated_players,
                threshold_matches_regulars=threshold_matches_regulars,
                progress_bar=progress_bar,
            )
        except Exception:
            LOGGER.exception("Error processing game %s", game["display_name_en"])
            yield game
        else:
            yield game | stats

    LOGGER.info("Done.")


def games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    output_path: Path | str,
    remove_isolated_players: bool = True,
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
            remove_isolated_players=remove_isolated_players,
            threshold_matches_regulars=threshold_matches_regulars,
            progress_bar=progress_bar,
        ):
            file.write(json.dumps(game) + "\n")


def _main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    games_stats(
        games_path="csv/games.jl",
        matches_dir="results/arrow/matches",
        output_path="csv/games_stats.jl",
        remove_isolated_players=True,
        threshold_matches_regulars=25,
        progress_bar=True,
    )


if __name__ == "__main__":
    _main()
