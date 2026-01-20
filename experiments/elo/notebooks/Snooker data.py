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
import numpy as np
import polars as pl
import seaborn as sns
from datetime import date, timedelta
from elo.optimal_k import approximate_optimal_k
from elo.elo_ratings import TwoPlayerElo
from pathlib import Path
from matplotlib import pyplot as plt
from tqdm import tqdm

jupyter_black.load()
pl.Config.set_tbl_rows(200)
sns.set_style("dark")

seed = 13
elo_scale = 400

# %%
data_dir = Path("../results/snooker/").resolve()
arrow_dir = Path("../results/arrow/matches").resolve()
arrow_dir.mkdir(parents=True, exist_ok=True)
result_dir = Path("../csv/snooker").resolve()
result_dir.mkdir(parents=True, exist_ok=True)
plot_dir = Path("../plots/snooker").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
data_dir, arrow_dir, result_dir, plot_dir

# %% [markdown]
# # General EDA

# %% [markdown]
# ## Events

# %%
events = (
    pl.scan_ndjson(data_dir / "events*.jl")
    .select(
        "ID",
        "Name",
        "StartDate",
        "EndDate",
        "Season",
        "Discipline",
        "Team",
        "scraped_at",
    )
    .sort("scraped_at")
    .drop("scraped_at")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(
        pl.col("StartDate", "EndDate").str.to_date().cast(pl.Datetime(time_zone="UTC")),
    )
    .collect()
)
events.shape

# %%
events.sample(10, seed=seed)

# %%
events.describe()

# %% [markdown]
# ## Matches

# %%
matches = (
    pl.scan_ndjson(data_dir / "matches*.jl", infer_schema_length=10_000)
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
matches.shape

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %% [markdown]
# ## Players

# %%
players = (
    pl.scan_ndjson(data_dir / "players*.jl", infer_schema_length=10_000)
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(pl.col("Born", "Died").str.to_date(strict=False))
    .collect()
)
players.shape

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
data.sample(10)

# %%
data.lazy().select(
    num_players=2,
    player_ids=pl.when("Player1Outcome")
    .then(pl.concat_list("Player1ID", "Player2ID"))
    .otherwise(pl.concat_list("Player2ID", "Player1ID")),
    places=[1, 2],
    payoffs=[1, 0],
).sink_ipc(arrow_dir / "snooker.arrow")


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


def df_to_numpy(data):
    return data.select(
        winner=pl.when("Player1Outcome").then("Player1ID").otherwise("Player2ID"),
        loser=pl.when("Player1Outcome").then("Player2ID").otherwise("Player1ID"),
    ).to_numpy()


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
matches_array = df_to_numpy(data)
elo_k = approximate_optimal_k(
    matches=matches_array,
    two_player_only=True,
    min_elo_k=0,
    max_elo_k=elo_scale / 2,
    elo_scale=elo_scale,
)
elo_k

# %%
elo = TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)
elo.update_elo_ratings_batch(matches=matches_array, progress_bar=True)
elo_ratings = elo.elo_ratings
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
elo_df.write_csv(
    result_dir / "elo_ranking.csv",
    datetime_format="%+",
    float_precision=3,
)

# %%
_, ax = plt.subplots()
sns.kdeplot(
    data=elo_df["Elo"],
    clip=(-elo_scale / 2, elo_scale / 2),
    ax=ax,
)
ax.legend([])
ax.grid(True)
ax.set_title("Elo ratings distribution of Snooker players")
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()
plt.savefig(plot_dir / "elo_distribution.png")
plt.savefig(plot_dir / "elo_distribution.svg")
plt.show()


# %% [markdown]
# # Elo over time


