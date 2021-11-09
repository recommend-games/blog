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
import json
import math
from datetime import datetime, timedelta, timezone
from itertools import groupby
from pathlib import Path
import pandas as pd
from pytility import flatten, parse_date

# %load_ext nb_black
# %load_ext lab_black

# %%
raw_dir = Path().resolve() / "stats" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)
out_dir = Path().resolve() / "stats" / "weekly"
out_dir.mkdir(parents=True, exist_ok=True)


# %%
def parse_rows(paths):
    for path in paths:
        with path.open() as lines:
            yield from map(json.loads, lines)


# %%
for week, group in groupby(
    sorted(raw_dir.rglob("*.jl")),
    key=lambda path: parse_date(path.stem, tzinfo=timezone.utc).strftime("%G-%V"),
):
    date = datetime.strptime(f"{week}-1", "%G-%V-%u") + timedelta(days=7)
    print(date)
    data = pd.DataFrame.from_records(data=parse_rows(group)).rename(
        columns={"_all": "page_views"}
    )
    grouped = data.groupby("bgg_id").sum().replace(0, math.nan)
    ranking = grouped.rank(
        method="first",
        ascending=False,
        na_option="keep",
    )
    result = (
        grouped.join(ranking, rsuffix="_rank")
        .rename(columns={"page_views_rank": "rank"})
        .sort_values(["rank", "en_rank", "de_rank"])
    )
    lang_columns = list(
        flatten(
            (lang, f"{lang}_rank")
            for lang in grouped.columns[grouped.columns != "page_views"].sort_values()
        )
    )
    result.reset_index().to_csv(
        out_dir / date.strftime("%Y%m%d-%H%M%S.csv"),
        float_format="%.0f",
        columns=["rank", "bgg_id", "page_views"] + lang_columns,
    )
    print(result.shape)
