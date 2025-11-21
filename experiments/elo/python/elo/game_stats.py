from __future__ import annotations

import itertools
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


def game_stats_and_elo_distribution(
    *,
    matches_path: Path | str,
    output_path: Path | str,
    game_name: str | None = None,
    remove_isolated_players: bool = True,
    max_players: int | None = 12,
    max_matches: int | None = None,
    max_threshold_matches_regulars: int = 100,
) -> None:
    matches_path = Path(matches_path).resolve()
    output_path = Path(output_path).resolve()

    game_name = game_name or "?"
    game_id = matches_path.stem
    log_tag = f"[{game_name} ({game_id})] "

    logging.info(
        "%sReading matches from <%s>, writing stats to <%s>",
        log_tag,
        matches_path,
        output_path,
    )

    if not matches_path.exists():
        logging.warning("%sMatches file <%s> does not exist", log_tag, matches_path)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result_lazy = _game_stats_and_elo_distribution(
            matches_path=matches_path,
            remove_isolated_players=remove_isolated_players,
            max_threshold_matches_regulars=max_threshold_matches_regulars,
            max_players=max_players,
            max_matches=max_matches,
            log_tag=log_tag,
        )

    except Exception:
        logging.exception("%sError while processing", log_tag)
        return

    if result_lazy is None:
        logging.warning("%sNo game stats calculated", log_tag)
        return

    result = result_lazy.collect()

    logging.info(
        "%sGame stats calculated for %d thresholds",
        log_tag,
        max_threshold_matches_regulars,
    )

    logging.info("%sWriting game stats to <%s>", log_tag, output_path)
    result.write_csv(
        file=output_path,
        include_header=True,
        float_precision=1,
    )


def _game_stats_and_elo_distribution(
    *,
    matches_path: Path,
    remove_isolated_players: bool,
    max_players: int | None,
    max_matches: int | None,
    max_threshold_matches_regulars: int,
    log_tag: str = "",
) -> pl.LazyFrame | None:
    data = pl.scan_ipc(matches_path, memory_map=True).filter(
        pl.col("payoffs").list.eval(pl.element() >= 0).list.all(),
        pl.col("payoffs").list.eval(pl.element() > 0).list.any(),
    )

    if max_players:
        data = data.filter(pl.col("num_players") <= max_players)

    num_all_matches, num_all_players = _match_and_player_count(data)
    logging.info(
        "%sLoaded %d matches with %d players",
        log_tag,
        num_all_matches,
        num_all_players,
    )

    if not num_all_matches:
        logging.warning("%sNo matches found in %s", log_tag, matches_path)
        return None

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
        return None  # TODO: Write stats so far?

    if max_matches is not None and num_connected_matches > max_matches:
        logging.warning(
            "%sToo many matches (%d>%d), skipping Elo calculation.",
            log_tag,
            num_connected_matches,
            max_matches,
        )
        return None  # TODO: Write stats so far?

    elo_k, elo_scale, two_player_only, elo_ratings = _optimal_k_and_elo_ratings(
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

    return (
        pl.concat(
            _elo_stats_for_regular_players(
                data=player_info,
                threshold_matches_regulars=threshold_matches_regulars,
            )
            for threshold_matches_regulars in range(
                1, max_threshold_matches_regulars + 1
            )
        )
        .with_columns(
            num_all_matches=pl.lit(num_all_matches),
            num_connected_matches=pl.lit(num_connected_matches),
            num_all_players=pl.lit(num_all_players),
            num_connected_players=pl.lit(num_connected_players),
            elo_k=pl.lit(elo_k),
            elo_scale=pl.lit(elo_scale),
            two_player_only=pl.lit(two_player_only),
            remove_isolated_players=pl.lit(remove_isolated_players),
            threshold_matches_regulars=pl.arange(1, max_threshold_matches_regulars + 1),
        )
        .sort("threshold_matches_regulars")
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


def _optimal_k_and_elo_ratings(
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


def _pl_to_matches(data: pl.LazyFrame) -> Iterable[dict[Any, float]]:
    match_rows = data.select("player_ids", "payoffs").collect().iter_rows(named=True)
    for row in match_rows:
        yield dict(zip(row["player_ids"], row["payoffs"]))


def _elo_stats_for_regular_players(
    data: pl.LazyFrame,
    threshold_matches_regulars: int = 25,
) -> pl.LazyFrame:
    return data.filter(pl.col("num_matches") >= threshold_matches_regulars).select(
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


def games_stats(
    *,
    games_path: Path | str,
    matches_dir: Path | str,
    output_dir: Path | str,
    remove_isolated_players: bool = True,
    max_players: int | None = 12,
    max_matches: int | None = None,
    max_threshold_matches_regulars: int = 100,
) -> None:
    games_path = Path(games_path).resolve()
    matches_dir = Path(matches_dir).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Reading games from %s", games_path)
    logging.info("Reading matches from %s", matches_dir)
    logging.info("Writing games stats to %s", output_dir)

    games = dict(
        pl.scan_ndjson(games_path)
        .select("id", "display_name_en")
        .select(pl.all().cast(pl.String))
        .collect()
        .iter_rows()
    )
    logging.info("Loaded %d games", len(games))

    with ProcessPoolExecutor(initializer=_init_worker) as executor:
        futures = _game_stats_futures(
            executor=executor,
            matches_dir=matches_dir,
            output_dir=output_dir,
            games=games,
            remove_isolated_players=remove_isolated_players,
            max_players=max_players,
            max_matches=max_matches,
            max_threshold_matches_regulars=max_threshold_matches_regulars,
        )

        # Collect all submitted futures so we can monitor periodically.
        pending = set(futures)
        # Record start times only when a future actually begins running.
        started_at: dict[Future, float] = {}
        report_interval = int(os.getenv("PENDING_LOG_INTERVAL_SEC", "60"))
        warn_after = int(os.getenv("PENDING_WARN_AFTER_SEC", "600"))

        while pending:
            done, not_done = wait(
                pending,
                timeout=report_interval,
                return_when=FIRST_COMPLETED,
            )

            # Write completed results immediately
            for future in done:
                logging.info(
                    "Completed stats for %s (%s)",
                    getattr(future, "game_name", "?"),
                    getattr(future, "game_id", "?"),
                )

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


def _game_stats_futures(
    executor: ProcessPoolExecutor,
    matches_dir: Path,
    output_dir: Path,
    games: dict[str, str],
    remove_isolated_players: bool,
    max_players: int | None,
    max_matches: int | None,
    max_threshold_matches_regulars: int,
) -> Generator[Future]:
    for matches_path in matches_dir.glob("*.arrow"):
        if not matches_path.is_file():
            continue

        game_id = matches_path.stem
        game_name = games.get(game_id) or "?"
        output_path = output_dir / f"{game_id}.csv"

        future = executor.submit(
            game_stats_and_elo_distribution,
            matches_path=matches_path,
            output_path=output_path,
            game_name=game_name,
            remove_isolated_players=remove_isolated_players,
            max_players=max_players,
            max_matches=max_matches,
            max_threshold_matches_regulars=max_threshold_matches_regulars,
        )

        setattr(future, "game_id", game_id)
        setattr(future, "game_name", game_name)

        yield future


def main():
    _init_worker()
    games_stats(
        games_path="csv/games.jl",
        matches_dir="results/arrow/matches",
        output_dir="csv/game_stats",
        remove_isolated_players=True,
        max_players=12,
        max_matches=None,
        max_threshold_matches_regulars=100,
    )


if __name__ == "__main__":
    main()
