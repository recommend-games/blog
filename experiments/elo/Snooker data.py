# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from collections import defaultdict
from tqdm import tqdm
import jupyter_black
import polars as pl

jupyter_black.load()

seed = 13

# %%
events = (
    pl.scan_ndjson("results/snooker/events*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(
        pl.col("StartDate", "EndDate").str.to_date().cast(pl.Datetime(time_zone="UTC")),
    )
    .collect()
)
matches = (
    pl.scan_ndjson("results/snooker/matches*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(
        pl.col(
            "InitDate",
            "ModDate",
            "ScheduledDate",
            "StartDate",
            "EndDate",
        ).str.to_datetime("%+", strict=False, time_zone="UTC")
    )
    .collect()
)
players = (
    pl.scan_ndjson("results/snooker/players*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(pl.col("Born", "Died").str.to_date(strict=False))
    .collect()
)
events.shape, matches.shape, players.shape

# %%
events.sample(10, seed=seed)

# %%
events.describe()

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %%
players.sample(10, seed=seed)

# %%
players.describe()

# %%
data = (
    matches.lazy()
    .filter(~pl.col("Unfinished"))
    .filter(pl.col("Player1ID") > 0)
    .filter(pl.col("Player2ID") > 0)
    .filter(
        (pl.col("WinnerID") == pl.col("Player1ID"))
        | (pl.col("WinnerID") == pl.col("Player2ID"))
    )
    .with_columns(Date=pl.coalesce("EndDate", "StartDate", "ScheduledDate"))
    .select("Date", "Player1ID", "Player2ID", "WinnerID")
    .drop_nulls()
    .sort("Date")
    .collect()
)
data.shape

# %%
elo_ratings = defaultdict(int)
for _, player_1, player_2, winner in tqdm(data.iter_rows()):
    elo_1 = elo_ratings[player_1]
    elo_2 = elo_ratings[player_2]
    diff = elo_1 - elo_2
    player_1_pred = 1 / (1 + 10 ** (-diff / 400))
    player_1_actual = winner == player_1
    player_1_update = 20 * (player_1_actual - player_1_pred)
    elo_ratings[player_1] += player_1_update
    elo_ratings[player_2] -= player_1_update
len(elo_ratings)

# %%
elo_df = (
    pl.DataFrame({"ID": elo_ratings.keys(), "Elo": elo_ratings.values()})
    .join(players, on="ID", how="full")
    .sort("Elo", descending=True, nulls_last=True)
    .with_columns(pl.col("Elo").rank(method="min", descending=True).alias("Rank"))
)
elo_df.shape

# %%
with pl.Config(tbl_rows=100):
    display(
        elo_df.select(
            "Rank",
            "Elo",
            pl.col("FirstName") + " " + pl.col("LastName"),
            "ID",
        ).head(100)
    )

# %%
with pl.Config(tbl_rows=100):
    display(
        elo_df.select(
            "Rank",
            "Elo",
            pl.col("FirstName") + " " + pl.col("LastName"),
            "ID",
        ).tail(100)
    )
