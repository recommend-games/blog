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
import json
import logging
import sys

from pathlib import Path

import pandas as pd

from sklearn.preprocessing import MultiLabelBinarizer

from utils import bayes, process_games

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
data_path = Path("../../../board-game-data").resolve()

# %%
# TODO load from JSON
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
df = pd.read_csv(data_path / "scraped" / "bgg_GameItem.csv", index_col="bgg_id")
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
rankings_path = data_path / "rankings" / "bgg"
game_type_suffixes = []
for ranking_dir in rankings_path.glob("bgg_*"):
    game_type = ranking_dir.stem[4:]
    game_type_suffixes.append(game_type)
    latest_ranking_path = max(ranking_dir.glob("*.csv"))
    print(ranking_dir, game_type, latest_ranking_path.stem)
    latest_ranking = pd.read_csv(latest_ranking_path, index_col="bgg_id")
    print(latest_ranking.shape)
    games = games.join(
        other=latest_ranking.rename(columns={"score": "bayes_rating"}),
        how="outer",
        rsuffix=f"_{game_type}",
    )
    print(games.shape)

# %%
process_games(games)

# %%
for game_type in game_type_suffixes:
    print(game_type)
    print(
        json.dumps(
            process_games(
                games[games[f"rank_{game_type}"].notna()],
                bayes_rating=f"bayes_rating_{game_type}",
            ),
            indent=4,
        )
    )
