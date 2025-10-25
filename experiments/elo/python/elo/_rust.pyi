import numpy as np
import numpy.typing as npt

def approx_optimal_k_two_player_rust(
    *,
    matches: npt.NDArray[np.int32],
    min_k: float,
    max_k: float,
    elo_scale: float,
    max_iterations: int | None = None,
    x_absolute_tol: float | None = None,
) -> float: ...
def calculate_elo_ratings_two_players_rust(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: float,
    elo_k: float,
    elo_scale: float,
) -> dict[int, float]: ...
