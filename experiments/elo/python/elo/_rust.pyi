import numpy as np
import numpy.typing as npt

def approx_optimal_k_rust(
    *,
    players: npt.NDArray[np.int64],
    payoffs: npt.NDArray[np.float64] | None,
    row_splits: npt.NDArray[np.int64],
    two_player_only: bool,
    min_elo_k: np.float64 | float,
    max_elo_k: np.float64 | float,
    elo_scale: np.float64 | float,
    max_iterations: int | None,
    x_absolute_tol: np.float64 | float | None,
) -> np.float64: ...
def calculate_elo_ratings_rust(
    *,
    players: npt.NDArray[np.int64],
    payoffs: npt.NDArray[np.float64] | None,
    row_splits: npt.NDArray[np.int64],
    two_player_only: bool,
    elo_initial: np.float64 | float,
    elo_k: np.float64 | float,
    elo_scale: np.float64 | float,
) -> dict[int, np.float64 | float]: ...
def calculate_elo_ratings_two_players_rust(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: np.float64 | float,
    elo_k: np.float64 | float,
    elo_scale: np.float64 | float,
) -> dict[int, np.float64 | float]: ...
def calculate_elo_ratings_multi_players_rust(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: np.float64 | float,
    elo_k: np.float64 | float,
    elo_scale: np.float64 | float,
) -> dict[int, np.float64 | float]: ...
