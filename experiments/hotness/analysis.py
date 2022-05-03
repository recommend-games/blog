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
daily = points.groupby("bgg_id").resample("D").points.sum().reset_index()
daily["date"] = daily.timestamp.dt.date
daily.drop(columns="timestamp", inplace=True)
daily.sort_values(
    by=["date", "points", "bgg_id"],
    ascending=[True, False, True],
    inplace=True,
)
daily.shape

# %%
daily.sample(10)


# %%
def process_days(daily, weight_today=0.5):
    yesterday = None

    for date, data in daily.groupby("date"):
        today = pd.Series(index=data.bgg_id, data=data.points)

        if yesterday is None:
            yield date, today.rank(method="min", ascending=False)
            yesterday = today

        else:
            temp = pd.DataFrame({"yesterday": yesterday, "today": today})
            temp.fillna(value=0, inplace=True)
            values = (1 - weight_today) * temp.yesterday + weight_today * temp.today
            yield date, values.rank(method="min", ascending=False)
            yesterday = values


# %%
for date, p in process_days(daily):
    print(date)
    print(p.sort_values()[:5])
