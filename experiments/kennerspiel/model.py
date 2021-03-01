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
import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegressionCV
from sklearn.pipeline import make_pipeline
from bg_utils import make_transformer

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

SEED = 23

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
sdj = pd.read_csv("../sdj.csv")
ksdj = pd.read_csv("../ksdj.csv")
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
sdj.shape, ksdj.shape, games.shape

# %%
games["sdj"] = games.index.isin(
    set(
        sdj.bgg_id[
            (sdj.jahrgang > 2011) | ((sdj.jahrgang == 2011) & (sdj.nominated == 1))
        ]
    )
)
games["ksdj"] = games.index.isin(
    set(ksdj.bgg_id)
    | set(sdj.bgg_id[sdj.sonderpreis.isin({"Complex Game", "Game of the Year Plus"})])
)
games.sdj.sum(), games.ksdj.sum()

# %%
data = games[games.sdj | games.ksdj].copy()
data.shape

# %%
features = [
    "min_players",
    "max_players",
    "min_age",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
    "game_type",
    "mechanic",
    "category",
]

# %%
transformer = make_transformer(
    list_columns=("game_type", "mechanic", "category"),
    player_count_columns=("min_players", "max_players"),
    min_df=0.1,
)
imputer = SimpleImputer()
classifier = LogisticRegressionCV(
    class_weight="balanced",
    scoring="f1",
    max_iter=10_000,
)
pipeline = make_pipeline(transformer, imputer, classifier)

# %%
pipeline.fit(data[features], data["ksdj"])

# %%
data["kennerspiel_score"] = pipeline.predict_proba(data[features])[:, 1]

# %%
data.sample(100, random_state=SEED).sort_values("kennerspiel_score", ascending=False)[
    ["name", "year", "ksdj", "kennerspiel_score"]
]

# %%
joblib.dump(pipeline, "model.joblib")
