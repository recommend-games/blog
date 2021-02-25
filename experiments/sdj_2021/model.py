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

from imblearn.ensemble import BalancedRandomForestClassifier, RUSBoostClassifier
from imblearn.metrics import classification_report_imbalanced
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from games import transform

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
)
games.shape

# %%
sdj = pd.read_csv(
    "sdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
sdj["award"] = "sdj"
ksdj = pd.read_csv(
    "ksdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
ksdj["award"] = "ksdj"
sdj = pd.concat((sdj, ksdj))
sdj.shape

# %%
sdj.sample(10, random_state=SEED)

# %%
games["shortlist"] = games.index.isin(sdj[sdj.winner | sdj.nominated].bgg_id)
games["longlist"] = games.index.isin(sdj.bgg_id)

# %%
games.shortlist.sum(), games.longlist.sum()

# %%
alt_candidates = pd.read_csv("alt_candidates.csv", index_col="bgg_id")
alt_candidates.shape

# %%
games["alt_candidate"] = games.index.isin(alt_candidates.index)

# %%
data = games[games.longlist | games.alt_candidate].copy().reset_index()
data.shape

# %%
all_data = transform(
    data=data,
    list_columns=("game_type", "category", "mechanic"),
    min_df=0.01,
)
all_data.shape

# %%
all_data.sample(3, random_state=SEED).T[-50:]

# %%
num_features = [
    "min_age",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
]
features = num_features + [
    col for col in all_data.columns if (":" in col) or col.startswith("playable_")
]
len(features)

# %%
in_data = all_data[features + ["longlist"]].dropna()
X_train, X_test, y_train, y_test = train_test_split(
    in_data[features], in_data.longlist, test_size=0.2
)
X_train.shape, X_test.shape

# %%
lr = LogisticRegressionCV(
    class_weight="balanced",
    max_iter=1_000_000,
    scoring="balanced_accuracy",
)
rf = RandomForestClassifier(n_estimators=100)
brf = BalancedRandomForestClassifier(n_estimators=100)
rusb = RUSBoostClassifier(n_estimators=200, algorithm="SAMME.R")
models = (lr, rf, brf, rusb)

# %%
for model in models:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(model)
    print(classification_report(y_test, y_pred))
    print(classification_report_imbalanced(y_test, y_pred))

# %%
sorted(zip(lr.coef_[0, :], features), reverse=True)

# %%
sorted(zip(rf.feature_importances_, features), reverse=True)

# %%
sorted(zip(brf.feature_importances_, features), reverse=True)

# %%
sorted(zip(rusb.feature_importances_, features), reverse=True)

# %%
joblib.dump(lr, "lr.joblib")
