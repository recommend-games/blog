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
from datetime import datetime, timedelta
from pathlib import Path
import jupyter_black
import pandas as pd
from pytility import parse_date
from aggregated_hotness.hotness import aggregate_hotness

jupyter_black.load()


# %%
def hot_games(
    games_path=Path("../../../board-game-data/scraped/bgg_GameItem.csv").resolve(),
    hot_dir=Path("../../../board-game-data/rankings/bgg/hotness/").resolve(),
    start_date=datetime.utcnow() - timedelta(days=60),
    end_date=datetime.utcnow(),
    top=30,
):
    games = pd.read_csv(
        games_path,
        index_col="bgg_id",
        low_memory=False,
    )
    hotness = aggregate_hotness(
        path_dir=hot_dir,
        start_date=start_date,
        end_date=end_date,
        top=top,
    ).rename("hotness")
    return (
        games[["name"]]
        .join(hotness, how="right")
        .sort_values("hotness", ascending=False)
    )


# %%
results = hot_games(
    start_date=parse_date("2024-02-01T00:00Z"),
    end_date=parse_date("2024-04-01T00:00Z"),
    top=30,
)
results.head(50)
