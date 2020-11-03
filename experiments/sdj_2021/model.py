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
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

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
data = games[games.shortlist | games.alt_candidate].copy()
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
X_train, X_test, y_train, y_test = train_test_split(
    values, data.shortlist, test_size=0.2
)

# %%
lr = LogisticRegressionCV(
    class_weight="balanced", max_iter=100_000, scoring="balanced_accuracy"
)
lr.fit(X_train, y_train)

# %%
y_pred = lr.predict(X_test)

# %%
print(classification_report(y_test, y_pred))
