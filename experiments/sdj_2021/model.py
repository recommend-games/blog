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
import json

import joblib
import pandas as pd

from pytility import arg_to_iter, clear_list, parse_int
from imblearn.ensemble import BalancedRandomForestClassifier, RUSBoostClassifier
from imblearn.metrics import classification_report_imbalanced
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingClassifier,
    GradientBoostingClassifier,
    IsolationForest,
    RandomForestClassifier,
)
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.linear_model import LogisticRegressionCV, RidgeClassifierCV
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
with open("../categories.json") as file:
    categories = json.load(file)
with open("../game_types.json") as file:
    game_types = json.load(file)
with open("../mechanics.json") as file:
    mechanics = json.load(file)

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
def map_id(id_, categories=categories, game_types=game_types, mechanics=mechanics):
    id_ = parse_int(id_)
    if not id_:
        return None
    id_ = str(id_)
    if name := categories.get(id_):
        return f"Category: {name}"
    if name := game_types.get(id_):
        return f"Game type: {name}"
    if name := mechanics.get(id_):
        return f"Mechanic: {name}"
    return id_


def map_ids(ids, categories=categories, game_types=game_types, mechanics=mechanics):
    return list(filter(None, map(map_id, arg_to_iter(ids))))


# %%
concatenated = (
    data.game_type.str.cat(data.category, sep=",", na_rep="")
    .str.cat(data.mechanic, sep=",", na_rep="")
    .apply(lambda x: clear_list(x.split(sep=",")) if isinstance(x, str) else [])
    .apply(map_ids)
)

# %%
mlb = MultiLabelBinarizer()
values = mlb.fit_transform(concatenated)
values.shape

# %%
values_df = pd.DataFrame(data=values, columns=mlb.classes_)
values_df.shape

# %%
threshold = len(values_df) / 100
values_df.drop(columns=values_df.columns[values_df.sum() < threshold], inplace=True)
values_df.shape

# %%
all_data = pd.concat((data, values_df), axis=1)

# %%
features = [
    "min_players",
    "max_players",
    "min_players_rec",
    "max_players_rec",
    "min_players_best",
    "max_players_best",
    "min_age",
    # "min_age_rec",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
] + list(values_df.columns)

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
models = (
    lr,
    rf,
    brf,
    rusb,
    # QuadraticDiscriminantAnalysis(),
    # AdaBoostClassifier(n_estimators=100),
    # BaggingClassifier(n_estimators=100),
    # GradientBoostingClassifier(n_estimators=100),
    # IsolationForest(n_estimators=100),
    # GaussianProcessClassifier(1.0 * RBF(1.0)),
    # RidgeClassifierCV(class_weight="balanced"),
    # BernoulliNB(),
    # GaussianNB(),
    # MultinomialNB(),
    # KNeighborsClassifier(),
    # MLPClassifier(
    #    hidden_layer_sizes=(
    #        200,
    #        200,
    #    ),
    #    max_iter=100_000,
    # ),
    # SVC(),
    # DecisionTreeClassifier(),
    # ExtraTreeClassifier(),
)

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
