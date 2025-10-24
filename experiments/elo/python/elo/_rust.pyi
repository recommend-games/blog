import numpy as np
import numpy.typing as npt

def hello_from_bin() -> str: ...
def calculate_elo_ratings_rust(
    *,
    matches: npt.NDArray[np.int32],
    elo_initial: float,
    elo_k: float,
    elo_scale: float,
) -> dict[int, float]: ...
