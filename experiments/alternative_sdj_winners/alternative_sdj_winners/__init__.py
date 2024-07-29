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
    exclude = list(exclude) if exclude is not None else []
    # TODO: Exclude games from response, not via parameter
    # This avoids accidentally excluding reimplementations
    base_params = {
        "exclude_clusters": True,
        "exclude_known": True,
        "user": "S_d_J",
        "exclude": exclude,
    }
    years = (
        trange(first_year, last_year + 1)
        if progress
        else range(first_year, last_year + 1)
    )
    for year in years:
        for kennerspiel in (False, True):
            params = base_params | {
                "year__gte": year,
                "year__lte": year,
                f"kennerspiel_score__{'gte' if kennerspiel else 'lt'}": 0.5,
            }
            response = requests.get(base_url, params)
            response.raise_for_status()
            alt_winner = response.json()["results"][0]
            yield {
                "bgg_id": alt_winner["bgg_id"],
                "name": alt_winner["name"],
                "award": "ksdj" if kennerspiel else "sdj",
                "jahrgang": year,
            }
