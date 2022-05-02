# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json
import pandas as pd
import pathlib

# %load_ext nb_black
# %load_ext lab_black

# %%
responses_dir = (
    pathlib.Path()
    / ".."
    / ".."
    / ".."
    / "board-game-scraper"
    / "feeds"
    / "r_g_responses"
).resolve()
responses_dir


# %%
def parse_dir(path_dir):
    for path_file in path_dir.rglob("*.jl"):
        with path_file.open() as file:
            yield from map(json.loads, file)


# %%
responses = pd.DataFrame.from_records(
    data=parse_dir(responses_dir),
    columns=["timestamp", "response"],
)
responses.shape

# %%
responses["timestamp"] = pd.to_datetime(responses.timestamp)
responses.set_index("timestamp", inplace=True)
responses["points"] = responses["response"].apply(
    lambda l: list(range(25, 25 - len(l), -1))
)
responses.shape

# %%
points = responses.explode(["response", "points"])
points.rename(columns={"response": "bgg_id"}, inplace=True)
points.shape

# %%
daily = (
    points.groupby("bgg_id")
    .resample("D")
    .points.sum()
    .swaplevel()
    .reset_index()
    .sort_values(["timestamp", "points", "bgg_id"], ascending=[True, False, True])
)
daily.shape
