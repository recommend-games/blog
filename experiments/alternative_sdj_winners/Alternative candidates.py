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
from pathlib import Path

jupyter_black.load()

BASE_DIR = Path().resolve()
PROJECT_DIR = BASE_DIR.parent.parent
BASE_DIR, PROJECT_DIR

# %%
exclude_list = pl.scan_csv(BASE_DIR / "exclude.csv")
sdj = pl.scan_csv(PROJECT_DIR / "spiel-des-jahres" / "data" / "*.csv")
exclude = (
    pl.concat([exclude_list.select("bgg_id"), sdj.select("bgg_id")])
    .select(pl.col("bgg_id").unique())
    .collect()["bgg_id"]
)
len(exclude)

# %%
df = pl.DataFrame(
    fetch_alt_candidates(
        exclude=exclude,
        progress=True,
    )
)
df.shape

# %%
df.head(10)

# %%
df.write_csv(BASE_DIR / "alt_candidates.csv")
