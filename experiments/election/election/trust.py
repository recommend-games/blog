"""Calculate the trust into users."""

from __future__ import annotations

import json
import math
from itertools import groupby
from collections.abc import Generator, Iterable
from typing import Any

from scipy.stats import shapiro
from tqdm import tqdm


def _user_trust(
    *,
    ratings: Iterable[float | None],
    dates: Iterable[str | None],
    min_ratings: int,
) -> float:
    ratings = tuple(r for r in ratings if r is not None)
    if (len(ratings) < min_ratings) or all(r == ratings[0] for r in ratings):
        return 0.0

    months = len({d[:7] for d in dates if isinstance(d, str)})
    if months < 2:
        return 0.0

    try:
        score, _ = shapiro(ratings)
    except Exception:
        return 0.0

    return float(score * math.log2(months))


def _users_trust(
    *,
    ratings: str | Iterable[dict[str, Any]],
    min_ratings: int,
    key_col: str,
    ratings_col: str,
    date_col: str,
    progress_bar: bool = False,
) -> Generator[tuple[str, float], None, None]:
    if isinstance(ratings, str):
        with open(ratings, encoding="utf-8") as file:
            yield from _users_trust(
                ratings=map(json.loads, file),
                min_ratings=min_ratings,
                key_col=key_col,
                ratings_col=ratings_col,
                date_col=date_col,
                progress_bar=progress_bar,
            )
            return

    if progress_bar:
        ratings = tqdm(ratings, desc="Processing ratings")

    for key, group in groupby(ratings, key=lambda r: r[key_col]):
        rows = ((row.get(ratings_col), row.get(date_col)) for row in group)
        ratings, dates = zip(*rows)
        yield key, _user_trust(ratings=ratings, min_ratings=min_ratings, dates=dates)


def user_trust(
    ratings: str | Iterable[dict[str, Any]],
    *,
    min_ratings: int = 10,
    key_col: str = "bgg_user_name",
    ratings_col: str = "bgg_user_rating",
    date_col: str = "updated_at",
    progress_bar: bool = False,
) -> dict[str, float]:
    """Calculate the trust in users."""

    trust = _users_trust(
        ratings=ratings,
        min_ratings=min_ratings,
        key_col=key_col,
        ratings_col=ratings_col,
        date_col=date_col,
        progress_bar=progress_bar,
    )

    return dict(trust)
