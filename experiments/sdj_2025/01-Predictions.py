# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
from spiel_des_jahres.predictions import sdj_predictions

jupyter_black.load()

pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_rows(100)

# %%
predictions = sdj_predictions(
    year=2025,
    main_user_weights={"rec_standard": 14.0},
    jury_member_weights={"rec_standard": 1.0},
    fetch_from_api=False,
    games_path="../../../board-game-data/scraped/bgg_GameItem.csv",
    kennerspiel_model="kennerspiel.joblib",
    recommender_model="../../../recommend-games-server/data/recommender_light.npz",
).collect()
predictions.shape

# %%
predictions.remove(pl.col("kennerspiel")).head(100)

# %%
predictions.filter(pl.col("kennerspiel")).head(100)

# %%
predictions.write_csv("predictions.csv", float_precision=5)
