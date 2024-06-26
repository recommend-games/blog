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

# %% [markdown]
# # Spiel des Jahres winning designers

# %%
import jupyter_black
import pandas as pd
from more_itertools import powerset
from pytility import arg_to_iter, clear_list, parse_int

jupyter_black.load()

SEED = 23

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100
pd.options.display.float_format = "{:.6g}".format

# %% [markdown]
# ## Basic data

# %%
game_data = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
game_data.shape

# %%
designers = pd.read_csv(
    "../../../board-game-data/scraped/bgg_Person.csv",
    index_col="bgg_id",
    low_memory=False,
)["name"]
designers.shape

# %%
sdj = pd.read_csv(
    "sdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
sdj["award"] = "spiel"

kennersdj = pd.read_csv(
    "ksdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
kennersdj["award"] = "kenner"

kindersdj = pd.read_csv(
    "kindersdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
kindersdj["award"] = "kinder"

awards = pd.concat((sdj, kennersdj, kindersdj))
awards = awards.groupby("bgg_id").agg(
    {
        "jahrgang": "max",
        "winner": "max",
        "nominated": "max",
        "recommended": "max",
        "sonderpreis": lambda group: ", ".join(
            sorted(set(s for s in group if isinstance(s, str)))
        ),
        "award": lambda group: ", ".join(sorted(set(group))),
    }
)
# Just one Exit and Sherlock game
awards.drop(
    index=[203416, 203417, 247436, 250779],
    inplace=True,
)
# The early "Beautiful Game" special awards clutter the results
awards.loc[
    awards["sonderpreis"] == "Beautiful Game",
    ["recommended", "sonderpreis"],
] = (True, "")
awards.shape

# %%
games_summary = (
    awards.assign(sonderpreis=awards["sonderpreis"].str.len() > 0)
    .groupby("award")[["winner", "nominated", "recommended", "sonderpreis"]]
    .sum()
)
print(games_summary.to_markdown())

# %%
games = game_data.join(awards, how="inner")
games.shape


# %% [markdown]
# ## Counting awards

# %%
def parse_ids(value):
    if isinstance(value, str):
        return parse_ids(value.split(","))
    return clear_list(map(parse_int, arg_to_iter(value)))


designer_awards = games["designer"].apply(parse_ids).explode().dropna().astype("int64")
designer_awards.shape

# %%
columns = [
    "name",
    "year",
    "award",
    "winner",
    "nominated",
    "recommended",
    "sonderpreis",
    "bayes_rating",
]
data = games[columns].dropna(subset=["award"]).join(designer_awards).copy()
data["designer"] = data["designer"].fillna(3).astype("int64")
data["year"] = data["year"].fillna(0).astype("int64")
data.shape

# %%
data.to_csv("games.csv")

# %%
best_rating = data.groupby("designer").agg({"bayes_rating": "max"})
best_rating.columns = pd.MultiIndex.from_arrays([["all"], ["best_rating"]])
best_rating.shape

# %%
winner_mask = data["winner"]
sonderpreis_mask = ~winner_mask & (data["sonderpreis"].str.len() > 0)
nominated_mask = ~winner_mask & ~sonderpreis_mask & data["nominated"]
recommended_mask = (
    ~winner_mask & ~sonderpreis_mask & ~nominated_mask & data["recommended"]
)
winner = data[winner_mask]
sonderpreis = data[sonderpreis_mask]
nominated = data[nominated_mask]
recommended = data[recommended_mask]
winner.shape, sonderpreis.shape, nominated.shape, recommended.shape


# %%
def count_awards(data, label):
    count = data.groupby(["designer", "award"]).size().unstack(fill_value=0)
    count["total"] = count.sum(axis=1)
    count.columns = pd.MultiIndex.from_product([[label], count.columns])
    return count


# %%
# Individual counts
winner_count = count_awards(winner, "winner")
nominated_count = count_awards(nominated, "nominated")
recommended_count = count_awards(recommended, "recommended")
sonderpreis_count = count_awards(sonderpreis, "sonderpreis")

# Join the counts
counts = (
    winner_count.join(nominated_count, how="outer")
    .join(recommended_count, how="outer")
    .join(sonderpreis_count, how="outer")
    .join(best_rating, how="left")
    .fillna(0)
)

# "Uncredited" designs don't really make sense in our analysis
counts.drop(index=3, inplace=True)

# Bring index and dtypes in correct format
counts.index = counts.index.astype("int64")
counts.index.name = None
count_columns = pd.MultiIndex.from_product(
    [
        ["winner", "sonderpreis", "nominated", "recommended"],
        ["spiel", "kenner", "kinder", "total"],
    ]
)
counts[count_columns] = counts[count_columns].astype("int64")

# Add some more data
counts.insert(0, ("designer", "name"), designers)
counts["all", "total"] = (
    counts[("winner", "total")]
    + counts[("nominated", "total")]
    + counts[("recommended", "total")]
    + counts[("sonderpreis", "total")]
)

# Rank and sort
counts["all", "rank"] = (
    counts[
        [
            ("winner", "total"),
            ("sonderpreis", "total"),
            ("nominated", "total"),
            ("recommended", "total"),
            ("winner", "spiel"),
            ("winner", "kenner"),
            ("winner", "kinder"),
            ("sonderpreis", "spiel"),
            ("sonderpreis", "kenner"),
            ("sonderpreis", "kinder"),
            ("nominated", "spiel"),
            ("nominated", "kenner"),
            ("nominated", "kinder"),
            ("recommended", "spiel"),
            ("recommended", "kenner"),
            ("recommended", "kinder"),
            ("all", "total"),
            ("all", "best_rating"),
        ]
    ]
    .apply(tuple, axis=1)
    .rank(method="min", ascending=False)
    .astype("int64")
)
counts.sort_values(
    [
        ("all", "rank"),
        ("designer", "name"),
    ],
    ascending=True,
    inplace=True,
)

# Done.
counts.shape

# %% [markdown]
# ## Overall results

# %%
counts.head(10)

# %%
counts.reset_index(col_level=1, names="bgg_id").to_csv("designers.csv", index=False)


# %%
def designer_table(counts):
    criterion = (counts["all", "total"] >= 5) | (
        (counts["winner", "total"] + counts["sonderpreis", "total"]) >= 2
    )
    result = "| Designer | Spiel | Kennerspiel | Kinderspiel | Total |\n"
    result += "|:---------|:-----:|:-----------:|:-----------:|:-----:|\n"
    for bgg_id, row in counts[criterion].iterrows():
        cells = [
            "",
            f" [{row['designer', 'name']}](https://recommend.games/#/?designer={bgg_id:.0f}) ",
        ]
        for award in ("spiel", "kenner", "kinder"):
            winner = row["winner", award]
            sonderpreis = row["sonderpreis", award]
            sonderpreis_str = f" ({sonderpreis:.0f})" if sonderpreis > 0 else ""
            nominated = row["nominated", award]
            recommended = row["recommended", award]
            cells.append(
                f" {winner:.0f}{sonderpreis_str} / {nominated:.0f} / {recommended:.0f} "
            )
        cells.append(f" {row['all', 'total']} ")
        cells.append("")
        result += "|".join(cells)
        result += "\n"
    return result


# %%
with open("table.md", "w") as f:
    f.write(designer_table(counts))

# %% [markdown]
# ## More statistics

# %%
awards = ("spiel", "kenner", "kinder")
awards_full_names = dict(
    zip(
        awards,
        ("Spiel des Jahres", "Kennerspiel des Jahres", "Kinderspiel des Jahres"),
    )
)

for award_set in powerset(awards):
    award_set = list(award_set)
    if not award_set:
        # skip empty set
        continue
    award_data = counts.swaplevel(axis=1)[award_set]
    num_longlist = award_data.T.groupby(level=0).any().all().sum()
    num_shortlist = (
        award_data.drop(columns=["recommended"], level=1)
        .T.groupby(level=0)
        .any()
        .all()
        .sum()
    )
    num_winner_any = (
        award_data.drop(columns=["recommended", "nominated"], level=1)
        .T.groupby(level=0)
        .any()
        .all()
        .sum()
    )
    num_winner = (
        award_data.drop(columns=["recommended", "nominated", "sonderpreis"], level=1)
        .T.groupby(level=0)
        .any()
        .all()
        .sum()
    )
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
steps = ["winner", "sonderpreis", "nominated", "recommended"]
cat_count_longlist = (
    counts.drop(columns="total", level=1)[steps].T.groupby(level=1).any().sum()
)
cat_count_shortlist = (
    counts.drop(columns="total", level=1)[steps[:3]].T.groupby(level=1).any().sum()
)
cat_count_winner_any = (
    counts.drop(columns="total", level=1)[steps[:2]].T.groupby(level=1).any().sum()
)
cat_count_winner = (
    counts.drop(columns="total", level=1)[steps[:1]].T.groupby(level=1).any().sum()
)
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
    for num, count in (
        count_list.value_counts().sort_index(ascending=False).cumsum().items()
    ):
        if num > 0:
            print(
                f"- {count} designer{'' if count == 1 else 's'} appear in {'all' if num == 3 else 'at least'} {num} categor{'y' if num == 1 else 'ies'}"
            )
    print()
    print()

# %%
awards = (
    "total",
    "spiel",
    "kenner",
    "kinder",
)
award_titles = (
    "Overall",
    "Spiel des Jahres",
    "Kennerspiel des Jahres",
    "Kinderspiel des Jahres",
)
steps = ("winner", "sonderpreis", "nominated", "recommended")
step_titles = (
    "Most wins (main award)",
    "Most wins (incl special award)",
    "Most games on the shortlist",
    "Most games on the longlist",
)
print("## Designer records")
for award, award_title in zip(awards, award_titles):
    print(f"\n\n### {award_title}\n")

    for i in range(len(steps), 0, -1):
        num_games = counts[pd.MultiIndex.from_product([steps[:i], [award]])].sum(axis=1)
        most = num_games.max()
        print(f"- {step_titles[i-1]}: {most}")
        for bgg_id, name in counts.reindex(num_games[num_games == most].index)[
            "designer", "name"
        ].items():
            print(f"  - [{name}](https://recommend.games/#/?designer={bgg_id:.0f})")

    nominated = counts[counts["winner", award] == 0].sort_values(
        ("nominated", award),
        ascending=False,
    )
    nominated_num = nominated["nominated", award].max()
    print(f"- Most games on the shortlist without win: {nominated_num}")
    for bgg_id, name in nominated[nominated["nominated", award] == nominated_num][
        "designer", "name"
    ].items():
        print(f"  - [{name}](https://recommend.games/#/?designer={bgg_id:.0f})")
