# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.8.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv("sdj.csv")  # ksdj.csv
games.sort_values(
    ["jahrgang", "winner", "nominated", "recommended"], ascending=False, inplace=True
)
games.shape

# %%
ratings = {"winner": 10, "sonderpreis": 9, "nominated": 8, "recommended": 7}
ratings

# %%
winners = games.winner == 1
sonderpreis = (
    ~winners & games.sonderpreis.notna() & (games.sonderpreis != "Beautiful Game")
)
nominated = ~winners & ~sonderpreis & (games.nominated == 1)
recommended = ~winners & ~nominated & (games.recommended == 1)

winners.sum(), sonderpreis.sum(), nominated.sum(), recommended.sum()

# %%
for url in games[winners].url.unique():
    print(url)
