# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import csv
import re

from pathlib import Path

import pandas as pd
import requests

from pytility import arg_to_iter, parse_int

# %load_ext nb_black
# %load_ext lab_black

# %%
def games_in_articles(paths):
    seen = set()
    for path in arg_to_iter(paths):
        path = Path(path).resolve()
        with open(path) as file:
            for line in file:
                for match in regex.finditer(line):
                    bgg_id = parse_int(match.group(1))
                    name = match.group(2)
                    if bgg_id and bgg_id not in seen:
                        seen.add(bgg_id)
                        yield bgg_id, name, path


# %%
regex = re.compile(r"\{\{%\s*game\s*(\d+)\s*%\}\}([^{]+)\{\{%\s*/game\s*%\}\}")

# %%
directory = Path("../../content/posts/").resolve()
out_path = Path("2020_articles.csv").resolve()

# %%
paths = directory.glob("sdj*/*.md")

# %%
with out_path.open("w", newline="") as out_file:
    writer = csv.writer(out_file)
    writer.writerow(("bgg_id", "name", "comment"))
    for bgg_id, name, path in games_in_articles(paths):
        comment = f"From article <{path}>"
        writer.writerow((bgg_id, name, comment))

# %%
include = pd.read_csv("include.csv", index_col="bgg_id")
exclude = pd.read_csv("exclude.csv", index_col="bgg_id")
include.shape, exclude.shape

# %%
url = "http://localhost:8000/api/games/recommend/"
params = {
    "user": "S_d_J",
    "year__gte": 2020,
    "year__lte": 2021,
    "complexity__lte": 2,
    "max_players__gte": 4,
    "min_players__lte": 3,
    "max_time__lte": 60,
    "min_age__lte": 14,
    "include": ",".join(map(str, include.index)),
    "exclude": ",".join(map(str, exclude.index)),
}

# %%
response = requests.get(url, params)

# %%
candidates = pd.DataFrame.from_records(response.json()["results"], index="bgg_id")
candidates.shape

# %%
candidates[
    [
        "name",
        "year",
        "num_votes",
        "avg_rating",
        "bayes_rating",
        "bgg_rank",
        "rec_rating",
        "complexity",
        "cooperative",
    ]
]
