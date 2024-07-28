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
from datetime import date
import jupyter_black
import polars as pl

jupyter_black.load()

pl.Config.set_tbl_rows(100)

# %%
games = pl.scan_csv("../../../board-game-data/scraped/bgg_GameItem.csv").select(
    "bgg_id",
    "name",
    "bayes_rating",
)

# %%
exclude = {203416, 203417}
len(exclude)

# %%
sdj = (
    pl.scan_csv("../../spiel-des-jahres/data/sdj.csv")
    .filter(pl.col("jahrgang") < date.today().year)
    .filter(pl.col("winner") == 1)
    .filter(~pl.col("bgg_id").is_in(exclude))
    .select("bgg_id", "jahrgang")
    .with_columns(award=pl.lit("sdj"))
)
ksdj = (
    pl.scan_csv("../../spiel-des-jahres/data/ksdj.csv")
    .filter(pl.col("jahrgang") < date.today().year)
    .filter(pl.col("winner") == 1)
    .filter(~pl.col("bgg_id").is_in(exclude))
    .select("bgg_id", "jahrgang")
    .with_columns(award=pl.lit("ksdj"))
)
ksdj = pl.concat(
    [
        sdj.filter(pl.col("jahrgang") < 2011).with_columns(award=pl.lit("ksdj")),
        ksdj,
    ]
)
winners = pl.concat([sdj, ksdj]).join(games, on="bgg_id", how="inner")

# %%
candidates = (
    pl.scan_csv("./alt_candidates.csv")
    .select("bgg_id", "jahrgang", "award")
    .join(games, on="bgg_id", how="inner")
)

# %%
data = (
    winners.join(candidates, on=["jahrgang", "award"], how="inner", suffix="_alt")
    .with_columns(alt_winner=pl.col("bayes_rating") < pl.col("bayes_rating_alt"))
    .sort("jahrgang", "award", descending=[False, True])
    .collect()
)
data.shape

# %%
data.head(10)

# %%
data.select(pl.col("alt_winner").sum())

# %%
data.filter(pl.col("alt_winner"))
