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
import seaborn as sns
from elo.elo_ratings import TwoPlayerElo
from elo.optimal_k import approximate_optimal_k
from elo.p_deterministic import simulate_p_deterministic_matches
from matplotlib import pyplot as plt
from pathlib import Path
from tqdm import tqdm

jupyter_black.load()
sns.set_style("dark")

seed = 13
rng = np.random.default_rng(seed)

plot_dir = Path("../plots/").resolve()

# %%
elo_scale = 400
num_players = 1000
num_matches = num_players**2
players_per_match = 2
p_deterministic = np.linspace(0.2, 0.8, 7)
p_deterministic


# %%
def elo_ratings(
    *,
    num_players: int,
    num_matches: int,
    players_per_match: int = 2,
    p_deterministic: float,
    elo_scale: float = 400,
    rng: np.random.Generator = np.random.default_rng(),
):
    matches = simulate_p_deterministic_matches(
        rng=rng,
        num_players=num_players,
        num_matches=num_matches,
        players_per_match=players_per_match,
        p_deterministic=p_deterministic,
    )

    elo_k = approximate_optimal_k(
        matches=matches,
        two_player_only=players_per_match == 2,
        min_elo_k=0,
        max_elo_k=elo_scale / 2,
        elo_scale=elo_scale,
    )

    elo = TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
    elo.update_elo_ratings_batch(matches=matches)

    return pl.LazyFrame(
        data={
            "num_players": num_players,
            "num_matches": num_matches,
            "players_per_match": players_per_match,
            "p_deterministic": p_deterministic,
            "elo_scale": elo_scale,
            "player_id": elo.elo_ratings.keys(),
            "elo_rating": elo.elo_ratings.values(),
        },
    )


# %%
data = (
    pl.concat(
        [
            elo_ratings(
                num_players=num_players,
                num_matches=num_matches,
                players_per_match=players_per_match,
                p_deterministic=p,
                elo_scale=elo_scale,
                rng=rng,
            )
            for p in tqdm(p_deterministic)
        ]
    )
    .select(
        pl.col("p_deterministic").round(1).cast(pl.String),
        pl.col("elo_rating").alias("Elo rating"),
    )
    .collect()
)
data.shape

# %%
palette = sns.dark_palette(
    "purple",
    n_colors=data.select(pl.n_unique("p_deterministic")).item(),
    reverse=True,
)
data.shape

# %%
_, ax = plt.subplots()
sns.kdeplot(
    data=data,
    x="Elo rating",
    hue="p_deterministic",
    palette=palette,
    common_norm=False,
    ax=ax,
)
ax.grid(True)
ax.set_title("Elo ratings distributions of p_deterministic games")
plt.tight_layout()
plt.savefig(plot_dir / "elo_distribution_p_deterministic.png")
plt.savefig(plot_dir / "elo_distribution_p_deterministic.svg")
plt.show()
