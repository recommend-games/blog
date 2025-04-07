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
import os
import requests

jupyter_black.load()

# %%
API_HEADER = {"X-Requested-By": os.getenv("SNOOKER_API_HEADER")}

# %%
events_response = requests.get(
    url="https://api.snooker.org/",
    params={"t": 5, "s": 1974, "tr": "main"},
    headers=API_HEADER,
)

# %%
events = events_response.json()
len(events)

# %%
for event in events:
    event_id = event["ID"]
    print(event_id, event["Name"], event["StartDate"])
    print(event)
    matches_response = requests.get(
        url="https://api.snooker.org/",
        params={"t": 6, "e": event_id},
        headers=API_HEADER,
    )
    matches = matches_response.json()
    print(len(matches))
    break

# %%
matches[0]

# %%
player_ids = {match["Player1ID"] for match in matches} | {
    match["Player2ID"] for match in matches
}
len(player_ids)

# %%
for player_id in player_ids:
    print(player_id)
    player_response = requests.get(
        url="https://api.snooker.org/",
        params={"p": player_id},
        headers=API_HEADER,
    )
    player = player_response.json()
    print(player)
