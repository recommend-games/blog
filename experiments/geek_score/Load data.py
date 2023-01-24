# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

pd.options.display.max_columns = 150
pd.options.display.max_rows = 150

# %load_ext nb_black
# %load_ext lab_black

# %%
path = (Path(".") / ".." / ".." / ".." / "bgg-ranking-historicals").resolve()
path


# %%
def parse_file(file):
    df = pd.read_csv(file)
    df.drop(columns=["Name", "Year", "URL", "Thumbnail"], inplace=True)
    df.rename(
        columns={
            "ID": "bgg_id",
            "Rank": "rank",
            "Average": "avg_rating",
            "Bayes average": "bayes_rating",
            "Users rated": "num_votes",
        },
        inplace=True,
    )
    df["timestamp"] = datetime.fromisoformat(file.stem).replace(tzinfo=timezone.utc)
    return df


# %%
data = pd.concat(objs=map(parse_file, path.glob("*.csv")), ignore_index=True)
data.sort_values(by=["timestamp", "rank"], ascending=True, inplace=True)
data.set_index(keys=["timestamp", "bgg_id"], inplace=True)
data.shape

# %%
data.sample(10, random_state=23)

# %%
bgg_id = 13  # Catan
data_game = data.xs(bgg_id, level=1)
data_game.shape

# %%
data_game["num_votes"].plot()

# %%
data_game["avg_rating"].plot()

# %%
data_game["bayes_rating"].plot()
