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
import jupyter_black
import polars as pl
from elo.optimal_k import approximate_optimal_k
from elo.elo_ratings import calculate_elo_ratings

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
nobody_id = 440

data = (
    matches.lazy()
    .filter(~pl.col("Unfinished"))
    .filter(pl.col("Player1ID") > 0)
    .filter(pl.col("Player1ID") != nobody_id)
    .filter(pl.col("Player2ID") > 0)
    .filter(pl.col("Player2ID") != nobody_id)
    .filter(
        (pl.col("WinnerID") == pl.col("Player1ID"))
        | (pl.col("WinnerID") == pl.col("Player2ID"))
    )
    .join(
        events.lazy(),
        left_on="EventID",
        right_on="ID",
        how="left",
        suffix="Event",
    )
    .filter(~pl.col("Team"))
    .filter(pl.col("Discipline") == "snooker")
    .with_columns(
        Date=pl.coalesce(
            "EndDate",
            "StartDate",
            "ScheduledDate",
            "EndDateEvent",
            "StartDateEvent",
        )
    )
    .select(
        "Date",
        "Player1ID",
        "Player2ID",
        "WinnerID",
        Player1Outcome=pl.col("Player1ID") == pl.col("WinnerID"),
    )
    .drop_nulls()
    .sort("Date")
    .collect()
)

data.shape

# %%
elo_k = approximate_optimal_k(
    player_1_ids=data["Player1ID"],
    player_2_ids=data["Player2ID"],
    player_1_outcomes=data["Player1Outcome"],
    min_elo_k=0,
    max_elo_k=200,
    elo_scale=400,
)
elo_k

# %%
elo_ratings = calculate_elo_ratings(
    player_1_ids=data["Player1ID"],
    player_2_ids=data["Player2ID"],
    player_1_outcomes=data["Player1Outcome"],
    elo_k=elo_k,
    elo_scale=400,
    progress_bar=True,
)
len(elo_ratings)

# %%
elo_df = (
    pl.DataFrame({"ID": elo_ratings.keys(), "Elo": elo_ratings.values()})
    .join(players, on="ID", how="left")
    .sort("Elo", descending=True, nulls_last=True)
    .with_columns(
        Name=pl.when(pl.col("SurnameFirst"))
        .then(pl.col("LastName") + " " + pl.col("FirstName"))
        .otherwise(pl.col("FirstName") + " " + pl.col("LastName")),
        Rank=pl.col("Elo").rank(method="min", descending=True),
    )
)
elo_df.shape

# %%
elo_df["Elo"].describe()

# %%
with pl.Config(tbl_rows=100):
    display(elo_df.select("Rank", "Elo", "Name", "ID").head(100))

# %%
with pl.Config(tbl_rows=100):
    display(elo_df.select("Rank", "Elo", "Name", "ID").tail(100))

# %%
elo_df.select("Rank", "Elo", "Name", "ID").write_csv("results/snooker/elo_ranking.csv")
