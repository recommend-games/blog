from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import polars as pl
from tqdm import tqdm

from elo.data import merge_games
from elo.game_stats import games_stats


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds").replace(":", "-")


def matches_jl_to_ipc(
    *,
    in_dir: Path | str,
    out_dir: Path | str,
    delete: bool = False,
    progress_bar: bool = False,
) -> None:
    schema: dict[str, pl.datatypes.DataType | pl.datatypes.DataTypeClass] = {
        "id": pl.String,
        "timestamp": pl.String,
        "game_id": pl.Int64,
        "players": pl.List(
            pl.Struct(
                {
                    "player_id": pl.Int64,
                    "place": pl.Int64,
                    "score": pl.Float64,
                }
            )
        ),
        "scraped_at": pl.String,
    }

    in_dir = Path(in_dir).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = list(in_dir.glob("matches-*.jl"))
    iterator = tqdm(paths) if progress_bar else paths
    logging.info(
        "Processing %d match JL files from <%s> into Arrow format in <%s>",
        len(paths),
        in_dir,
        out_dir,
    )

    for path in iterator:
        p_key = pl.PartitionByKey(
            base_path=out_dir,
            file_path=lambda ctx: f"{ctx.keys[0].str_value}/{path.stem}.arrow",
            by="game_id",
            include_key=True,
        )

        (
            pl.scan_ndjson(source=path, schema=schema)
            .with_columns(pl.col("id", "timestamp").cast(pl.Int64))
            .with_columns(
                pl.from_epoch("timestamp").dt.convert_time_zone(time_zone="UTC"),
                pl.col("scraped_at").str.to_datetime(time_zone="UTC"),
            )
            .sink_ipc(path=p_key, mkdir=True)
        )

        if delete:
            path.unlink()


def _dedupe_matches_single_game(path: Path, *, delete: bool) -> None:
    files = list(path.glob("*.arrow"))

    if len(files) < 2:
        logging.info("Skipping dedupe for %s; only %d file(s)", path, len(files))
        return

    logging.info("Deduping %d files in %s", len(files), path)

    (
        pl.scan_ipc(files, memory_map=False)
        .group_by("id")
        .agg(pl.all().sort_by("timestamp", "scraped_at").last())
        .sink_ipc(path / f"matches-{_now()}-merged.arrow")
    )

    if not delete:
        return

    for file in files:
        file.unlink()


def dedupe_matches(partitions_dir: Path | str, *, delete: bool = False) -> None:
    partitions_dir = Path(partitions_dir).resolve()
    game_dirs = [d for d in partitions_dir.iterdir() if d.is_dir()]

    logging.info(
        "Deduping matches in %d game dirs in %s",
        len(game_dirs),
        partitions_dir,
    )

    for game_dir in game_dirs:
        _dedupe_matches_single_game(game_dir, delete=delete)


