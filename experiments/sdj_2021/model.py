# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegressionCV
from bg_utils import transform

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
games.shape

# %%
sdj = pd.read_csv(
    "../sdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
sdj["award"] = "sdj"
ksdj = pd.read_csv(
    "../ksdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
ksdj["award"] = "ksdj"
awards = pd.concat((sdj, ksdj))
awards.drop_duplicates("bgg_id", inplace=True)
awards.set_index("bgg_id", inplace=True)
awards.shape

# %%
games["award"] = awards["award"]
games["longlist"] = games["award"].notna()
games.longlist.sum(), games.award.value_counts()

# %%
alt_candidates = pd.read_csv("alt_candidates.csv", index_col="bgg_id")
games["kennerspiel_score"] = alt_candidates["kennerspiel_score"]
games["alt_candidate"] = games["kennerspiel_score"].notna()
alt_candidates.shape, games["alt_candidate"].sum()

# %%
games.sample(3).T

# %%
data_all = games[games.longlist ^ games.alt_candidate]
sdj_mask = (data_all.award == "sdj") | (
    data_all.award.isna() & (data_all.kennerspiel_score < 0.5)
)
data_sdj = data_all[sdj_mask]
data_ksdj = data_all[~sdj_mask]
data_all.shape, data_sdj.shape, data_ksdj.shape

# %%
NUM_FEATURES = ("min_age", "min_time", "max_time", "cooperative", "complexity")


def train_model(data, model=None, target="longlist", num_features=NUM_FEATURES):
    model = (
        LogisticRegressionCV(
            class_weight="balanced",
            max_iter=1_000_000,
            scoring="balanced_accuracy",
        )
        if model is None
        else model
    )
    transformed = transform(
        data=data,
        list_columns=("game_type", "category", "mechanic"),
        min_df=0.01,
    )

    features = list(num_features) + [
        col
        for col in transformed.columns
        if (":" in col) or col.startswith("playable_")
    ]
    in_data = transformed[features + [target]].dropna()  # TODO impute

    model.fit(in_data[features], in_data[target])

    return model, features


# %%
model_sdj, features_sdj = train_model(data_sdj)
print(f"Using {len(features_sdj)} features in SdJ model")
joblib.dump(model_sdj, "lr_sdj.joblib")
with open("features_sdj.json", "w") as f:
    json.dump(features_sdj, f, indent=4)

# %%
model_ksdj, features_ksdj = train_model(data_ksdj)
print(f"Using {len(features_ksdj)} features in KSdJ model")
joblib.dump(model_ksdj, "lr_ksdj.joblib")
with open("features_ksdj.json", "w") as f:
    json.dump(features_ksdj, f, indent=4)