# %%
def calculate_elo_ratings_by_month(data=data, elo_k=elo_k, elo_scale=elo_scale):
    elo = TwoPlayerElo(elo_k=elo_k, elo_scale=elo_scale)

    for (dt,), group in tqdm(
        data.group_by_dynamic(
            "Date",
            every="1mo",
            period="1mo",
            closed="left",
            label="right",
        )
    ):
        matches_array = df_to_numpy(group)
        elo.update_elo_ratings_batch(matches=matches_array, progress_bar=False)
        df = pl.LazyFrame(
            data=np.array(list(elo.elo_ratings.values())).reshape(1, -1),
            schema=list(map(str, elo.elo_ratings.keys())),
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
player_cols = sorted(hist_elo.select(pl.exclude("Date")).columns, key=int)
len(player_cols)

# %%
hist_elo.select("Date", *player_cols).write_csv(
    result_dir / "elo_ratings_history.csv",
    float_precision=1,
)

# %%
hist_elo.select("Date", *player_cols).tail(12)

# %%
_, ax = plt.subplots()
plot_data = hist_elo.filter(
    pl.col("Date") >= date.today() - timedelta(days=10 * 365.25)
)
ax.step(x=plot_data["Date"], y=plot_data["5"], where="post", label="Ronnie O'Sullivan")
ax.step(x=plot_data["Date"], y=plot_data["237"], where="post", label="John Higgins")
ax.step(x=plot_data["Date"], y=plot_data["1"], where="post", label="Mark Williams")
ax.legend()
ax.grid(True)
ax.set_xlabel(None)
ax.set_ylabel("Elo")
plt.show()

# %%
long_hist = (
    hist_elo.lazy()
    .unpivot(index="Date", variable_name="ID", value_name="Elo")
    .filter(pl.col("Elo").is_not_null())
    .with_columns(pl.col("ID").cast(pl.Int64))
)
max_elo = long_hist.group_by("Date").agg(EloMax=pl.col("Elo").max())
top_rated_players = (
    long_hist.join(max_elo, on="Date", how="inner")
    .filter(pl.col("Elo") == pl.col("EloMax"))
    .drop("EloMax")
    .join(elo_df.lazy().select("ID", "Name"), on="ID", how="left")
    .sort("Date")
    .collect()
)
full_dates = pl.date_range(
    start=top_rated_players["Date"].min(),
    end=top_rated_players["Date"].max(),
    interval="1mo",
    eager=True,
).alias("Date")
top_rated_players = (
    pl.DataFrame({"Date": full_dates})
    .join(top_rated_players, on="Date", how="left")
    .fill_null(strategy="forward")
)
top_rated_players.shape

# %%
top_rated_months = (
    top_rated_players.group_by("Name")
    .agg(
        Months=pl.len(),
        First=pl.col("Date").min(),
        Last=pl.col("Date").max(),
    )
    .sort("Months", "First", descending=[True, False])
)
top_rated_months

# %%
top_rated_players.filter(pl.col("Elo") == pl.col("Elo").max())

# %%
top_rated_players_compact = (
    top_rated_players.with_columns(
        group=(pl.col("ID") != pl.col("ID").shift())
        .cast(pl.Int8)
        .fill_null(0)
        .cum_sum()
    )
    .group_by("group", maintain_order=True)
    .agg(
        pl.col("Date").first().alias("DateFrom"),
        pl.col("Date").last().alias("DateTo"),
        pl.col("ID").first(),
        pl.col("Name").first(),
        pl.col("Elo").max(),
    )
    .with_columns(
        Months=(
            (pl.col("DateTo") - pl.col("DateFrom")).dt.total_days() / 365.25 * 12 + 1
        )
        .round()
        .cast(pl.Int64),
    )
)
top_rated_players_compact.shape

# %%
top_rated_players_compact

# %%
top_rated_players.write_csv(
    result_dir / "elo_top_rated_players.csv",
    float_precision=1,
)

# %%
line_styles = ("dashed", "dashdot", "dotted")
colors = ("crimson", "purple", "darkblue")
top_n_players = 3

assert len(line_styles) == top_n_players
assert len(colors) == top_n_players

for year in range(1970, 2021, 10):
    start_date = date(year, 1, 1)
    end_date = date(year + 10, 1, 1)
    print(start_date, end_date)
    player_df = (
        long_hist.filter(pl.col("Date") >= start_date)
        .filter(pl.col("Date") < end_date)
        .group_by("ID")
        .agg(pl.col("Elo").max())
        .sort("Elo", descending=True)
        .head(top_n_players)
        .join(elo_df.lazy().select("ID", "Name"), on="ID", how="left")
        .collect()
    )

    _, ax = plt.subplots()
    plot_data = hist_elo.filter(pl.col("Date") >= start_date).filter(
        pl.col("Date") < end_date
    )
    for (id_, elo, name), line_style, color in zip(
        player_df.iter_rows(),
        line_styles,
        colors,
    ):
        ax.step(
            x=plot_data["Date"],
            y=plot_data[str(id_)],
            where="post",
            linestyle=line_style,
            color=color,
            label=f"{name} (max: {elo:.0f})",
        )
    ax.legend()
    ax.grid(True)
    min_max_year = plot_data.select(
        min_year=pl.col("Date").dt.year().min(),
        max_year=pl.col("Date").dt.year().max(),
    )
    min_year = min_max_year.item(0, 0)
    max_year = min_max_year.item(0, 1)
    ax.set_title(f"Highest rated players {min_year}–{max_year}")
    ax.set_xlabel(None)
    ax.set_ylabel("Elo")
    plt.tight_layout()
    plt.savefig(plot_dir / f"elo_timeseries_{year}.png")
    plt.savefig(plot_dir / f"elo_timeseries_{year}.svg")
    plt.show()
