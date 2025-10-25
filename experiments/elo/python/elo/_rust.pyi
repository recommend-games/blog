import numpy as np
import numpy.typing as npt

def approx_optimal_k_two_player_rust(
    *,
    matches: npt.NDArray[np.int32],
    min_k: np.float64 | float,
    max_k: np.float64 | float,
    elo_scale: np.float64 | float,
    max_iterations: int | None = None,
    x_absolute_tol: np.float64 | float | None = None,
) -> np.float64: ...
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
