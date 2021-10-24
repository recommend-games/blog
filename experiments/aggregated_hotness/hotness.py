# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import timezone
from itertools import groupby
from pathlib import Path
import pandas as pd
import numpy as np
from pytility import parse_date

# %load_ext nb_black
# %load_ext lab_black

# %%
hot_dir = Path("../../../board-game-data/rankings/bgg/hotness/").resolve()
hot_dir


# %%
def load_hotness(path, start, end):
    for d, group in groupby(
        sorted(
            (d, p)
            for p in path.glob("*.csv")
            if start <= (d := parse_date(p.stem, tzinfo=timezone.utc)) < end
        ),
        key=lambda x: x[0].date(),
    ):
        _, p = min(group)
        s = pd.read_csv(p, index_col="bgg_id",)[
            "rank"
        ].rename(d.isoformat())
        yield s


# %%
def compute_scores(path, start, end):
    result = pd.concat(
        objs=load_hotness(path=path, start=start, end=end),
        axis=1,
    )
    for bgg_id, ranks in result.T.iteritems():
        yield bgg_id, np.exp2(1 - ranks.sort_values().head(30)).sum() * 100 / 30


# %%
aggregated_hotness = pd.Series(
    dict(
        compute_scores(
            path=hot_dir,
            start=parse_date("2021-08-01T00:00Z"),
            end=parse_date("2021-10-01T00:00Z"),
        )
    )
).sort_values(ascending=False)
aggregated_hotness.head(50)
