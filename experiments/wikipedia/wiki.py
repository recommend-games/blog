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
import re
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
from pytility import arg_to_iter, parse_date

# %load_ext nb_black
# %load_ext lab_black

# %%
data_path = Path("../../../board-game-data").resolve()
bgg_path = data_path / "scraped" / "bgg_GameItem.csv"
wiki_path = data_path / "scraped" / "wikidata_GameItem.jl"

# %%
games_path = Path(bgg_path).resolve()
games = pd.read_csv(
    games_path,
    index_col="bgg_id",
    low_memory=False,
)
games.shape

# %%
domain_regex = re.compile(r"^([a-z]{2,3})\.wikipedia\.org$")
path_regex = re.compile(r"^/wiki/(.+)$")


# %%
def is_wiki_url(url):
    url = urlparse(url)
    return bool(url and domain_regex.match(url.hostname) and path_regex.match(url.path))


# %%
def load_links(path):
    path = Path(path).resolve()
    with path.open() as file:
        for line in file:
            game = json.loads(line)
            bgg_id = game.get("bgg_id")
            wiki_links = [
                u for u in arg_to_iter(game.get("external_link")) if is_wiki_url(u)
            ]
            if bgg_id and wiki_links:
                yield bgg_id, wiki_links


# %%
links = defaultdict(set)
for bgg_id, wiki_links in load_links(wiki_path):
    links[bgg_id].update(wiki_links)
len(links)

# %%
games[~games.index.isin(links)].sort_values("rank").head(50)
