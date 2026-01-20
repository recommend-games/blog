# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from urllib.parse import quote
from board_game_recommender.trust import user_trust

# %load_ext nb_black
# %load_ext lab_black

# %%
trust = user_trust(
    ratings="../../../board-game-data/scraped/bgg_RatingItem.jl",
    min_ratings=10,
)
trust.shape

# %%
trust = trust.sort("trust", ascending=False)

# %%
trust["User"] = trust["bgg_user_name"].apply(
    lambda u: f"[{u.title()}](https://boardgamegeek.com/user/{quote(u)})"
)
trust["Rank"] = range(len(trust))
trust["Rank"] += 1
trust["Trust"] = trust["trust"].apply("{:.3f}".format)

# %%
trust.print_rows(100)

# %%
celebrities = [
    "w eric martin",
    "tomvasel",
    "jonpurkis",
    "quinns",
    "markus shepherd",
    "bohnanzar",
    "aldie",
    "bruno des montagnes",
    "cephalofair",
    "donaldx",
    "elizharg",
    "engelstein",
    "eric lang",
    "faidutti",
    "frog1",
    "jameystegmaier",
    "matthiasmai",
    "mleacock",
    "nopunincluded",
    "phelddagrif",
    "robdaviau",
    "toinito",
    "vlaada",
]
len(celebrities)

# %%
trust[trust["bgg_user_name"].is_in(celebrities)]["User", "Rank", "Trust"].print_rows(
    num_rows=len(celebrities),
    max_column_width=100,
    max_row_width=1000,
)
