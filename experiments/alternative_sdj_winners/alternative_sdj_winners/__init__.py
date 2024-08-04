import itertools
from datetime import date
from tqdm import trange
from typing import Iterable
import requests


def fetch_alt_candidates(
    *,
    first_year: int = 1979,
    last_year: int = date.today().year - 1,
    base_url: str = "https://recommend.games/api/games/recommend/",
    exclude: Iterable[int] | None = None,
    progress: bool = False,
) -> Iterable[dict[str, str | int]]:
    exclude = frozenset(exclude if exclude is not None else ())
    base_params = {
        "exclude_clusters": True,
        "exclude_known": True,
        "user": "S_d_J",
        "bayes_rating__gte": 1.0,
    }
    years = (
        trange(first_year, last_year + 1)
        if progress
        else range(first_year, last_year + 1)
    )
    for year in years:
        for kennerspiel in (False, True):
            for page in itertools.count(1):
                params = base_params | {
                    "year__gte": year,
                    "year__lte": year,
                    f"kennerspiel_score__{'gte' if kennerspiel else 'lt'}": 0.5,
                    "page": page,
                }
                response = requests.get(base_url, params)
                response.raise_for_status()
                results = (
                    result
                    for result in response.json()["results"]
                    if result["bgg_id"] not in exclude
                )
                alt_winner = next(results, None)
                if alt_winner is not None:
                    break
                if not response.json()["next"]:
                    raise ValueError(
                        f"No alternative {'Kennerspiel' if kennerspiel else 'Spiel'} winner found for {year}"
                    )
            yield {
                "bgg_id": alt_winner["bgg_id"],
                "name": alt_winner["name"],
                "award": "ksdj" if kennerspiel else "sdj",
                "jahrgang": year,
            }
