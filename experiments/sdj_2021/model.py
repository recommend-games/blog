# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd

from pytility import clear_list
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
from sklearn.linear_model import (
    BayesianRidge,
    ElasticNetCV,
    GammaRegressor,
    Huber,
    LassoLarsCV,
    LogisticRegressionCV,
    RidgeClassifierCV,
)
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import BernoulliRBM, MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
)
games.shape

# %%
nominated = pd.concat(
    (
        pd.read_csv("sdj.csv", index_col="bgg_id"),
        pd.read_csv("ksdj.csv", index_col="bgg_id"),
    )
)
nominated.shape

# %%
games["shortlist"] = games.index.isin(nominated.index)

# %%
games.shortlist

# %%
alt_candidates = pd.read_csv("alt_candidates.csv", index_col="bgg_id")
alt_candidates.shape

# %%
games["alt_candidate"] = games.index.isin(alt_candidates.index)

# %%
data = games[games.shortlist | games.alt_candidate].copy().reset_index()
data.shape

# %%
categories = (
    data.game_type.str.cat(data.category, sep=",", na_rep="")
    .str.cat(data.mechanic, sep=",", na_rep="")
    .apply(lambda x: clear_list(x.split(sep=",")) if isinstance(x, str) else [])
)

# %%
mlb = MultiLabelBinarizer()
values = mlb.fit_transform(categories)
values.shape

# %%
all_data = pd.concat((data, pd.DataFrame(data=values, columns=mlb.classes_)), axis=1)

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
] + list(mlb.classes_)

# %%
in_data = all_data[features + ["shortlist"]].dropna()
X_train, X_test, y_train, y_test = train_test_split(
    in_data[features], in_data.shortlist, test_size=0.2
)
X_train.shape, X_test.shape

# %%
models = (
    QuadraticDiscriminantAnalysis(),
    AdaBoostClassifier(n_estimators=100),
    BaggingClassifier(n_estimators=100),
    GradientBoostingClassifier(n_estimators=100),
    IsolationForest(n_estimators=100),
    RandomForestClassifier(n_estimators=100),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    LogisticRegressionCV(
        class_weight="balanced",
        max_iter=1_000_000,
        scoring="balanced_accuracy",
    ),
)

# %%
for model in models:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(model)
    print(classification_report(y_test, y_pred))
