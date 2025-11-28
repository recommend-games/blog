import sys

import polars as pl
import numpy as np
from numpy import typing as npt

from elo._rust import (
    calculate_elo_ratings_multi_players_rust,
    calculate_elo_ratings_two_players_rust,
)
from elo.elo_ratings import (
    calculate_elo_ratings_multi_players_python,
    calculate_elo_ratings_two_players_python,
)
from elo.optimal_k import approximate_optimal_k


def matches_from_arrow_file(
    file_path: str,
    *,
    player_count: int = 2,
) -> npt.NDArray[np.int32]:
    assert file_path.endswith(".arrow"), "Input file must be an Arrow file (.arrow)"
    assert player_count >= 2, "Player count must be at least 2"

    data = (
        pl.scan_ipc(file_path)
        .select(pl.col("player_ids").list.to_struct(upper_bound=player_count))
        .unnest("player_ids")
        .drop_nulls()
        .collect()
    )
    print(f"Loaded {len(data)} matches with {player_count} players from {file_path}")

    return data.to_numpy().astype(np.int32)


def main():
    from codetiming import Timer

    if len(sys.argv) < 2:
        print("Usage: python -m elo __main__.py <matches.arrow>")
        sys.exit(1)

    file_path = sys.argv[1]
    player_count = int(sys.argv[2]) if len(sys.argv) >= 3 else 2

    matches = matches_from_arrow_file(
        file_path=file_path,
        player_count=player_count,
    )

    if len(matches) == 0:
        print("No matches found in the input file.")
        return

    elo_initial = 0.0
    elo_k = 32.0
    elo_scale = 400.0

    if player_count == 2:
        print("Elo ratings (two player Python implementation):")
        with Timer(
            text="Calculated Elo ratings (Python) in {:.3f} seconds", logger=print
        ):
            elo_ratings = calculate_elo_ratings_two_players_python(
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

    print("Elo ratings (multi player Python implementation):")
    with Timer(text="Calculated Elo ratings (Python) in {:.3f} seconds", logger=print):
        elo_ratings = calculate_elo_ratings_multi_players_python(
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

    if player_count == 2:
        print("Elo ratings (two player Rust implementation):")
        with Timer(
            text="Calculated Elo ratings (Rust) in {:.3f} seconds",
            logger=print,
        ):
            elo_ratings = calculate_elo_ratings_two_players_rust(
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

    print("Elo ratings (multi player Rust implementation):")
    with Timer(text="Calculated Elo ratings (Rust) in {:.3f} seconds", logger=print):
        elo_ratings = calculate_elo_ratings_multi_players_rust(
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
            two_player_only=(player_count == 2),
            min_elo_k=0,
            max_elo_k=200,
            elo_scale=elo_scale,
            max_iterations=None,
            x_absolute_tol=None,
            python=True,
        )
    print(f"Approximate optimal K (Python): {optimal_k:.3f}")

    print("Approximate optimal K (Rust implementation):")
    with Timer(text="Calculated optimal K (Rust) in {:.3f} seconds", logger=print):
        optimal_k = approximate_optimal_k(
            matches=matches,
            two_player_only=(player_count == 2),
            min_elo_k=0,
            max_elo_k=200,
            elo_scale=elo_scale,
            max_iterations=None,
            x_absolute_tol=None,
            python=False,
        )
    print(f"Approximate optimal K (Rust): {optimal_k:.3f}")


if __name__ == "__main__":
    main()
