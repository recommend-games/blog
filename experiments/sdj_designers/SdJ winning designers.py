# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Spiel des Jahres winning designers

# %%
import jupyter_black
import polars as pl
from more_itertools import powerset
from pytility import arg_to_iter, clear_list, parse_int
from tabulate import tabulate

jupyter_black.load()

SEED = 23
# Set to e.g. "_2026" to write designers_2026.csv / games_2026.csv / table_2026.md
# instead of overwriting the originals.
OUTPUT_SUFFIX = "_2026"

pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_rows(100)
pl.Config.set_float_precision(6)

STEPS = ("winner", "sonderpreis", "nominated", "recommended")
COLUMN_STEPS = ("winner", "nominated", "recommended", "sonderpreis")
AWARDS = ("kenner", "kinder", "spiel")

# %% [markdown]
# ## Basic data

# %%
game_data = (
    pl.scan_csv(
        "../../../board-game-data/scraped/bgg_GameItem.csv",
        infer_schema_length=None,
    )
    .select(["bgg_id", "name", "year", "bayes_rating", "designer"])
    .collect()
)
game_data.shape

# %%
designers = (
    pl.scan_csv(
        "../../../board-game-data/scraped/bgg_Person.csv",
        infer_schema_length=None,
    )
    .select(["bgg_id", "name"])
    .collect()
)
designers.shape


# %%
def read_award(path, award):
    return (
        pl.read_csv(
            path,
            schema_overrides={
                "winner": pl.Int8,
                "nominated": pl.Int8,
                "recommended": pl.Int8,
                "sonderpreis": pl.String,
            },
        )
        .with_columns(pl.col(["winner", "nominated", "recommended"]).cast(pl.Boolean))
        .with_columns(pl.lit(award).alias("award"))
    )


sdj = read_award("sdj.csv", "spiel")
kennersdj = read_award("ksdj.csv", "kenner")
kindersdj = read_award("kindersdj.csv", "kinder")

awards = pl.concat([sdj, kennersdj, kindersdj], how="diagonal_relaxed")
awards = (
    awards.group_by("bgg_id")
    .agg(
        pl.col("jahrgang").max(),
        pl.col("winner").max(),
        pl.col("nominated").max(),
        pl.col("recommended").max(),
        pl.col("sonderpreis").drop_nulls().unique().sort().str.join(", "),
        pl.col("award").unique().sort().str.join(", "),
    )
    # Just one Exit and Sherlock game
    .filter(~pl.col("bgg_id").is_in([203416, 203417, 247436, 250779]))
    # The early "Beautiful Game" special awards clutter the results
    .with_columns(
        pl.when(pl.col("sonderpreis") == "Beautiful Game")
        .then(True)
        .otherwise(pl.col("recommended"))
        .alias("recommended"),
        pl.when(pl.col("sonderpreis") == "Beautiful Game")
        .then(pl.lit(""))
        .otherwise(pl.col("sonderpreis"))
        .alias("sonderpreis"),
    )
)
awards.shape

# %%
games_summary = (
    awards.with_columns((pl.col("sonderpreis").str.len_chars() > 0).alias("sonderpreis"))
    .group_by("award")
    .agg(
        pl.col("winner").sum(),
        pl.col("nominated").sum(),
        pl.col("recommended").sum(),
        pl.col("sonderpreis").sum(),
    )
)
print(tabulate(games_summary.rows(), headers=games_summary.columns, tablefmt="pipe"))

# %%
games = game_data.join(awards, on="bgg_id", how="inner")
games.shape


# %% [markdown]
# ## Counting awards

# %%
def parse_ids(value):
    if isinstance(value, str):
        return parse_ids(value.split(","))
    return clear_list(map(parse_int, arg_to_iter(value)))


designer_awards = (
    games.select(["bgg_id", "designer"])
    .with_columns(
        pl.col("designer")
        .map_elements(parse_ids, return_dtype=pl.List(pl.Int64))
        .alias("designer")
    )
    .explode("designer")
)
designer_awards.shape

# %%
columns = [
    "bgg_id",
    "name",
    "year",
    "award",
    "winner",
    "nominated",
    "recommended",
    "sonderpreis",
    "bayes_rating",
]
data = (
    games.select(columns)
    .filter(pl.col("award").is_not_null())
    .join(designer_awards, on="bgg_id", how="left")
    .with_columns(
        pl.col("designer").fill_null(3),
        pl.col("year").fill_null(0),
    )
)
data.shape

# %%
data.with_columns(
    pl.col(["winner", "nominated", "recommended"]).map_elements(
        lambda value: "True" if value else "False", return_dtype=pl.String
    )
).select(
    [
        "bgg_id",
        "name",
        "year",
        "award",
        "winner",
        "nominated",
        "recommended",
        "sonderpreis",
        "bayes_rating",
        "designer",
    ]
).write_csv(f"games{OUTPUT_SUFFIX}.csv")

