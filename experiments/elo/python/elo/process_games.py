from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import polars as pl
from tqdm import tqdm

from elo.data import merge_games


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds").replace(":", "-")


def matches_jl_to_ipc(
    *,
    in_dir: Path | str,
    out_dir: Path | str,
    delete_jl: bool = False,
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

        if delete_jl:
            path.unlink()


def merge_matches() -> None:
    in_dir = Path("results").resolve()
    out_dir = in_dir / "arrow"
    match_dir = out_dir / "matches" / "new"
    out_dir.mkdir(parents=True, exist_ok=True)
    match_dir.mkdir(parents=True, exist_ok=True)

    exclude_games = frozenset(
        {
            1,
            10,
            11,
            49,  # Yahtzee
            1467,  # Azul
        }
    )

    (
        pl.scan_ipc(out_dir / "matches-*.arrow")
        .select("id", "game_id", "players", "scraped_at")
        .remove(pl.col("game_id").is_in(exclude_games))
        # Deduplicate per (id, game_id); keep an arbitrary row for each group (streaming-friendly)
        .group_by("id", "game_id")
        .agg(pl.all().first())
        # Derive per-match features
        .select(
            "game_id",
            num_players=pl.col("players").list.len(),
            player_ids=pl.col("players").list.eval(
                pl.element().struct.field("player_id")
            ),
            places=pl.col("players").list.eval(pl.element().struct.field("place")),
        )
        .filter(
            pl.col("num_players") >= 2,
            pl.col("player_ids").list.eval(pl.element().is_not_null()).list.all(),
            pl.col("places")
            .list.eval(pl.element().is_not_null() & (pl.element() >= 1))
            .list.all(),
        )
        .with_columns(payoffs=pl.col("places").list.eval(pl.len() - pl.element()))
        .filter(
            pl.col("payoffs").list.eval(pl.element() >= 0).list.all(),
            pl.col("payoffs").list.eval(pl.element() > 0).list.any(),
        )
        .sink_ipc(
            pl.PartitionByKey(
                base_path=match_dir,
                file_path=lambda ctx: f"{ctx.keys[0].str_value}.arrow",
                by="game_id",
                include_key=False,
            ),
            mkdir=True,
        )
    )


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
    partition_dir = input_dir / "arrow" / "partitions"
    csv_dir = Path("csv").resolve()

    merge_games(
        games_path=input_dir / "games-*.jl",
        output_path=csv_dir / "games.jl",
        overwrite=True,
        progress_bar=True,
    )

    matches_jl_to_ipc(
        in_dir=csv_dir,
        out_dir=partition_dir,
        delete_jl=True,
        progress_bar=True,
    )

    merge_matches()

    # games_stats(
    #     games_path=output_dir / "games.jl",
    #     matches_dir="results/arrow/matches",
    #     output_path=output_dir / "games_stats.jl",
    #     remove_isolated_players=True,
    #     threshold_matches_regulars=25,
    # )


if __name__ == "__main__":
    process_games()
