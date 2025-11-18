from __future__ import annotations

import itertools
import json
import logging
import os
import time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx
import numpy as np
import polars as pl

from elo._rust import approx_optimal_k_rust, calculate_elo_ratings_rust
from elo.utils import matches_to_arrays

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from concurrent.futures import Future
    from typing import Any


def _remove_isolated_players(data: pl.LazyFrame, log_tag: str = "") -> pl.LazyFrame:
    logging.info("%sRemoving isolated players…", log_tag)

    graph: nx.Graph = nx.Graph()

    player_ids_col = data.select("player_ids").collect().to_series()

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
    log_tag: str = "",
) -> tuple[float, float, bool, dict[np.int64, float]]:
    two_player_only = (
        data.select(two_players=pl.col("num_players") == 2)
        .select(pl.all("two_players"))
        .collect()
        .item()
    )

    matches = _pl_to_matches(data)
    players_array, payoffs_array, row_splits_array, unique_players = matches_to_arrays(
        matches=matches,
    )
    if unique_players is not None:
        player_id_mapping = dict(enumerate(unique_players))
    else:
        unique_players_array = np.unique(players_array)
        player_id_mapping = dict(zip(unique_players_array, unique_players_array))

    if elo_k is None:
        logging.info(
            "%sCalculating approximate optimal k*, this may take a while…",
            log_tag,
        )
        elo_k = approx_optimal_k_rust(
            players=players_array,
            payoffs=payoffs_array,
            row_splits=row_splits_array,
            two_player_only=two_player_only,
            min_elo_k=0.0,
            max_elo_k=elo_scale / 2,
            elo_scale=elo_scale,
            max_iterations=None,
            x_absolute_tol=None,
        )

    logging.info("%sCalculating Elo ratings with k*=%.3f", log_tag, elo_k)
    elo_ratings = calculate_elo_ratings_rust(
        players=players_array,
        payoffs=payoffs_array,
        row_splits=row_splits_array,
        two_player_only=two_player_only,
        elo_initial=0.0,
        elo_k=elo_k,
        elo_scale=elo_scale,
    )
    logging.info("%sElo ratings calculated for %d players", log_tag, len(elo_ratings))

    elo_ratings_dict = {
        player_id_mapping[k]: rating for k, rating in elo_ratings.items()
    }

    return elo_k, elo_scale, two_player_only, elo_ratings_dict


