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
from pathlib import Path
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

DATA_DIR = Path.home() / "Recommend.Games" / "board-game-data" / "scraped"

# %% [markdown]
# ## Basic data

# %%
game_data = pl.scan_csv(DATA_DIR / "bgg_GameItem.csv", infer_schema_length=None).select(
    "bgg_id",
    "name",
    "year",
    "bayes_rating",
    "designer",
)
designers = pl.scan_csv(DATA_DIR / "bgg_Person.csv", infer_schema_length=None).select(
    "bgg_id",
    "name",
)
game_data.collect_schema(), designers.collect_schema()


# %%
def read_award(path, award):
    return (
        pl.scan_csv(
            path,
            schema_overrides={
                "winner": pl.Int8,
                "nominated": pl.Int8,
                "recommended": pl.Int8,
                "sonderpreis": pl.String,
            },
        )
        .with_columns(pl.col(["winner", "nominated", "recommended"]).cast(pl.Boolean))
        .with_columns(award=pl.lit(award))
    )


sdj = read_award("sdj.csv", "spiel")
kennersdj = read_award("ksdj.csv", "kenner")
kindersdj = read_award("kindersdj.csv", "kinder")

awards = (
    pl.concat([sdj, kennersdj, kindersdj], how="diagonal_relaxed")
    .group_by("bgg_id")
    .agg(
        pl.col("jahrgang").max(),
        pl.col("jahrgang").min().alias("first_jahrgang"),
        pl.col("winner").max(),
        pl.col("nominated").max(),
        pl.col("recommended").max(),
        pl.col("sonderpreis").drop_nulls().unique().sort().str.join(", "),
        pl.col("award").unique().sort().str.join(", "),
    )
    # Just one Exit and Sherlock game
    .filter(~pl.col("bgg_id").is_in([203416, 203417, 247436, 250779]))
    # Games with no Sonderpreis end up with an empty string, not null
    .with_columns(
        sonderpreis=pl.when(pl.col("sonderpreis") == "")
        .then(None)
        .otherwise(pl.col("sonderpreis"))
    )
    # The early "Beautiful Game" special awards clutter the results
    .with_columns(
        recommended=pl.when(pl.col("sonderpreis") == "Beautiful Game")
        .then(True)
        .otherwise(pl.col("recommended")),
        sonderpreis=pl.when(pl.col("sonderpreis") == "Beautiful Game")
        .then(None)
        .otherwise(pl.col("sonderpreis")),
    )
    .cache()
)
awards.collect_schema()

# %%
games_summary = (
    awards.with_columns(pl.col("sonderpreis").is_not_null())
    .group_by("award")
    .agg(
        pl.col("winner").sum(),
        pl.col("nominated").sum(),
        pl.col("recommended").sum(),
        pl.col("sonderpreis").sum(),
    )
    .sort("award")
    .collect()
)
print(tabulate(games_summary.rows(), headers=games_summary.columns, tablefmt="pipe"))

# %%
games = game_data.join(awards, on="bgg_id", how="inner").cache()
games.collect_schema()


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
        pl.col("designer").map_elements(parse_ids, return_dtype=pl.List(pl.Int64))
    )
    .explode("designer", empty_as_null=False)
)

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
    "jahrgang",
    "first_jahrgang",
]
data = (
    games.select(columns)
    .filter(pl.col("award").is_not_null())
    .join(designer_awards, on="bgg_id", how="left")
    .with_columns(
        pl.col("designer").fill_null(3),
        pl.col("year").fill_null(0),
    )
    .cache()
)
data.collect_schema()

