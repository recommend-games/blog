# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import date
from tqdm import trange
import jupyter_black
import polars as pl
import requests

jupyter_black.load()

# %%
exclude = (
    pl.scan_csv("./exclude.csv").select(pl.col("bgg_id").unique()).collect()["bgg_id"]
)
len(exclude)


# %%
def fetch_alt_winners(
    first_year=1979,
    last_year=date.today().year - 1,
    base_url: str = "https://recommend.games/api/games/recommend/",
    exclude=None,
    verbose: bool = False,
):
    exclude = list(exclude) if exclude is not None else []
    base_params = {
        "exclude_clusters": True,
        "exclude_known": True,
        "user": "S_d_J",
        "exclude": list(exclude),
    }
    for year in trange(first_year, last_year + 1):
        for kennerspiel in (False, True):
            params = base_params | {
                "year__gte": year,
                "year__lte": year,
                f"kennerspiel_score__{'gte' if kennerspiel else 'lt'}": 0.5,
            }
            response = requests.get(base_url, params)
            response.raise_for_status()
            alt_winner = response.json()["results"][0]
            if verbose:
                print(
                    f"Alternative {'Kennerspiel' if kennerspiel else 'Spiel'} des Jahres {year}: "
                    f"{alt_winner['name']} ({alt_winner['bgg_id']})"
                )
            yield {
                "bgg_id": alt_winner["bgg_id"],
                "name": alt_winner["name"],
                "award": "ksdj" if kennerspiel else "sdj",
                "jahrgang": year,
            }


# %%
df = pl.DataFrame(fetch_alt_winners())
df.shape

# %%
df.head(10)

# %%
df.write_csv("./alt_candidates.csv")
