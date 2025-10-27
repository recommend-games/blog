# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
from pathlib import Path

jupyter_black.load()

# %%
rank_dir = Path("../../../bgg-ranking-historicals").resolve()
old_file = rank_dir / "2020-10-27T00-48-32.csv"
new_file = rank_dir / "2025-10-27T00-37-40.csv"
rank_dir

# %%
cols = ("Rank", "Average", "Bayes average", "Users rated")
suffix = " 5 years ago"

# %%
df_old = pl.scan_csv(old_file).select("ID", *cols)
df_new = pl.scan_csv(new_file).select("ID", "Name", *cols)
df = df_new.join(df_old, on="ID", how="inner", suffix=suffix)
for col in cols:
    df = df.with_columns((pl.col(f"{col}{suffix}") - pl.col(col)).alias(f"{col} diff"))
df = df.collect()
df.shape

# %%
df.head(10)

# %%
top_games = df.filter(pl.col(f"Rank{suffix}") <= 1000)
for col in cols:
    print(f"Sorted by {col} diff asc")
    display(top_games.sort(f"{col} diff", descending=False).head(10))
    print(f"Sorted by {col} diff desc")
    display(top_games.sort(f"{col} diff", descending=True).head(10))
