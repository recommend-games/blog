# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.8.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json

import pandas as pd

from pytility import parse_date

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
def process_ratings(
    lines, keys=("item_id", "bgg_id", "bgg_user_name", "bgg_user_rating", "updated_at")
):
    for line in lines:
        item = json.loads(line)
        if not item or not item.get("bgg_user_rating"):
            continue
        yield {
            k: parse_date(item.get(k)) if k.endswith("_at") else item.get(k)
            for k in keys
        }


# %%
with open(
    "../../../board-game-scraper/feeds/bgg/RatingItem/2020-12-28T07-00-47-merged.jl"
) as file:
    df = pd.DataFrame.from_records(process_ratings(file), index="updated_at")

# %%
df.sample(25)
