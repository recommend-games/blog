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
from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib import ticker
from scipy.special import factorial
from scipy.stats import hypergeom, nhypergeom

jupyter_black.load()

# %%
num_cards = 16
num_dark = 4
num_games = 1_000_000
possible_lengths = np.arange(num_dark - 1, num_cards)

random_seed = 13
rng = np.random.default_rng(seed=random_seed)

# %% [markdown]
# ## Simulation

# %%
games = np.zeros((num_games, num_cards), dtype=bool)
games[:, :num_dark] = True
games = rng.permuted(games, axis=1, out=games)

# %%
lengths_simulations = np.sum(np.cumsum(games, axis=1) < num_dark, axis=1)
print(lengths_simulations.mean(), lengths_simulations.std())
unique_lengths, length_counts = np.unique(lengths_simulations, return_counts=True)
actual_lengths = defaultdict(float, zip(unique_lengths, length_counts / num_games))
{num_rounds: actual_lengths[num_rounds] for num_rounds in possible_lengths}

# %%
for num_rounds in possible_lengths:
    num_rounds: actual_lengths[num_rounds]
    print(f"|{num_rounds}|{actual_lengths[num_rounds]:.1%}|")

# %% [markdown]
# ## Hypergeometric distribution

# %%
cum_probs = hypergeom.pmf(
    num_dark,
    num_cards,
    num_dark,
    np.arange(num_dark - 1, num_cards + 1),
)
probs_hgd = cum_probs[1:] - cum_probs[:-1]
dict(zip(possible_lengths, probs_hgd))


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
probs_formula = np.array([probability(num_rounds) for num_rounds in possible_lengths])
dict(zip(possible_lengths, probs_formula))


# %% [markdown]
# ## Exact formula (alt)

# %%
def probability_alt(
    num_rounds: int,
    num_cards: int = num_cards,
    num_dark: int = num_dark,
) -> float:
    if num_rounds < num_dark - 1 or num_rounds >= num_cards:
        return 0.0
    arr = np.arange(num_rounds - 2, num_cards - num_dark + 1)
    prod = (arr / (arr + num_dark)).prod()
    return prod * num_dark / (num_rounds + 1)


# %%
probs_alt_formula = np.array(
    [probability_alt(num_rounds) for num_rounds in possible_lengths]
)
dict(zip(possible_lengths, probs_alt_formula))


# %% [markdown]
# ## Exact formula with factorials

# %%
def probability_factorial(
    num_rounds: int,
    num_cards: int = num_cards,
    num_dark: int = num_dark,
) -> float:
    if num_rounds < num_dark - 1 or num_rounds >= num_cards:
        return 0.0
    return (
        factorial(num_cards - num_dark)
        * factorial(num_rounds)
        * num_dark
        / factorial(num_rounds - 3)
        / factorial(num_cards)
    )


# %%
probs_factorial_formula = np.array(
    [probability_factorial(num_rounds) for num_rounds in possible_lengths]
)
dict(zip(possible_lengths, probs_factorial_formula))

# %% [markdown]
# ## Negative hypergeometric distribution

# %%
probs_nhgd = nhypergeom.pmf(
    possible_lengths - 3,
    num_cards,
    num_cards - num_dark,
    num_dark,
)
dict(zip(possible_lengths, probs_nhgd))

# %% [markdown]
# ## Plot

# %%
sns.barplot(x=possible_lengths, y=probs_formula)
plt.title("High Society")
plt.xlabel("Game length")
plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
plt.savefig("game_lengths.png")
plt.savefig("game_lengths.svg")
plt.show()
