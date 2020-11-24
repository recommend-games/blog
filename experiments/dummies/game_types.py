# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import logging
import sys

from pathlib import Path

import pandas as pd

from sklearn.preprocessing import MultiLabelBinarizer

from utils import bayes

LOGGER = logging.getLogger(__name__)
SEED = 23

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
path = Path("../../../board-game-data/scraped/bgg_GameItem.csv").resolve()

# %%
game_types = {
    "4666": "Abstract Game",
    "4665": "Children's Game",
    "4667": "Customizable",
    "5499": "Family Game",
    "5498": "Party Game",
    "5497": "Strategy Game",
    "5496": "Thematic",
    "4664": "War Game",
}

# %%
df = pd.read_csv(path, index_col="bgg_id")
df.shape

# %%
df.sample(5, random_state=SEED)

# %%
mlb = MultiLabelBinarizer()
values = mlb.fit_transform(
    df.game_type.apply(
        lambda x: [str(x)]
        if isinstance(x, float) and pd.notna(x)
        else x.split(",")
        if isinstance(x, str) and x
        else []
    )
)
values.shape

# %%
gt_df = pd.DataFrame(data=values, columns=mlb.classes_, index=df.index)
gt_df.shape

# %%
games = df.join(gt_df[list(game_types)].rename(columns=game_types))
games.shape

# %%
game_type = "Strategy Game"
column_score, column_rank = f"{game_type} bayes", f"{game_type} rank"
data = games[games[game_type] == 1].copy()
print(len(data))
total = data.num_votes.sum()
print(total)
data[column_score] = bayes(
    avg_rating=data.avg_rating,
    num_rating=data.num_votes,
    dummy_value=5.5,
    num_dummy=total / 1_000,
)
data[column_rank] = data[column_score].rank(method="min", ascending=False)
data.sort_values(by=column_rank, inplace=True)
data[["name", column_score, column_rank, "year", "avg_rating", "num_votes"]].head(10)

# %%
rankings_path = Path("../../../board-game-data/rankings/bgg/bgg_strategy/").resolve()
latest_ranking_path = max(rankings_path.glob("*.csv"))
latest_ranking = pd.read_csv(latest_ranking_path, index_col="bgg_id")
latest_ranking.shape

# %%
games.join(
    other=latest_ranking.rename(columns={"score": "bayes_rating"}),
    how="outer",
    rsuffix="_strategy",
)
