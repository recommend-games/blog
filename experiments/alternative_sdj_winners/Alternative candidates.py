# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
from alternative_sdj_winners import fetch_alt_candidates

jupyter_black.load()

# %%
exclude = (
    pl.scan_csv("./exclude.csv").select(pl.col("bgg_id").unique()).collect()["bgg_id"]
)
len(exclude)

# %%
df = pl.DataFrame(fetch_alt_candidates(progress=True))
df.shape

# %%
df.head(10)

# %%
df.write_csv("./alt_candidates.csv")
