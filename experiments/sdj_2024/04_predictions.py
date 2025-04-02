# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json
import warnings
from functools import reduce
from itertools import islice
from operator import add
from pathlib import Path
import joblib
import jupyter_black
import numpy as np
import pandas as pd
from bg_utils import transform, recommend_games
from pytility import clear_list
from tqdm import tqdm
from yaml import safe_dump, safe_load

jupyter_black.load()

pd.options.display.max_columns = 100
pd.options.display.max_rows = 500
pd.options.display.float_format = "{:.6g}".format

warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

# %%
reviews = pd.read_csv("reviews.csv", index_col="bgg_id")
reviews.drop(columns="name", inplace=True)
reviews.dropna(axis=1, how="all", inplace=True)
reviews.shape

# %%
include = clear_list(
    pd.concat(
        [pd.read_csv("include.csv").bgg_id, reviews.reset_index().bgg_id],
        ignore_index=True,
    )
)
exclude = clear_list(pd.read_csv("exclude.csv").bgg_id)
len(include), len(exclude)

# %%
r_g_rankings_dir = (
    Path() / ".." / ".." / ".." / "board-game-data" / "rankings" / "bgg" / "r_g"
).resolve()
r_g_rankings_file = max(r_g_rankings_dir.rglob("*.csv"))
r_g_rankings_file

# %%
r_g_rankings = pd.read_csv(r_g_rankings_file, index_col="bgg_id")
r_g_rankings.shape

# %%
params = {
    "user": "S_d_J",
    "year__gte": 2023,
    "year__lte": 2024,
    "num_votes__gte": 1,
    "kennerspiel_score__gte": 0.0,
    "include": ",".join(map(str, include)),
    "exclude": ",".join(map(str, exclude)),
    "exclude_clusters": False,
    "exclude_known": False,
    "exclude_owned": False,
    "base_url": "https://recommend.games",
}

max_results = 10_000
candidates = list(
    tqdm(
        iterable=recommend_games(max_results=max_results, **params),
        total=max_results,
    )
)

for game in candidates[:10]:
    print(
        f"{game['name'].upper()} by {', '.join(game['designer_name'])} ({game['bgg_id']})"
    )

# %%
df = pd.DataFrame.from_records(candidates, index="bgg_id")
df["kennerspiel"] = df["kennerspiel_score"] >= 0.5
df = df.join(r_g_rankings["score"].rename("r_g_score"), how="inner")
df.dropna(
    subset=["num_votes", "rec_rating", "kennerspiel_score", "r_g_score"],
    inplace=True,
)
df.shape

# %%
data = transform(
    data=df,
    list_columns=("game_type", "category", "mechanic"),
    min_df=1,
)
data.shape

# %%
with open("features.json") as f:
    features = json.load(f)
len(features)

# %%
for feature in features:
    if feature not in data:
        print(feature)
        data[feature] = False

# %%
model = joblib.load("lr.joblib")
model

# %%
x = data[features]
x = x.fillna(x.mean())
data["sdj_prob"] = model.predict_proba(x)[:, 1]
data.shape

# %%
rank_features = [
    "num_votes",
    "rec_rating",
    "sdj_prob",
    "r_g_score",
]
rank_columns = [f"{f}_rank" for f in rank_features]
data[rank_columns] = data.groupby("kennerspiel")[rank_features].rank(
    method="max",
    na_option="top",
    ascending=True,
    pct=True,
)
data.shape

# %%
data["jury_reviews"] = reviews.mean(axis=1)
data["jury_reviews"] = data["jury_reviews"].fillna(5.5)
data.shape

# %%
scale_max_features = [
    "num_votes",
    "rec_rating",
]
scale_max_columns = [f"{f}_scale_max" for f in scale_max_features]
data[scale_max_columns] = data[scale_max_features] / data[scale_max_features].max()
data.shape

# %%
scale_10_features = [
    "jury_reviews",
]
scale_10_columns = [f"{f}_scale_10" for f in scale_10_features]
data[scale_10_columns] = data[scale_10_features] / 10
data.shape

# %%
qt = joblib.load("qt.joblib")
qt

# %%
quantile_features = [
    "rec_rating",
    "jury_reviews",
]
for col in quantile_features:
    data[f"{col}_quantile"] = qt.transform(data[[col]].values)[:, 0]
data.shape

# %%
sdj_score_weights = {
    "num_votes": 0,
    "num_votes_rank": 0,
    "num_votes_scale_max": 0,
    "r_g_score": 0,
    "r_g_score_rank": 0,
    "rec_rating": 0,
    "rec_rating_rank": 0,
    "rec_rating_scale_max": 1,
    "rec_rating_quantile": 2,
    "jury_reviews": 0,
    "jury_reviews_scale_10": 0,
    "jury_reviews_quantile": 4,
    "sdj_prob": 1,
    "sdj_prob_rank": 0,
}

# %%
print("Calculate SdJ scores according to these weights:")
total_weight = sum(sdj_score_weights.values())
for column, weight in sorted(sdj_score_weights.items(), key=lambda x: (-x[1], x[0])):
    if weight > 0:
        print(f"{100 * weight / total_weight:4.1f}%: {column}")

# %%
data["sdj_score"] = (
    reduce(add, (weight * data[column] for column, weight in sdj_score_weights.items()))
    / total_weight
)
data["sdj_rank"] = (
    data.groupby("kennerspiel")["sdj_score"]
    .rank(
        ascending=False,
        method="min",
        na_option="bottom",
    )
    .astype(int)
)
data.shape

