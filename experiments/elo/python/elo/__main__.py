import polars as pl
import numpy as np
from numpy import typing as npt
import sys
from elo._rust import approx_optimal_k_two_player_rust, calculate_elo_ratings_rust
from elo.elo_ratings import calculate_elo_ratings_python
from elo.optimal_k import approximate_optimal_k


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

    print("Approximate optimal K (Python implementation):")
    with Timer(text="Calculated optimal K (Python) in {:.3f} seconds", logger=print):
        optimal_k = approximate_optimal_k(
            matches=matches,
            two_player_only=True,
            min_elo_k=0,
            max_elo_k=200,
            elo_scale=elo_scale,
            max_iterations=None,
            x_absolute_tol=None,
        )
    print(f"Approximate optimal K (Python): {optimal_k:.3f}")

    print("Approximate optimal K (Rust implementation):")
    with Timer(text="Calculated optimal K (Rust) in {:.3f} seconds", logger=print):
        optimal_k = approx_optimal_k_two_player_rust(
            matches=matches,
            min_k=0,
            max_k=200,
            elo_scale=elo_scale,
            max_iterations=None,
            x_absolute_tol=None,
        )
    print(f"Approximate optimal K (Rust): {optimal_k:.3f}")


if __name__ == "__main__":
    main()
