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
import seaborn as sns
from elo.optimal_k import approximate_optimal_k
from elo.p_deterministic import simulate_p_deterministic_games, update_elo_ratings_p_deterministic

jupyter_black.load()


# %%
def generate_distributions(
    num_players=1000,
    num_games=1_000_000,
    p_deterministic_min=0.01,
    p_deterministic_max=0.99,
    num_steps=99,
    elo_scale=400,
    seed=None,
    progress_bar: bool = False,
):
    rng = np.random.default_rng(seed)

    p_deterministics = np.linspace(
        start=p_deterministic_min,
        stop=p_deterministic_max,
        num=num_steps,
    )

    if progress_bar:
        from tqdm import tqdm

        p_deterministics = tqdm(p_deterministics)

    for p_deterministic in p_deterministics:
        player_1_ids, player_2_ids, player_1_outcomes = simulate_p_deterministic_games(
            rng=rng,
            num_players=num_players,
            num_games=num_games,
            p_deterministic=p_deterministic,
        )

        elo_k = approximate_optimal_k(
            player_1_ids=player_1_ids,
            player_2_ids=player_2_ids,
            player_1_outcomes=player_1_outcomes,
            min_elo_k=0,
            max_elo_k=elo_scale / 2,
            elo_scale=elo_scale,
        )

        elo_ratings = update_elo_ratings_p_deterministic(
            rng=rng,
            elo_ratings=np.zeros(num_players),
            num_games=num_games,
            p_deterministic=p_deterministic,
            elo_k=elo_k,
            elo_scale=elo_scale,
            inplace=True,
            progress_bar=False,
        )

        yield p_deterministic, elo_k, elo_ratings


# %%
p_deterministics, elo_ks, elo_ratingss = zip(
    *generate_distributions(seed=13, progress_bar=True)
)

# %%
elo_ratingss_array = np.array(elo_ratingss)
elo_ratingss_array.shape, elo_ratingss_array.dtype

# %%
elo_ratings_stds = np.std(elo_ratingss_array, axis=1)
elo_ratings_stds.shape, elo_ratings_stds.dtype

# %%
results = pl.DataFrame(
    data=elo_ratingss_array,
    schema=[f"elo_{i:03d}" for i in range(elo_ratingss_array.shape[1])],
).select(
    pl.Series("p_deterministic", p_deterministics),
    pl.Series("elo_k", elo_ks),
    pl.Series("elo_ratings_std", elo_ratings_stds),
    pl.all(),
)
results.shape

# %%
results.write_csv("results/p_deterministic.csv", float_precision=5)

# %%
sns.scatterplot(data=results, x="p_deterministic", y="elo_k")

# %%
sns.scatterplot(data=results, x="p_deterministic", y="elo_ratings_std")