# %%
results = data[
    [
        "name",
        "year",
        "sdj_score",
        "sdj_rank",
        "num_votes",
        "jury_reviews",
        "avg_rating",
        "bayes_rating",
        "rec_rating",
        "rec_rating_rank",
        "sdj_prob",
        "sdj_prob_rank",
        "r_g_score",
        "r_g_score_rank",
        "kennerspiel",
        "kennerspiel_score",
        "min_age",
        "min_time",
        "max_time",
        "complexity",
    ]
].copy()
results[["min_players", "max_players"]] = df[["min_players", "max_players"]]
results["url"] = [
    f"<a href='https://recommend.games/#/game/{bgg_id}'>{name}</a>"
    for bgg_id, name in results.name.items()
]
results.sort_values("sdj_score", ascending=False, inplace=True)
results.shape

# %%
sdj = results[~results["kennerspiel"]].copy()
sdj["name_raw"] = sdj["name"]
sdj["name"] = sdj["url"]
sdj.drop(columns="url", inplace=True)
kdj = results[results["kennerspiel"]].copy()
kdj["name_raw"] = kdj["name"]
kdj["name"] = kdj["url"]
kdj.drop(columns="url", inplace=True)
results.shape, sdj.shape, kdj.shape

# %%
results.drop(columns="url", inplace=True)
results.sort_values(["kennerspiel", "sdj_rank"], inplace=True)
results.to_csv("predictions.csv", header=True, float_format="%.5g")

# %% [markdown]
# # SdJ candidates

# %%
sdj[:100].style

# %% [markdown]
# # KdJ candidates

# %%
kdj[:100].style

# %% [markdown]
# # Outputs

# %%
notes_file = Path("notes.yaml").resolve()

if not notes_file.exists():
    num = 50
    top_candidates = pd.concat((sdj[:num], kdj[:num]))

    dummy_notes = {
        bgg_id: {
            "name": game.name_raw,
            "text": f"{{{{% game {bgg_id} %}}}}{game.name_raw}{{{{% /game %}}}}",
            "description": "",
        }
        for bgg_id, game in top_candidates.iterrows()
    }

    with notes_file.open("w", encoding="utf-8") as f:
        safe_dump(dummy_notes, f)

# %%
COMPLEXITIES = (None, "light", "medium light", "medium", "medium heavy", "heavy")

with notes_file.open(encoding="utf-8") as f:
    NOTES = safe_load(f)


def game_str(game, bgg_id=None, position=None, notes=NOTES):
    bgg_id = game["bgg_id"] if bgg_id is None else bgg_id
    position_str = f"#{int(position)}: " if position is not None else ""
    name = game.get("name_raw") or game.get("name")
    min_players = int(min_players) if (min_players := game["min_players"]) else None
    max_players = int(max_players) if (max_players := game["max_players"]) else None
    player_count = (
        f"{min_players:d}–{max_players:d} players"
        if max_players > min_players
        else f"{min_players:d} players" if min_players > 1 else "Solo game"
    )
    min_time = int(min_time) if (min_time := game["min_time"]) else None
    max_time = int(max_time) if (max_time := game["max_time"]) else None
    play_time = (
        f"{min_time:d}–{max_time:d} minutes"
        if max_time > min_time
        else f"{min_time:d} minutes"
    )
    player_age = (
        f"{int(min_age)}+ years"
        if (min_age := game["min_age"]) and pd.notna(min_age)
        else ""
    )
    complexity = (
        complexity
        if (complexity := game["complexity"]) and np.isfinite(complexity)
        else 0
    )
    complexity_str = (
        f"{COMPLEXITIES[round(complexity)]} ({complexity:.1f}), "
        if complexity > 0
        else ""
    )
    kennerspiel_score = (
        round(100 * kennerspiel_score)
        if (kennerspiel_score := game["kennerspiel_score"])
        else None
    )
    kennerspiel = (
        ""
        if kennerspiel_score is None
        else (
            f"{kennerspiel_score}% {{{{% kdj %}}}}Kennerspiel{{{{% /kdj %}}}}"
            if kennerspiel_score >= 50
            else f"{100 - kennerspiel_score}% {{{{% sdj %}}}}Spiel{{{{% /sdj %}}}}"
        )
    )
    description = (
        note.get("description") if notes and (note := notes.get(bgg_id)) else None
    )
    description_str = f"*{description}*\n\n" if description else ""
    text = (
        (note.get("text") or "")
        if notes and (note := notes.get(bgg_id))
        else f"{{{{% game {bgg_id} %}}}}{name}{{{{% /game %}}}}"
    )

    # TODO data for each game: designers, player count, play time, age, complexity, Kennerspiel score

    return f"""## {position_str}{{{{% game {bgg_id} %}}}}{name}{{{{% /game %}}}}

*{player_count}, {play_time}, {player_age}, {complexity_str}{kennerspiel}*

{{{{< img src="{bgg_id}" size="x300" alt="{name}" >}}}}

{description_str}{text}"""


# %%
with open("candidates.md", "w") as f:
    print("# Spiel des Jahres\n\n", file=f)
    for pos, (bgg_id, game) in enumerate(sdj[:12].iterrows()):
        print(game_str(game, bgg_id, pos + 1), file=f)
        print("\n", file=f)

    print("# Kennerspiel des Jahres\n\n", file=f)
    for pos, (bgg_id, game) in enumerate(kdj[:12].iterrows()):
        print(game_str(game, bgg_id, pos + 1), file=f)
        print("\n", file=f)
