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
import jupyter_black
import requests

jupyter_black.load()

# %%
base_url = "https://recommend.games/api/games/recommend/"
base_params = {
    "exclude_clusters": True,
    "exclude_known": True,
    "user": "S_d_J",
}
base_url, base_params

# %%
for kennerspiel in (False, True):
    for year in range(1979, 2024):
        params = base_params | {
            "year__gte": year,
            "year__lte": year,
            f"kennerspiel_score__{'gte' if kennerspiel else 'lt'}": 0.5,
        }
        response = requests.get(base_url, params)
        response.raise_for_status()
        alt_winner = response.json()["results"][0]
        print(
            f"Alternative {'Kennerspiel' if kennerspiel else 'Spiel'} des Jahres {year}: "
            f"{alt_winner['name']} ({alt_winner['bgg_id']})"
        )