# %%
best_rating = data.group_by("designer").agg(pl.col("bayes_rating").max().alias("best_rating"))
best_rating.shape

# %%
winner = data.filter(pl.col("winner"))
sonderpreis = data.filter(~pl.col("winner") & (pl.col("sonderpreis").str.len_chars() > 0))
nominated = data.filter(
    ~pl.col("winner")
    & ~(pl.col("sonderpreis").str.len_chars() > 0)
    & pl.col("nominated")
)
recommended = data.filter(
    ~pl.col("winner")
    & ~(pl.col("sonderpreis").str.len_chars() > 0)
    & ~pl.col("nominated")
    & pl.col("recommended")
)
winner.shape, sonderpreis.shape, nominated.shape, recommended.shape


# %%
def count_awards(data, label):
    count = data.pivot(
        on="award",
        index="designer",
        values="award",
        aggregate_function="len",
    ).fill_null(0)
    for award in AWARDS:
        if award not in count.columns:
            count = count.with_columns(pl.lit(0).alias(award))
    count = count.with_columns(pl.sum_horizontal(list(AWARDS)).alias("total"))
    count = count.select(
        ["designer"] + [pl.col(award).cast(pl.Int64) for award in (*AWARDS, "total")]
    )
    return count.rename({award: f"{label}_{award}" for award in (*AWARDS, "total")})


# %%
# Individual counts
winner_count = count_awards(winner, "winner")
nominated_count = count_awards(nominated, "nominated")
recommended_count = count_awards(recommended, "recommended")
sonderpreis_count = count_awards(sonderpreis, "sonderpreis")

# Join the counts
counts = (
    winner_count.join(nominated_count, on="designer", how="full", coalesce=True)
    .join(recommended_count, on="designer", how="full", coalesce=True)
    .join(sonderpreis_count, on="designer", how="full", coalesce=True)
    .join(best_rating, on="designer", how="left")
    .fill_null(0)
)

# "Uncredited" designs don't really make sense in our analysis
counts = counts.filter(pl.col("designer") != 3)

# Bring dtypes in correct format
count_columns = [
    f"{step}_{award}" for step in STEPS for award in (*AWARDS, "total")
]
counts = counts.with_columns([pl.col(c).cast(pl.Int64) for c in count_columns])

# Add some more data
counts = counts.join(
    designers.rename({"bgg_id": "designer", "name": "designer_name"}),
    on="designer",
    how="left",
).rename({"designer": "bgg_id", "designer_name": "name"})
counts = counts.with_columns(
    (
        pl.col("winner_total")
        + pl.col("nominated_total")
        + pl.col("recommended_total")
        + pl.col("sonderpreis_total")
    ).alias("total")
)

# Rank and sort
RANK_COLUMNS = [
    "winner_total",
    "sonderpreis_total",
    "nominated_total",
    "recommended_total",
    "winner_spiel",
    "winner_kenner",
    "winner_kinder",
    "sonderpreis_spiel",
    "sonderpreis_kenner",
    "sonderpreis_kinder",
    "nominated_spiel",
    "nominated_kenner",
    "nominated_kinder",
    "recommended_spiel",
    "recommended_kenner",
    "recommended_kinder",
    "total",
    "best_rating",
]
counts = (
    counts.sort(
        RANK_COLUMNS, descending=[True] * len(RANK_COLUMNS), nulls_last=True
    )
    .with_row_index("_rn", offset=1)
    .with_columns(pl.col("_rn").min().over(RANK_COLUMNS).alias("rank"))
    .drop("_rn")
    .sort(["rank", "name"], nulls_last=True)
)

# Done.
counts.shape

# %% [markdown]
# ## Overall results

# %%
counts.head(10)

# %%
column_order = (
    ["bgg_id", "name"]
    + [f"{step}_{award}" for step in COLUMN_STEPS for award in (*AWARDS, "total")]
    + ["best_rating", "total", "rank"]
)
counts.select(column_order).write_csv(f"designers{OUTPUT_SUFFIX}.csv")


# %%
def designer_table(counts):
    criterion = (pl.col("total") >= 5) | (
        (pl.col("winner_total") + pl.col("sonderpreis_total")) >= 2
    )
    result = "| Designer | Spiel | Kennerspiel | Kinderspiel | Total |\n"
    result += "|:---------|:-----:|:-----------:|:-----------:|:-----:|\n"
    for row in counts.filter(criterion).iter_rows(named=True):
        bgg_id = row["bgg_id"]
        cells = [
            "",
            f" [{row['name']}](https://recommend.games/#/?designer={bgg_id:.0f}) ",
        ]
        for award in ("spiel", "kenner", "kinder"):
            winner = row[f"winner_{award}"]
            sonderpreis = row[f"sonderpreis_{award}"]
            sonderpreis_str = f" ({sonderpreis:.0f})" if sonderpreis > 0 else ""
            nominated = row[f"nominated_{award}"]
            recommended = row[f"recommended_{award}"]
            cells.append(
                f" {winner:.0f}{sonderpreis_str} / {nominated:.0f} / {recommended:.0f} "
            )
        cells.append(f" {row['total']} ")
        cells.append("")
        result += "|".join(cells)
        result += "\n"
    return result


