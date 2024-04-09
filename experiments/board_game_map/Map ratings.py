# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import math
from functools import reduce
from operator import or_

import jupyter_black
import polars as pl
import polars.selectors as cs

jupyter_black.load()

# %%
rankings = pl.read_csv("data/boardgames_ranks.csv")
rankings.shape

# %%
rankings.head()

# %%
columns = rankings.select(cs.ends_with("_rank")).columns
columns_map = {i: col[:-5] for i, col in enumerate(columns)}
columns_map

# %%
game_types = (
    rankings.filter(reduce(or_, (pl.col(col).is_not_null() for col in columns)))
    .with_columns(cs.ends_with("_rank") / cs.ends_with("_rank").max())
    .fill_null(math.inf)
    .select(
        bgg_id="id",
        name="name",
        game_type=pl.concat_list(columns).list.arg_min().map_dict(columns_map),
    )
)
game_types.shape

# %%
game_types.select(pl.col("game_type").value_counts(sort=True))
