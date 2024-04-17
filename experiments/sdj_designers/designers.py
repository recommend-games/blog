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
import jupyter_black
import pandas as pd
from pytility import arg_to_iter, clear_list, parse_int

jupyter_black.load()

SEED = 23

pd.options.display.max_columns = 100
pd.options.display.max_rows = 1000
pd.options.display.float_format = "{:.6g}".format

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
    "../sdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
sdj["award"] = "spiel"

kennersdj = pd.read_csv(
    "../ksdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
kennersdj["award"] = "kenner"

kindersdj = pd.read_csv(
    "../kindersdj.csv",
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
awards.shape

# %%
games = game_data.join(awards)
games.shape

# %%
games.sample(5, random_state=SEED).T


# %%
def parse_ids(value):
    if isinstance(value, str):
        return parse_ids(value.split(","))
    return clear_list(map(parse_int, arg_to_iter(value)))


designer_awards = games["designer"].apply(parse_ids).explode().dropna().astype(int)
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
]
data = games[columns].dropna(subset=["award"]).join(designer_awards)
data.shape

# %%
winner_mask = data["winner"]
nominated_mask = ~winner_mask & data["nominated"]
recommended_mask = ~winner_mask & ~nominated_mask & data["recommended"]
winner = data[winner_mask]
nominated = data[nominated_mask]
recommended = data[recommended_mask]
# TODO add special awards
winner.shape, nominated.shape, recommended.shape


# %%
def count_awards(data, label):
    count = data.groupby(["designer", "award"]).size().unstack(fill_value=0)
    count["total"] = count.sum(axis=1)
    count.columns = pd.MultiIndex.from_product([[label], count.columns])
    return count


# %%
winner_count = count_awards(winner, "winner")
nominated_count = count_awards(nominated, "nominated")
recommended_count = count_awards(recommended, "recommended")
counts = (
    winner_count.join(nominated_count, how="outer")
    .join(recommended_count, how="outer")
    .fillna(0)
)
counts.insert(0, ("designer", "name"), designers)
counts[("all", "total")] = (
    counts[("winner", "total")]
    + counts[("nominated", "total")]
    + counts[("recommended", "total")]
)
counts.sort_values(
    [
        ("winner", "total"),
        ("nominated", "total"),
        ("recommended", "total"),
        ("winner", "spiel"),
        ("winner", "kenner"),
        ("winner", "kinder"),
        ("nominated", "spiel"),
        ("nominated", "kenner"),
        ("nominated", "kinder"),
        ("recommended", "spiel"),
        ("recommended", "kenner"),
        ("recommended", "kinder"),
        ("all", "total"),
    ],
    ascending=False,
    inplace=True,
)
# TODO add highest rated game as final (?) tie breaker
counts

# %%
counts.to_csv("designers.csv", float_format="%d")

# %%
print("| Designer | Spiel | Kennerspiel | Kinderspiel |")
print("|:---------|:-----:|:-----------:|:-----------:|")
for bgg_id, row in counts.iterrows():
    cells = [
        "",
        f" [{row[('designer', 'name')]}](https://recommend.games/#/?designer={bgg_id:.0f}) ",
    ]
    for award in ("spiel", "kenner", "kinder"):
        winner = row[("winner", award)]
        nominated = row[("nominated", award)]
        recommended = row[("recommended", award)]
        cells.append(f" {winner:.0f} / {nominated:.0f} / {recommended:.0f} ")
    cells.append("")
    print("|".join(cells))