# %%
with open(f"table{OUTPUT_SUFFIX}.md", "w") as f:
    f.write(designer_table(counts))

# %% [markdown]
# ## More statistics


# %%
def has_any(award, steps):
    return pl.any_horizontal([pl.col(f"{step}_{award}") > 0 for step in steps])


def all_awards(award_set, steps):
    return pl.all_horizontal([has_any(award, steps) for award in award_set])


awards_full_names = dict(
    zip(
        AWARDS,
        ("Kennerspiel des Jahres", "Kinderspiel des Jahres", "Spiel des Jahres"),
    )
)

for award_set in powerset(("spiel", "kenner", "kinder")):
    award_set = list(award_set)
    if not award_set:
        # skip empty set
        continue
    num_longlist = counts.select(all_awards(award_set, STEPS)).to_series().sum()
    num_shortlist = counts.select(all_awards(award_set, STEPS[:3])).to_series().sum()
    num_winner_any = counts.select(all_awards(award_set, STEPS[:2])).to_series().sum()
    num_winner = counts.select(all_awards(award_set, STEPS[:1])).to_series().sum()
    headline = " & ".join(awards_full_names[award] for award in award_set)
    print(f"### {headline}")
    print()
    print(f"- {num_longlist:d} different designers had a game on the longlist")
    print(f"- {num_shortlist:d} different designers had a game on the shortlist")
    if num_winner < num_winner_any:
        print(
            f"- {num_winner_any:d} different designers won the award (incl special awards)"
        )
    print(f"- {num_winner:d} different designers won the main award")
    print()
    print()


# %%
def cat_count(steps):
    return pl.sum_horizontal(
        [has_any(award, steps).cast(pl.Int64) for award in ("spiel", "kenner", "kinder")]
    )


cat_count_longlist = counts.select(cat_count(STEPS).alias("n")).to_series()
cat_count_shortlist = counts.select(cat_count(STEPS[:3]).alias("n")).to_series()
cat_count_winner_any = counts.select(cat_count(STEPS[:2]).alias("n")).to_series()
cat_count_winner = counts.select(cat_count(STEPS[:1]).alias("n")).to_series()
(
    cat_count_longlist.shape,
    cat_count_shortlist.shape,
    cat_count_winner_any.shape,
    cat_count_winner.shape,
)

# %%
count_lists = {
    "Longlist": cat_count_longlist,
    "Shortlist": cat_count_shortlist,
    "Winner (incl special award)": cat_count_winner_any,
    "Winner (main award)": cat_count_winner,
}

for title, count_list in count_lists.items():
    print(f"### {title}")
    print()
    value_counts = (
        count_list.value_counts()
        .sort("n", descending=True)
        .with_columns(pl.col("count").cum_sum().alias("cum"))
    )
    for num, count in zip(value_counts["n"], value_counts["cum"]):
        if num > 0:
            print(
                f"- {count} designer{'' if count == 1 else 's'} appear in {'all' if num == 3 else 'at least'} {num} categor{'y' if num == 1 else 'ies'}"
            )
    print()
    print()

# %%
report_awards = ("total", "spiel", "kenner", "kinder")
award_titles = (
    "Overall",
    "Spiel des Jahres",
    "Kennerspiel des Jahres",
    "Kinderspiel des Jahres",
)
step_titles = (
    "Most wins (main award)",
    "Most wins (incl special award)",
    "Most games on the shortlist",
    "Most games on the longlist",
)
print("## Designer records")
for award, award_title in zip(report_awards, award_titles):
    print(f"\n\n### {award_title}\n")

    for i in range(len(STEPS), 0, -1):
        num_games_expr = pl.sum_horizontal(
            [pl.col(f"{step}_{award}") for step in STEPS[:i]]
        )
        tmp = counts.with_columns(num_games_expr.alias("_num_games"))
        most = tmp["_num_games"].max()
        print(f"- {step_titles[i - 1]}: {most}")
        for bgg_id, name in tmp.filter(pl.col("_num_games") == most)[
            ["bgg_id", "name"]
        ].iter_rows():
            print(f"  - [{name}](https://recommend.games/#/?designer={bgg_id:.0f})")

    nominated = counts.filter(pl.col(f"winner_{award}") == 0).sort(
        f"nominated_{award}",
        descending=True,
        maintain_order=True,
    )
    nominated_num = nominated[f"nominated_{award}"].max()
    print(f"- Most games on the shortlist without win: {nominated_num}")
    for bgg_id, name in nominated.filter(pl.col(f"nominated_{award}") == nominated_num)[
        ["bgg_id", "name"]
    ].iter_rows():
        print(f"  - [{name}](https://recommend.games/#/?designer={bgg_id:.0f})")
