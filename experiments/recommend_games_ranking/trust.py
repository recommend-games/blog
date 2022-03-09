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
trust["rank"] = range(len(trust))
trust["rank"] += 1

# %%
trust.print_rows(1000)

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
trust[trust["bgg_user_name"].is_in(celebrities)].print_rows(len(celebrities))
