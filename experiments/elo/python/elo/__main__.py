import polars as pl
import numpy as np
from numpy import typing as npt
import sys
from elo._rust import calculate_elo_ratings_rust
from elo.elo_ratings import calculate_elo_ratings_python


def matches_from_arrow_file(file_path: str) -> npt.NDArray[np.int32]:
    data = (
        pl.scan_ipc(file_path)
        .select(pl.col("player_ids").list.to_struct(upper_bound=2))
        .unnest("player_ids")
        .drop_nulls()
        .collect()
    )
    print(f"Loaded {len(data)} matches from {file_path}")
    return data.to_numpy().astype(np.int32)


def main():
    from codetiming import Timer

    matches = matches_from_arrow_file(sys.argv[1])

    elo_initial = 0.0
    elo_k = 32.0
    elo_scale = 400.0

    print("Elo ratings (Python implementation):")
    with Timer(text="Calculated Elo ratings (Python) in {:.3f} seconds", logger=print):
        elo_ratings = calculate_elo_ratings_python(
            matches=matches,
            elo_initial=elo_initial,
            elo_k=elo_k,
            elo_scale=elo_scale,
            progress_bar=True,
        )
    sorted_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_ratings) > 20:
        sorted_ratings = sorted_ratings[:10] + [(0, 0)] + sorted_ratings[-10:]
    for player, rating in sorted_ratings:
        print(f"Player {player:10d}:\tElo {rating:10.3f}")

    print("Elo ratings (Rust implementation):")
    with Timer(text="Calculated Elo ratings (Rust) in {:.3f} seconds", logger=print):
        elo_ratings = calculate_elo_ratings_rust(
            matches=matches,
            elo_initial=elo_initial,
            elo_k=elo_k,
            elo_scale=elo_scale,
        )
    sorted_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_ratings) > 20:
        sorted_ratings = sorted_ratings[:10] + [(0, 0)] + sorted_ratings[-10:]
    for player, rating in sorted_ratings:
        print(f"Player {player:10d}:\tElo {rating:10.3f}")


if __name__ == "__main__":
    main()
