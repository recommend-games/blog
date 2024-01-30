# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # High Society

# %%
import jupyter_black
import numpy as np
import seaborn as sns
from scipy.stats import hypergeom

jupyter_black.load()

# %%
num_cards = 16
num_dark = 4
num_games = 1_000_000
random_seed = None
rng = np.random.default_rng(seed=random_seed)

# %% [markdown]
# ## Simulation

# %%
games = np.zeros((num_games, num_cards), dtype=bool)
games[:, :num_dark] = True
games = rng.permuted(games, axis=1, out=games)

# %%
lengths = np.sum(np.cumsum(games, axis=1) < num_dark, axis=1)
print(lengths.mean(), lengths.std())
game_length, game_length_count = np.unique(lengths, return_counts=True)
dict(zip(game_length, game_length_count / num_games))

# %% [markdown]
# ## Hypergeometric distribution

# %%
cum_probs = hypergeom.pmf(
    num_dark,
    num_cards,
    num_dark,
    np.arange(num_dark - 1, num_cards + 1),
)
probs = cum_probs[1:] - cum_probs[:-1]
dict(zip(np.arange(num_dark - 1, num_cards), probs))


# %% [markdown]
# ## Exact formula

# %%
def probability(
    num_rounds: int,
    num_cards: int = num_cards,
    num_dark: int = num_dark,
) -> float:
    if num_rounds < num_dark - 1 or num_rounds >= num_cards:
        return 0.0
    return (
        num_dark
        * np.arange(num_rounds - num_dark + 2, num_rounds + 1).prod()
        / np.arange(num_cards - num_dark + 1, num_cards + 1).prod()
    )


# %%
probs_formula = np.array(
    [probability(num_rounds) for num_rounds in np.arange(num_dark - 1, num_cards)]
)
dict(zip(np.arange(num_dark - 1, num_cards), probs_formula))

# %%
sns.barplot(x=np.arange(num_dark - 1, num_cards), y=probs_formula)
