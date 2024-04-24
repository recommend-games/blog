# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
import jupyter_black
import polars as pl
from rankings_by_country.countries import CONVERTER, get_country_code, get_flag_emoji
from rankings_by_country.data import load_population_data

jupyter_black.load()

PROJECT_DIR = Path(".").resolve()
BASE_DIR = PROJECT_DIR.parent.parent
DATA_DIR = BASE_DIR.parent / "board-game-data"
PROJECT_DIR, BASE_DIR, DATA_DIR

# %%
markdown_settings = {
    "tbl_formatting": "ASCII_MARKDOWN",
    "tbl_hide_column_data_types": True,
    "tbl_hide_dataframe_shape": True,
    "tbl_width_chars": 999,
    "fmt_str_lengths": 999,
}

# %%
ratings = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_rating")
    .drop_nulls()
)
users = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_UserItem.jl")
    .select("bgg_user_name", "country")
    .with_columns(
        country_code=pl.col("country")
        .map_elements(get_country_code, return_dtype=pl.String)
        .str.to_lowercase()
    )
    .drop_nulls()
)
data = ratings.join(other=users, on="bgg_user_name", how="inner")

# %%
data.select(
    pl.n_unique("bgg_id", "bgg_user_name", "country_code"),
    num_ratings=pl.len(),
).collect()

# %%
game_data = pl.scan_csv(DATA_DIR / "scraped" / "bgg_GameItem.csv").select(
    "bgg_id",
    "name",
    "year",
)
bayes = (
    data.with_columns(num_ratings_per_country=pl.len().over("country_code"))
    .filter(pl.col("num_ratings_per_country") >= 10_000)
    .with_columns(
        num_dummies=pl.col("num_ratings_per_country") / 10_000,
        num_ratings=pl.len().over("country_code", "bgg_id"),
    )
    .filter(pl.col("num_ratings") >= pl.min_horizontal(3 * pl.col("num_dummies"), 30))
    .group_by("country_code", "bgg_id")
    .agg(
        pl.col("num_dummies").first(),
        pl.col("num_ratings").first(),
        avg_rating=pl.col("bgg_user_rating").mean(),
    )
    .with_columns(
        bayes_rating=(
            pl.col("avg_rating") * pl.col("num_ratings") + 5.5 * pl.col("num_dummies")
        )
        / (pl.col("num_ratings") + pl.col("num_dummies"))
    )
    .with_columns(
        rank=pl.col("bayes_rating")
        .rank(method="min", descending=True)
        .over("country_code")
    )
    .join(game_data, on="bgg_id")
    .sort(
        "num_dummies",
        "country_code",
        "rank",
        "bgg_id",
        descending=[True, False, False, False],
    )
    .collect()
)
bayes.shape

# %%
bayes.select(pl.n_unique("country_code"))

# %%
rankings_dir = PROJECT_DIR / "rankings"
rankings_dir.mkdir(parents=True, exist_ok=True)
partitions = bayes.select(
    "country_code",
    "rank",
    "bgg_id",
    "name",
    "year",
    "avg_rating",
    "bayes_rating",
    "num_ratings",
).partition_by(["country_code"], maintain_order=True, include_key=True, as_dict=True)
for (country_code,), group_data in partitions.items():
    group_data.write_csv(rankings_dir / f"{country_code}.csv", float_precision=5)

# %%
population_data = load_population_data()

country_users = data.group_by("country_code").agg(
    num_users=pl.col("bgg_user_name").n_unique(),
    total_ratings=pl.len(),
)

# TODO: Ensure uniqueness of #1 ranked game
top_games = (
    bayes.lazy()
    .filter(pl.col("rank") == 1)
    .select(
        "country_code",
        "bgg_id",
        "name",
        "year",
        "num_ratings",
        "avg_rating",
        "bayes_rating",
    )
    .select("country_code", pl.exclude("country_code").name.prefix("top_game_"))
)

country_data = (
    population_data.select(
        "country_code",
        country_name=pl.col("country_code").map_elements(
            lambda c: CONVERTER.convert(c, to="name"),
            pl.String,
        ),
        flag=pl.col("country_code").map_elements(get_flag_emoji, pl.String),
        population="population",
        population_rank=pl.col("population").rank(method="min", descending=True),
    )
    .join(country_users, on="country_code", how="outer")
    .with_columns(
        country_code=pl.coalesce("country_code", "country_code_right"),
        total_ratings_rank=pl.col("total_ratings").rank(method="min", descending=True),
        ratings_per_capita=(pl.col("total_ratings") / pl.col("population")) * 100_000,
    )
    .drop("country_code_right")
    .with_columns(
        ratings_per_capita_rank=pl.when(pl.col("total_ratings") >= 10_000)
        .then(pl.col("ratings_per_capita"))
        .rank(method="min", descending=True)
    )
    .join(
        top_games,
        on="country_code",
        how="left",
    )
    .sort(
        "total_ratings",
        "ratings_per_capita",
        "population",
        "country_code",
        descending=[True, True, True, False],
        nulls_last=True,
    )
    .collect()
)
country_data.shape

# %%
country_data.sort("total_ratings_rank", nulls_last=True).head(10)

# %%
country_data.sort("ratings_per_capita_rank", nulls_last=True).head(10)

# %%
country_data.filter(pl.col("country_code").is_in(["aq", "va"]))

# %%
top_games_by_country = (
    country_data.sort("total_ratings_rank", nulls_last=True)
    .head(10)
    .select(
        pl.format("**{} {}**", "flag", "country_name").alias("Country"),
        pl.format(
            "{} mil",
            (pl.col("population") / 1_000_000).round(1),
        ).alias("Population"),
        pl.format(
            "{}k",
            (pl.col("num_users") / 1_000).round(1),
        ).alias("Users"),
        pl.format(
            "{}k",
            pl.col("total_ratings") // 1_000,
        ).alias("Ratings"),
        pl.col("ratings_per_capita").cast(pl.Int64).alias("Per 100k residents"),
        pl.format(
            "{{% game {} %}}{}{{% /game %}}",
            "top_game_bgg_id",
            "top_game_name",
        ).alias("#1 rated game"),
    )
)
with pl.Config(**markdown_settings):
    print(top_games_by_country)

# %%
country_data["top_game_name"].n_unique()

# %%
top_games_count = (
    country_data.lazy()
    .select(bgg_id="top_game_bgg_id")
    .select(pl.col("bgg_id").value_counts())
    .unnest("bgg_id")
    .join(game_data, on="bgg_id")
    .filter(pl.col("count") > 1)
    .sort("count", descending=True)
    .select(
        Game=pl.format("{{% game {} %}}{}{{% /game %}}", "bgg_id", "name"),
        Count="count",
    )
    .collect()
)
with pl.Config(**markdown_settings):
    print(top_games_count)

# %%
country_data.write_csv(PROJECT_DIR / "countries.csv", float_precision=3)

# %%
country_links = (
    country_data.filter(pl.col("top_game_bgg_id").is_not_null())
    .sort("country_name")
    .select(
        link=pl.format(
            "[{} {}](rankings/{}.csv)",
            "flag",
            "country_name",
            "country_code",
        )
    )["link"]
)
print(" | ".join(country_links))