def game_stats(
    matches_path: Path | str,
    *,
    remove_isolated_players: bool = True,
    max_matches: int | None = None,
    threshold_matches_regulars: int = 25,
    log_tag: str | None = None,
) -> dict[str, int]:
    log_tag = f"[{log_tag}] " if log_tag else ""

    matches_path = Path(matches_path).resolve()
    logging.info("%sReading matches from %s", log_tag, matches_path)

    data = (
        pl.scan_ipc(matches_path, memory_map=True)
        .filter(pl.col("payoffs").list.eval(pl.element() >= 0).list.all())
        .filter(pl.col("payoffs").list.eval(pl.element() > 0).list.any())
    )
    num_all_matches, num_all_players = _match_and_player_count(data)
    logging.info(
        "%sLoaded %d matches with %d players",
        log_tag,
        num_all_matches,
        num_all_players,
    )

    if not num_all_matches:
        logging.warning("%sNo matches found in %s", log_tag, matches_path)
        return {
            "num_all_matches": 0,
            "num_connected_matches": 0,
            "num_all_players": 0,
            "num_connected_players": 0,
            "remove_isolated_players": remove_isolated_players,
            "threshold_matches_regulars": threshold_matches_regulars,
        }

    if remove_isolated_players:
        data = _remove_isolated_players(data=data, log_tag=log_tag)
    num_connected_matches, num_connected_players = _match_and_player_count(data)
    logging.info(
        "%sAfter removing isolated players: %d matches with %d players",
        log_tag,
        num_connected_matches,
        num_connected_players,
    )

    if not num_connected_matches:
        logging.warning(
            "%sNo connected matches found in %s after removing isolated players",
            log_tag,
            matches_path,
        )
        return {
            "num_all_matches": num_all_matches,
            "num_connected_matches": 0,
            "num_all_players": num_all_players,
            "num_connected_players": 0,
            "remove_isolated_players": remove_isolated_players,
            "threshold_matches_regulars": threshold_matches_regulars,
        }

    if max_matches is not None and num_connected_matches > max_matches:
        logging.warning(
            "%sToo many matches (%d>%d), skipping Elo calculation.",
            log_tag,
            num_connected_matches,
            max_matches,
        )
        return {
            "num_all_matches": num_all_matches,
            "num_connected_matches": num_connected_matches,
            "num_all_players": num_all_players,
            "num_connected_players": num_connected_players,
            "remove_isolated_players": remove_isolated_players,
            "threshold_matches_regulars": threshold_matches_regulars,
        }

    elo_k, elo_scale, two_player_only, elo_ratings = _elo_distribution(
        data=data,
        log_tag=log_tag,
    )
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
    player_info = matches_per_player.join(elo_df, on="player_id", how="inner")
    # TODO: Save the full Elo ratings per player somewhere?

    result = (
        player_info.filter(pl.col("num_matches") >= threshold_matches_regulars)
        .select(
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
    logging.info(
        "%sGame stats calculated for %d regular players",
        log_tag,
        result["num_regular_players"],
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


def _game_stats(
    *,
    game: dict[str, Any],
    matches_dir: Path,
    remove_isolated_players: bool = True,
    max_matches: int | None = None,
    threshold_matches_regulars: int = 25,
) -> dict[str, Any]:
    game_name = game["display_name_en"]
    game_id = game["id"]
    log_tag = f"{game_name} ({game_id})"
    logging.info("Processing game %s", log_tag)
    matches_path = matches_dir / f"{game_id}.arrow"
    if not matches_path.exists():
        logging.warning("[%s] Matches file %s does not exist", log_tag, matches_path)
        return game

    try:
        stats = game_stats(
            matches_path=matches_path,
            remove_isolated_players=remove_isolated_players,
            threshold_matches_regulars=threshold_matches_regulars,
            max_matches=max_matches,
            log_tag=log_tag,
        )
    except Exception:
        logging.exception("Error processing game %s", log_tag)
        return game
    else:
        return game | stats


def _games_stats(
    *,
    executor: ProcessPoolExecutor,
    games_path: Path | str,
    matches_dir: Path | str,
    remove_isolated_players: bool = True,
    max_matches: int | None = None,
    threshold_matches_regulars: int = 25,
) -> Generator[Future[dict[str, Any]]]:
    games_path = Path(games_path).resolve()
    matches_dir = Path(matches_dir).resolve()

    logging.info("Reading games from %s", games_path)
    logging.info("Reading matches from %s", matches_dir)

    games = pl.read_ndjson(games_path)
    games_dicts = games.to_dicts()
    logging.info("Loaded %d games", len(games_dicts))

    for game in games_dicts:
        fut = executor.submit(
            _game_stats,
            game=game,
            matches_dir=matches_dir,
            remove_isolated_players=remove_isolated_players,
            max_matches=max_matches,
            threshold_matches_regulars=threshold_matches_regulars,
        )
        # Attach identifiers for periodic logging
        setattr(fut, "game_id", game.get("id"))
        setattr(fut, "game_name", game.get("display_name_en"))
        yield fut


def _init_worker(name: str | None = None) -> None:
    log_format = (
        f"%(asctime)s [%(processName)s – {name}] %(levelname)s: %(message)s"
        if name
        else "%(asctime)s [%(processName)s] %(levelname)s: %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
    )


def games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    output_path: Path | str,
    remove_isolated_players: bool = True,
    max_matches: int | None = None,
    threshold_matches_regulars: int = 25,
) -> None:
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(initializer=_init_worker) as executor:
        futures = _games_stats(
            executor=executor,
            games_path=games_path,
            matches_dir=matches_dir,
            remove_isolated_players=remove_isolated_players,
            max_matches=max_matches,
            threshold_matches_regulars=threshold_matches_regulars,
        )
        logging.info("Writing games stats to %s", output_path)

        # Collect all submitted futures so we can monitor periodically.
        pending = set(futures)
        # Record start times only when a future actually begins running.
        started_at: dict[Future, float] = {}
        report_interval = int(os.getenv("PENDING_LOG_INTERVAL_SEC", "60"))
        warn_after = int(os.getenv("PENDING_WARN_AFTER_SEC", "600"))

        with output_path.open("w", buffering=1) as file:
            while pending:
                done, not_done = wait(
                    pending,
                    timeout=report_interval,
                    return_when=FIRST_COMPLETED,
                )

                # Write completed results immediately
                for future in done:
                    try:
                        result = future.result()

                    except Exception:
                        logging.exception(
                            "Worker failed for %s (%s)",
                            getattr(future, "game_name", "?"),
                            getattr(future, "game_id", "?"),
                        )
                        # Write a minimal record so downstream knows this game failed
                        result = {
                            "id": getattr(future, "game_id", None),
                            "display_name_en": getattr(future, "game_name", None),
                            "num_all_matches": None,
                            "num_connected_matches": None,
                            "num_all_players": None,
                            "num_connected_players": None,
                            "remove_isolated_players": remove_isolated_players,
                            "threshold_matches_regulars": threshold_matches_regulars,
                        }

                    result_json = json.dumps(
                        obj=result,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    file.write(f"{result_json}\n")
                    file.flush()
                    os.fsync(file.fileno())

                # Update the pending set
                pending = not_done

                if pending:
                    now = time.monotonic()
                    running = [f for f in pending if f.running() and not f.done()]
                    queued = [f for f in pending if not f.running() and not f.done()]
                    # Stamp start time on first transition to running
                    for f in running:
                        if f not in started_at:
                            started_at[f] = now

                    # Heartbeat shows only actively running tasks
                    names = [getattr(f, "game_name", "?") for f in running[:10]]
                    logging.info(
                        "In progress: %d running, %d queued%s",
                        len(running),
                        len(queued),
                        f" — running (up to 10): {', '.join(names)}" if names else "",
                    )

                    # Warn about long-runners (only for actually running tasks)
                    for f in running:
                        elapsed = now - started_at.get(f, now)
                        if elapsed >= warn_after:
                            logging.warning(
                                "Long-running job: %s (%s) running for %s",
                                getattr(f, "game_name", "?"),
                                getattr(f, "game_id", "?"),
                                timedelta(seconds=int(elapsed)),
                            )

    logging.info("Done.")


def _main():
    _init_worker()
    games_stats(
        games_path="csv/games.jl",
        matches_dir="results/arrow/matches",
        output_path="csv/games_stats.jl",
        remove_isolated_players=True,
        max_matches=None,
        threshold_matches_regulars=25,
    )


if __name__ == "__main__":
    _main()
