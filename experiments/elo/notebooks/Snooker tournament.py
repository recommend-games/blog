# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
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
pl.Config.set_tbl_rows(100)

seed = 13
rng = np.random.default_rng(seed)
elo_scale = 400
num_simulations = 10_000_000

# %%
players = pl.read_csv("../csv/snooker/elo_ranking.csv")
players.shape

# %%
players.head(10)

# %%
draw = [
    "Kyren Wilson",
    "Lei Peifan",
    "Jak Jones",
    "Zhao Xintong",
    "Neil Robertson",
    "Chris Wakelin",
    "Mark Allen",
    "Fan Zhengyi",
    "Ronnie O'Sullivan",
    "Ali Carter",
    "Zhang Anda",
    "Pang Junxu",
    "Si Jiahui",
    "David Gilbert",
    "Mark Selby",
    "Ben Woollaston",
    "John Higgins",
    "Joe O'Connor",
    "Xiao Guodong",
    "Matthew Selt",
    "Barry Hawkins",
    "Hossein Vafaei",
    "Mark Williams",
    "Wu Yize",
    "Luca Brecel",
    "Ryan Day",
    "Ding Junhui",
    "Zak Surety",
    "Shaun Murphy",
    "Daniel Wells",
    "Judd Trump",
    "Zhou Yuelong",
]


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
    odds = 1 / prob
    print(f"{prob:6.2%} ({odds:7.2f}): {name}")

# %%
betting_odds = pl.read_csv("../csv/snooker/wsc_odds.csv")
betting_odds.shape

# %%
full_result = (
    pl.DataFrame({"Name": results.keys(), "Wins": results.values()})
    .with_columns(Prob=pl.col("Wins") / num_simulations)
    .drop("Wins")
    .with_columns(Odds=1 / pl.col("Prob"))
    .join(players.select("Name", "Elo"), on="Name", how="left")
    .join(betting_odds.select("Name", "BestOdds"), on="Name", how="left")
    .with_columns(ExpectedWin=pl.col("BestOdds") - pl.col("Odds"))
    .sort("Odds")
    .select(
        pl.col("Name").alias("Player"),
        pl.col("Elo").round(1),
        pl.format("{}%", (pl.col("Prob") * 100).round(2)).alias(
            "Simulation probability"
        ),
        pl.col("Odds").round(2).alias("Simulation odds"),
        pl.col("BestOdds").round(2).alias("Betting odds"),
        pl.col("ExpectedWin").round(2).alias("Difference"),
    )
)
full_result.shape

# %%
full_result

# %%
full_result.write_csv("../csv/snooker/wsc_predictions.csv")