# %%
data.with_columns(
    pl.col("winner", "nominated", "recommended").map_elements(
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
).sort(
    "bgg_id",
    "designer",
).sink_csv(
    f"games{OUTPUT_SUFFIX}.csv"
)

# %%
best_rating = data.group_by("designer").agg(best_rating=pl.col("bayes_rating").max())

# %%
winner = data.filter(pl.col("winner"))
sonderpreis = data.filter(~pl.col("winner") & pl.col("sonderpreis").is_not_null())
nominated = data.filter(
    ~pl.col("winner") & pl.col("sonderpreis").is_null() & pl.col("nominated")
)
recommended = data.filter(
    ~pl.col("winner")
    & pl.col("sonderpreis").is_null()
    & ~pl.col("nominated")
    & pl.col("recommended")
)


# %%
def count_awards(data, label):
    count = (
        data.pivot(
            on="award",
            on_columns=list(AWARDS),
            index="designer",
            values="award",
            aggregate_function="len",
        )
        .fill_null(0)
        .with_columns(total=pl.sum_horizontal(list(AWARDS)))
        .select(
            ["designer"]
            + [pl.col(award).cast(pl.Int64) for award in (*AWARDS, "total")]
        )
        .rename({award: f"{label}_{award}" for award in (*AWARDS, "total")})
    )
    return count


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
count_columns = [f"{step}_{award}" for step in STEPS for award in (*AWARDS, "total")]
counts = counts.with_columns([pl.col(c).cast(pl.Int64) for c in count_columns])

# Add some more data
counts = counts.join(
    designers.rename({"bgg_id": "designer", "name": "designer_name"}),
    on="designer",
    how="left",
).rename({"designer": "bgg_id", "designer_name": "name"})
counts = counts.with_columns(
    total=pl.col("winner_total")
    + pl.col("nominated_total")
    + pl.col("recommended_total")
    + pl.col("sonderpreis_total")
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
    counts.sort(RANK_COLUMNS, descending=[True] * len(RANK_COLUMNS), nulls_last=True)
    .with_row_index("_rn", offset=1)
    .with_columns(rank=pl.col("_rn").min().over(RANK_COLUMNS))
    .drop("_rn")
    .sort(["rank", "name"], nulls_last=True)
    .collect()
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
# At least 2 wins (incl special awards) or at least 5 listed games
HALL_OF_FAME = (pl.col("total") >= 5) | (
    (pl.col("winner_total") + pl.col("sonderpreis_total")) >= 2
)


def designer_table(counts):
    criterion = HALL_OF_FAME
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
        [
            has_any(award, steps).cast(pl.Int64)
            for award in ("spiel", "kenner", "kinder")
        ]
    )


cat_count_longlist = counts.select(n=cat_count(STEPS)).to_series()
cat_count_shortlist = counts.select(n=cat_count(STEPS[:3])).to_series()
cat_count_winner_any = counts.select(n=cat_count(STEPS[:2])).to_series()
cat_count_winner = counts.select(n=cat_count(STEPS[:1])).to_series()
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
        .with_columns(cum=pl.col("count").cum_sum())
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
        tmp = counts.with_columns(
            _num_games=pl.sum_horizontal(
                [pl.col(f"{step}_{award}") for step in STEPS[:i]]
            )
        )
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

# %% [markdown]
# ## Timelines

# %%
# Special award winners count as shortlisted
SHORTLIST = pl.col("winner") | pl.col("sonderpreis").is_not_null() | pl.col("nominated")
AWARD_SHORT_NAMES = {"spiel": "Spiel", "kenner": "Kennerspiel", "kinder": "Kinderspiel"}


def designer_link(bgg_id, name):
    return f"[{name}](https://recommend.games/#/?designer={bgg_id:.0f})"


timeline = (
    data.filter(pl.col("designer") != 3)
    .join(
        designers.rename({"bgg_id": "designer", "name": "designer_name"}),
        on="designer",
        how="left",
    )
    .with_columns(shortlist=SHORTLIST)
    .select(
        "designer",
        "designer_name",
        "bgg_id",
        "name",
        "award",
        "jahrgang",
        "first_jahrgang",
        "winner",
        "shortlist",
    )
    .sort("jahrgang", "award", "name", "designer")
    .collect()
)
timeline.shape

# %% [markdown]
# ### Gaps between wins

# %%
wins = (
    timeline.filter(pl.col("winner"))
    .sort("designer", "jahrgang", "award")
    .with_columns(
        prev_jahrgang=pl.col("jahrgang").shift().over("designer"),
        prev_name=pl.col("name").shift().over("designer"),
        prev_award=pl.col("award").shift().over("designer"),
    )
    .filter(pl.col("prev_jahrgang").is_not_null())
    .with_columns(gap=pl.col("jahrgang") - pl.col("prev_jahrgang"))
)


def print_wins(wins):
    for row in wins.iter_rows(named=True):
        print(
            f"- {designer_link(row['designer'], row['designer_name'])}: "
            f"{row['prev_name']} ({AWARD_SHORT_NAMES[row['prev_award']]} {row['prev_jahrgang']}) → "
            f"{row['name']} ({AWARD_SHORT_NAMES[row['award']]} {row['jahrgang']})"
        )


print("### Longest gaps between two wins\n")
print_wins(
    wins.filter(pl.col("gap") >= 10).sort("gap", "jahrgang", descending=[True, False])
)
print("\n\n### Wins in the same or consecutive years\n")
print_wins(wins.filter(pl.col("gap") <= 1).sort("jahrgang", "designer_name"))

# %%
win_spans = (
    timeline.filter(pl.col("winner"))
    .sort("jahrgang", "award")
    .group_by("designer", "designer_name")
    .agg(
        num_wins=pl.len(),
        first_win=pl.col("jahrgang").first(),
        first_game=pl.col("name").first(),
        first_award=pl.col("award").first(),
        last_win=pl.col("jahrgang").last(),
        last_game=pl.col("name").last(),
        last_award=pl.col("award").last(),
    )
    .with_columns(span=pl.col("last_win") - pl.col("first_win"))
    .filter(pl.col("span") >= 10)
    .sort("span", "first_win", descending=[True, False])
)
print("### Longest spans from first to most recent win\n")
for row in win_spans.iter_rows(named=True):
    print(
        f"- {designer_link(row['designer'], row['designer_name'])}: "
        f"{row['first_game']} ({AWARD_SHORT_NAMES[row['first_award']]} {row['first_win']}) → "
        f"{row['last_game']} ({AWARD_SHORT_NAMES[row['last_award']]} {row['last_win']}), "
        f"{row['span']} years, {row['num_wins']} wins"
    )

# %% [markdown]
# ### Several games on the shortlist in the same year

# %%
multi_shortlist = (
    timeline.filter(pl.col("shortlist"))
    .with_columns(
        label=pl.format(
            "{} ({}{})",
            pl.col("name"),
            pl.col("award").replace_strict(AWARD_SHORT_NAMES),
            pl.when(pl.col("winner")).then(pl.lit(", winner")).otherwise(pl.lit("")),
        )
    )
    .group_by("designer", "designer_name", "jahrgang")
    .agg(num_games=pl.len(), games=pl.col("label"))
    .filter(pl.col("num_games") >= 2)
    .sort("jahrgang", "designer_name")
)
for row in multi_shortlist.iter_rows(named=True):
    print(
        f"- {row['jahrgang']}: {designer_link(row['designer'], row['designer_name'])} "
        f"– {', '.join(row['games'])}"
    )

# %% [markdown]
# ### Shots at the triple
#
# Shortlisted in one category while already holding wins in the other two.

# %%
first_wins = (
    timeline.filter(pl.col("winner"))
    .group_by("designer", "designer_name")
    .agg(
        [
            pl.col("jahrgang")
            .filter(pl.col("award") == award)
            .min()
            .alias(f"first_win_{award}")
            for award in AWARDS
        ]
    )
)

shots = []
for award in AWARDS:
    others = [other for other in AWARDS if other != award]
    shots.append(
        timeline.filter(pl.col("shortlist") & (pl.col("award") == award))
        .join(first_wins.drop("designer_name"), on="designer")
        .filter(
            pl.all_horizontal(
                [pl.col(f"first_win_{other}") <= pl.col("jahrgang") for other in others]
            )
            & (
                pl.col(f"first_win_{award}").is_null()
                | (pl.col(f"first_win_{award}") >= pl.col("jahrgang"))
            )
        )
    )
shots = pl.concat(shots).sort("jahrgang", "designer_name")

for row in shots.iter_rows(named=True):
    held = ", ".join(
        f"{AWARD_SHORT_NAMES[other]} {row[f'first_win_{other}']}"
        for other in AWARDS
        if other != row["award"]
    )
    result = "won" if row["winner"] else "missed"
    print(
        f"- {row['jahrgang']}: {designer_link(row['designer'], row['designer_name'])} "
        f"– {row['name']} ({AWARD_SHORT_NAMES[row['award']]}), "
        f"holding {held}: {result}"
    )

# %%
print("### Wins in exactly two categories: record in the third\n")
two_categories = first_wins.filter(
    pl.sum_horizontal([pl.col(f"first_win_{award}").is_not_null() for award in AWARDS])
    == 2
).sort("designer_name")
for row in two_categories.iter_rows(named=True):
    missing = next(award for award in AWARDS if row[f"first_win_{award}"] is None)
    won = ", ".join(
        f"{AWARD_SHORT_NAMES[award]} {row[f'first_win_{award}']}"
        for award in AWARDS
        if award != missing
    )
    third = timeline.filter(
        (pl.col("designer") == row["designer"]) & (pl.col("award") == missing)
    )
    listings = (
        ", ".join(
            f"{game['name']} ({'shortlist' if game['shortlist'] else 'longlist'} {game['jahrgang']})"
            for game in third.iter_rows(named=True)
        )
        or "never listed"
    )
    print(
        f"- {designer_link(row['designer'], row['designer_name'])} "
        f"(first wins: {won}) – {AWARD_SHORT_NAMES[missing]}: {listings}"
    )

# %% [markdown]
# ### Careers

# %%
first_win = pl.col("jahrgang").filter(pl.col("winner")).min()
careers = (
    timeline.group_by("designer", "designer_name")
    .agg(
        first=pl.col("first_jahrgang").min(),
        last=pl.col("jahrgang").max(),
        seasons=pl.col("jahrgang").append(pl.col("first_jahrgang")).n_unique(),
        num_games=pl.col("bgg_id").n_unique(),
        num_shortlist=pl.col("shortlist").sum(),
        num_wins=pl.col("winner").sum(),
        first_win=first_win,
        games_before_first_win=(pl.col("first_jahrgang") < first_win).sum(),
        first_win_debut=(
            pl.col("first_jahrgang").filter(pl.col("winner")).min()
            == pl.col("first_jahrgang").min()
        ),
    )
    .with_columns(span=pl.col("last") - pl.col("first"))
    .sort("seasons", "num_games", descending=True)
)
careers.head(15)

# %%
careers.sort("span", "num_games", descending=True).head(15)

# %% [markdown]
# ### Newcomers among the winners

# %%
winning_careers = careers.filter(pl.col("first_win").is_not_null())
num_winners = winning_careers.height
num_debut_wins = winning_careers["first_win_debut"].sum()
num_one_and_done = winning_careers.filter(pl.col("num_games") == 1).height
print(
    f"- {num_debut_wins} of {num_winners} winning designers won with a game "
    "first listed in their debut year on the lists"
)
print(
    f"- {num_one_and_done} of {num_winners} winning designers never had another game listed"
)

# %%
# Longest waits from first listing to first win
winning_careers.with_columns(wait=pl.col("first_win") - pl.col("first")).filter(
    pl.col("wait") >= 10
).sort("wait", "first_win", descending=[True, False]).select(
    "designer_name", "first", "first_win", "wait", "games_before_first_win", "num_games"
)

# %% [markdown]
# ## Honourable mentions
#
# The best designers who never won the main award, ranked by games on the shortlist
# (incl special awards), then by listed games.

# %%
honourable_mentions = (
    counts.filter(pl.col("winner_total") == 0)
    .with_columns(
        shortlist_total=pl.col("sonderpreis_total") + pl.col("nominated_total")
    )
    .sort(
        ["shortlist_total", "total", "best_rating"],
        descending=True,
        nulls_last=True,
    )
)
honourable_mentions.select(
    "bgg_id",
    "name",
    "sonderpreis_total",
    "nominated_spiel",
    "nominated_kenner",
    "nominated_kinder",
    "shortlist_total",
    "total",
    "best_rating",
).head(20)
