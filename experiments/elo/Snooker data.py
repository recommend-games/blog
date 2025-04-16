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
import numpy as np
import polars as pl
import seaborn as sns
from datetime import timedelta
from elo.optimal_k import approximate_optimal_k
from elo.elo_ratings import calculate_elo_ratings
from matplotlib import pyplot as plt
from tqdm import tqdm

jupyter_black.load()
pl.Config.set_tbl_rows(100)

seed = 13
elo_scale = 400

# %% [markdown]
# # General EDA

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
        pl.col("InitDate", "ModDate", "StartDate", "EndDate").str.to_datetime(
            "%+",
            strict=False,
            time_zone="UTC",
        ),
        pl.coalesce(
            pl.col("ScheduledDate").str.to_datetime(
                "%+",
                strict=False,
                ambiguous="null",
                time_zone="UTC",
            ),
            pl.col("ScheduledDate").str.to_datetime(
                "%Y-%m-%d",
                strict=False,
                ambiguous="null",
                time_zone="UTC",
            ),
        ),
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

# %% [markdown]
# ## Events

# %%
events.sample(10, seed=seed)

# %%
events.describe()

# %% [markdown]
# ## Matches

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %% [markdown]
# ## Players

# %%
players.sample(10, seed=seed)

# %%
players.describe()

# %% [markdown]
# # Elo ratings

# %%
nobody_id = 440
first_season = events.select(pl.col("Season").min()).item()

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
            pl.min_horizontal("ScheduledDate", "StartDate", "EndDateEvent"),
            "EndDate",
            "StartDateEvent",
        )
    )
    .filter(pl.col("Date").dt.year() >= first_season)
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
def player_info_df(data, player_id_col):
    return (
        data.lazy()
        .group_by(PlayerID=player_id_col)
        .agg(
            pl.len().alias(f"{player_id_col}NumMatches"),
            pl.col("Date").min().alias(f"{player_id_col}FirstMatchDate"),
            pl.col("Date").max().alias(f"{player_id_col}LastMatchDate"),
        )
    )


player_info = (
    player_info_df(data, "Player1ID")
    .join(player_info_df(data, "Player2ID"), on="PlayerID", how="full")
    .select(
        ID=pl.coalesce("PlayerID", "PlayerID_right"),
        NumMatches=pl.col("Player1IDNumMatches").fill_null(0)
        + pl.col("Player2IDNumMatches").fill_null(0),
        FirstMatchDate=pl.min_horizontal(
            pl.col("Player1IDFirstMatchDate"),
            pl.col("Player2IDFirstMatchDate"),
        ),
        LastMatchDate=pl.max_horizontal(
            pl.col("Player1IDLastMatchDate"),
            pl.col("Player2IDLastMatchDate"),
        ),
    )
    .collect()
)
player_info.shape

# %%
elo_k = approximate_optimal_k(
    player_1_ids=data["Player1ID"],
    player_2_ids=data["Player2ID"],
    player_1_outcomes=data["Player1Outcome"],
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
elo_k

# %%
elo_ratings = calculate_elo_ratings(
    player_1_ids=data["Player1ID"],
    player_2_ids=data["Player2ID"],
    player_1_outcomes=data["Player1Outcome"],
    elo_k=elo_k,
    elo_scale=elo_scale,
    progress_bar=True,
)
len(elo_ratings)

# %%
elo_df = (
    pl.DataFrame({"ID": elo_ratings.keys(), "Elo": elo_ratings.values()})
    .join(players, on="ID", how="left")
    .join(player_info, on="ID", how="left")
    .sort("Elo", descending=True, nulls_last=True)
    .select(
        pl.col("Elo").rank(method="min", descending=True).alias("Rank"),
        pl.when(pl.col("SurnameFirst"))
        .then(pl.col("LastName") + " " + pl.col("FirstName"))
        .otherwise(pl.col("FirstName") + " " + pl.col("LastName"))
        .alias("Name"),
        "ID",
        "Elo",
        "NumMatches",
        "FirstMatchDate",
        "LastMatchDate",
    )
)
elo_df.shape

# %%
elo_df.describe()

# %%
elo_df.head(100)

# %%
elo_df.tail(100)

# %%
elo_df.write_csv("results/snooker/elo_ranking.csv", datetime_format="%+")


# %% [markdown]
# # Elo over time

# %%
def calculate_elo_ratings_by_month(data=data, elo_k=elo_k, elo_scale=elo_scale):
    curr_elo_ratings = None

    for (dt,), group in tqdm(
        data.group_by_dynamic(
            "Date",
            every="1mo",
            period="1mo",
            closed="left",
            label="right",
        )
    ):
        curr_elo_ratings = calculate_elo_ratings(
            player_1_ids=group["Player1ID"],
            player_2_ids=group["Player2ID"],
            player_1_outcomes=group["Player1Outcome"],
            init_elo_ratings=curr_elo_ratings,
            elo_k=elo_k,
            elo_scale=elo_scale,
            progress_bar=False,
        )

        df = pl.LazyFrame(
            data=np.array(list(curr_elo_ratings.values())).reshape(1, -1),
            schema=list(map(str, curr_elo_ratings.keys())),
        )
        yield df.select(pl.lit(dt.date()).alias("Date"), pl.all())


# %%
hist_elo = pl.concat(calculate_elo_ratings_by_month(), how="diagonal")
for player_id, last_match_date in tqdm(
    player_info.select("ID", "LastMatchDate").iter_rows(),
):
    player_id = str(player_id)
    last_match_date += timedelta(days=31)
    hist_elo = hist_elo.with_columns(
        pl.when(pl.col("Date") <= last_match_date).then(player_id).alias(player_id),
    )
hist_elo = hist_elo.collect()
hist_elo.shape

# %%
hist_elo.write_csv("results/snooker/elo_ratings_history.csv", float_precision=1)

# %%
hist_elo.tail(12)

# %%
_, ax = plt.subplots()
ax.step(x=hist_elo["Date"], y=hist_elo["1"], where="post", label="Mark Williams")
ax.step(x=hist_elo["Date"], y=hist_elo["5"], where="post", label="Ronnie O'Sullivan")
ax.step(x=hist_elo["Date"], y=hist_elo["237"], where="post", label="John Higgins")
ax.legend()
ax.grid(True)
ax.set_xlabel(None)
ax.set_ylabel("Elo")
plt.show()
