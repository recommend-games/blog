from __future__ import annotations

from datetime import datetime
from itertools import batched
from pathlib import Path

import polars as pl
from tqdm import tqdm

from elo.data import merge_games
from elo.game_stats import games_stats


def games_jl_to_ipc() -> None:
    in_dir = Path("../results").resolve()
    out_dir = in_dir / "arrow"
    match_dir = out_dir / "matches"
    out_dir.mkdir(parents=True, exist_ok=True)
    match_dir.mkdir(parents=True, exist_ok=True)

    file_batch_size = 10
    ts = datetime.now().replace(microsecond=0).isoformat().replace(":", "-")
    suffix = f"{ts}-euler-"

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
    for i, batch in enumerate(
        batched(
            tqdm(in_dir.glob("matches-*.jl")),
            file_batch_size,
        ),
    ):
        df = (
            pl.scan_ndjson(list(batch), schema=schema)
            .with_columns(
                pl.col("id").cast(pl.Int64),
                pl.col("timestamp").cast(pl.Int64),
            )
            .with_columns(
                pl.from_epoch("timestamp").dt.convert_time_zone(time_zone="UTC"),
                pl.col("scraped_at").str.to_datetime(time_zone="UTC"),
            )
        )
        df.sink_ipc(out_dir / f"matches-{suffix}{i:05d}.arrow")


def merge_matches() -> None:
    in_dir = Path("../results").resolve()
    out_dir = in_dir / "arrow"
    match_dir = out_dir / "matches"
    out_dir.mkdir(parents=True, exist_ok=True)
    match_dir.mkdir(parents=True, exist_ok=True)

    exclude_games = frozenset(
        {
            49,  # Yahtzee
            1467,  # Azul
        }
    )

    matches = (
        pl.scan_ipc(out_dir / "matches-*.arrow")
        .select("id", "game_id", "players")
        .filter(~pl.col("game_id").is_in(exclude_games))
    )

    game_ids = matches.select(pl.col("game_id").unique()).collect()["game_id"]

    for game_id in tqdm(game_ids):
        match_data = (
            matches.filter(pl.col("game_id") == game_id)
            .drop("game_id")
            .unique("id", keep="any")
            .select(
                num_players=pl.col("players").list.len(),
                player_ids=pl.col("players").list.eval(
                    pl.element().struct.field("player_id")
                ),
                places=pl.col("players").list.eval(pl.element().struct.field("place")),
            )
            .filter(pl.col("num_players") >= 2)
            .filter(
                pl.col("player_ids").list.eval(pl.element().is_not_null()).list.all()
            )
            .filter(
                pl.col("places")
                .list.eval(pl.element().is_not_null() & (pl.element() >= 1))
                .list.all()
            )
            .with_columns(payoffs=pl.col("places").list.eval(pl.len() - pl.element()))
            .filter(pl.col("payoffs").list.eval(pl.element() >= 0).list.all())
        )
        match_data.sink_ipc(match_dir / f"{game_id}.arrow")


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

    input_dir = Path("results").resolve()
    output_dir = Path("csv").resolve()

    merge_games(
        games_path=input_dir / "games-*.jl",
        output_path=output_dir / "games.jl",
        overwrite=True,
        progress_bar=True,
    )

    games_jl_to_ipc()

    merge_matches()

    games_stats(
        games_path=output_dir / "games.jl",
        matches_dir="results/arrow/matches",
        output_path=output_dir / "games_stats.jl",
        remove_isolated_players=True,
        threshold_matches_regulars=25,
    )
