# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
import polars as pl
from collections import Counter
from elo.elo_ratings import elo_probability
from tqdm import trange

jupyter_black.load()

seed = 13
rng = np.random.default_rng(seed)
elo_scale = 400
num_simulations = 1_000_000

# %%
players = pl.read_csv("results/snooker/elo_ranking.csv")
players.shape

# %%
players.head(10)

# %%
draw = [
    "Kyren Wilson",
    "",
    "Jak Jones",
    "",
    "Neil Robertson",
    "",
    "Mark Allen",
    "",
    "Ronnie O'Sullivan",
    "",
    "Zhang Anda",
    "",
    "Si Jiahui",
    "",
    "Mark Selby",
    "",
    "John Higgins",
    "",
    "Xiao Guodong",
    "",
    "Barry Hawkins",
    "",
    "Mark Williams",
    "",
    "Luca Brecel",
    "",
    "Ding Junhui",
    "",
    "Shaun Murphy",
    "",
    "Judd Trump",
    "",
]

# %%
seeded_players = frozenset(draw) - {""}
other_players = (
    players.filter(~pl.col("Name").is_in(seeded_players))
    .sort("Elo", descending=True, nulls_last=True)
    .head(32 - len(seeded_players))
)
len(other_players)

# %%
draw[1::2] = other_players["Name"]
draw


# %%
def simulate_match(elo_a, elo_b, scale=elo_scale, rng=rng):
    prob_a = elo_probability(diff=elo_a - elo_b, scale=scale)
    return rng.random() < prob_a


def simulate_tournament(draw, elo_ratings, scale=elo_scale, rng=rng):
    current_round = draw
    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            player_a = current_round[i]
            elo_a = elo_ratings[player_a]
            player_b = current_round[i + 1]
            elo_b = elo_ratings[player_b]
            a_wins = simulate_match(elo_a=elo_a, elo_b=elo_b, scale=scale, rng=rng)
            next_round.append(player_a if a_wins else player_b)
        current_round = next_round
    return current_round[0]  # Winner of the tournament


def full_simulation(
    num_simulations,
    draw,
    elo_ratings,
    scale=elo_scale,
    rng=rng,
    progress_bar=False,
):
    range_ = trange(num_simulations) if progress_bar else range(num_simulations)
    results = Counter()
    for i in range_:
        winner = simulate_tournament(
            draw=draw,
            elo_ratings=elo_ratings,
            scale=scale,
            rng=rng,
        )
        results[winner] += 1
    return results


# %%
results = full_simulation(
    num_simulations=num_simulations,
    draw=draw,
    elo_ratings=dict(zip(players["Name"], players["Elo"])),
    scale=elo_scale,
    rng=rng,
    progress_bar=True,
)

# %%
for name, count in results.most_common():
    prob = count / num_simulations
    print(f"{prob:6.2%}: {name}")