def _merge_matches_single_game(match_dir: Path) -> pl.LazyFrame:
    return (
        pl.scan_ipc(match_dir / "matches-*.arrow")
        .select("id", "players", "timestamp", "scraped_at")
        .group_by("id")
        .agg(pl.all().sort_by("timestamp", "scraped_at").last())
        .sort("timestamp")
        .select(
            num_players=pl.col("players").list.len(),
            player_ids=pl.col("players").list.eval(
                pl.element().struct.field("player_id")
            ),
            places=pl.col("players").list.eval(pl.element().struct.field("place")),
        )
        .filter(
            pl.col("num_players") >= 2,
            pl.col("player_ids").list.eval(pl.element().is_not_null()).list.all(),
            pl.col("player_ids").list.unique().list.len() == pl.col("num_players"),
            pl.col("places")
            .list.eval(
                pl.element().is_not_null() & pl.element().is_between(1, pl.len())
            )
            .list.all(),
        )
        .with_row_index("match_idx")
        .explode("player_ids", "places")
        .rename({"player_ids": "player_id", "places": "place"})
        .sort("match_idx", "place")
        .with_columns(group_size=pl.len().over("match_idx", "place"))
        .with_columns(
            is_group_start=pl.col("place")
            .ne(pl.col("place").shift().over("match_idx"))
            .fill_null(True),
        )
        .with_columns(
            group_start=(
                pl.when(pl.col("is_group_start"))
                .then(pl.col("group_size"))
                .otherwise(0)
                .cum_sum()
                .over("match_idx")
                - pl.col("group_size")
            ),
        )
        .with_columns(
            payoff=(
                2 * pl.col("num_players")
                - 1
                - 2 * pl.col("group_start")
                - pl.col("group_size")
            )
            / 2.0,
        )
        .group_by("match_idx")
        .agg(
            num_players=pl.col("num_players").first(),
            player_ids=pl.col("player_id"),
            places=pl.col("place"),
            payoffs=pl.col("payoff"),
        )
        .drop("match_idx")
        .filter(
            pl.col("payoffs").list.eval(pl.element() >= 0).list.all(),
            pl.col("payoffs").list.eval(pl.element() > 0).list.any(),
            (
                pl.col("payoffs").list.sum()
                - (pl.col("num_players") * (pl.col("num_players") - 1) / 2)
            ).abs()
            <= 1e-6,
        )
    )


def merge_matches(
    partitions_dir: Path | str,
    matches_dir: Path | str,
) -> None:
    partitions_dir = Path(partitions_dir).resolve()
    matches_dir = Path(matches_dir).resolve()
    matches_dir.mkdir(parents=True, exist_ok=True)

    for match_dir in partitions_dir.iterdir():
        if not match_dir.is_dir():
            continue

        match_path = matches_dir / f"{match_dir.name}.arrow"
        logging.info(
            "Merging matches from <%s> into <%s>",
            match_dir,
            match_path,
        )

        matches = _merge_matches_single_game(match_dir)
        matches.sink_ipc(match_path)


def process_games() -> None:
    """
    - Merge game data (all games JL)
    - Process matches JL to arrow
    - Dedupe matches, combine into single file per match (occasionally fails atm)
    - For each game:
        - Remove unconnected players and their matches (optional)
        - Determine if two player only game
        - Number of matches per player (for determining regulars)
        - Calibrate k*
        - Calculate Elo ratings for that k*
        - Compute distribution characteristics for various regular cut-off points (at least 1, 25, 100)
        - Stats to record:
            - All players and matches
            - Connected players and matches
            - Regular players and matches
            - Elo: mean / std dev, p00, p01, p05, p25, p50, p75, p95, p99, p100
            - Other metrics from the paper?
        - Write the results into one CSV file per match
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(processName)s] %(levelname)s: %(message)s",
    )

    input_dir = Path("results").resolve()
    arrow_dir = input_dir / "arrow"
    partition_dir = arrow_dir / "partitions"
    matches_dir = arrow_dir / "matches"
    csv_dir = Path("csv").resolve()

    merge_games(
        games_path=input_dir / "games-*.jl",
        output_path=csv_dir / "games.jl",
        overwrite=True,
        progress_bar=True,
    )

    matches_jl_to_ipc(
        in_dir=input_dir,
        out_dir=partition_dir,
        delete=True,
        progress_bar=True,
    )

    dedupe_matches(
        partitions_dir=partition_dir,
        delete=True,
    )

    merge_matches(
        partitions_dir=partition_dir,
        matches_dir=matches_dir,
    )

    games_stats(
        games_path=csv_dir / "games.jl",
        matches_dir=matches_dir,
        stats_output_dir=csv_dir / "game_stats",
        players_output_dir=csv_dir / "player_stats",
        remove_isolated_players=True,
        max_players=12,
        max_matches=None,
        max_threshold_matches_regulars=100,
    )


if __name__ == "__main__":
    process_games()
