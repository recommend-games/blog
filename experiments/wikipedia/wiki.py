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
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
from pytility import arg_to_iter

# %load_ext nb_black
# %load_ext lab_black

# %%
data_path = Path("../../../board-game-data").resolve()
bgg_path = data_path / "scraped" / "bgg_GameItem.csv"
wiki_path = data_path / "scraped" / "wikidata_GameItem.jl"
stats_path = (
    Path("../../../board-game-scraper").resolve()
    / "feeds"
    / "wiki_stats"
    / "GameItem"
    / "2021-11-07-merged.jl"
)

# %%
games_path = Path(bgg_path).resolve()
games = pd.read_csv(
    games_path,
    index_col="bgg_id",
    low_memory=False,
)
games.shape

# %%
# TODO this does not capture simple.wikipedia.org
# TODO check all Wikipedias (https://en.wikipedia.org/wiki/List_of_Wikipedias)
domain_regex = re.compile(r"^([a-z-]+)\.wikipedia\.org$")
path_regex = re.compile(r"^/wiki/(.+)$")


# %%
def is_wiki_url(url):
    url = urlparse(url)
    return bool(url and domain_regex.match(url.hostname) and path_regex.match(url.path))


def wiki_lang(url):
    url = urlparse(url)
    domain_match = domain_regex.match(url.hostname)
    return (
        domain_match.group(1).lower()
        if url and domain_match and domain_match.group(1)
        else None
    )


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

# %%
for bgg_id, wiki_links in links.items():
    c = Counter(wiki_lang(wiki_link) for wiki_link in wiki_links)
    if c.most_common(1)[0][1] > 1:
        print(bgg_id)
        print("\n".join(sorted(wiki_links)))
        print(c)
        print()

# %%
wiki_bgg = pd.DataFrame.from_records(
    data=((url, bgg_id) for bgg_id, urls in links.items() for url in urls),
    columns=["wikipedia_url", "bgg_id"],
    index="wikipedia_url",
)
wiki_bgg["lang"] = wiki_bgg.index.map(wiki_lang)
wiki_bgg.shape

# %%
wiki_bgg.reset_index().sort_values(["bgg_id", "lang", "wikipedia_url"]).to_csv(
    path_or_buf=Path().resolve() / "wiki_bgg_links.csv",
    index=False,
)


# %%
def agg_monthly_views(path):
    path = Path(path).resolve()
    with path.open() as file:
        games = map(json.loads, file)
        for (url, month), group in groupby(
            games, key=lambda game: (game.get("url"), game.get("published_at")[:7])
        ):
            views = sum(game.get("page_views") for game in group)
            yield url, month, views


# %%
page_views = pd.DataFrame.from_records(
    data=agg_monthly_views(stats_path),
    columns=["wikipedia_url", "month", "page_views"],
    index=["wikipedia_url", "month"],
).join(wiki_bgg, on="wikipedia_url", how="left")
page_views.dropna(inplace=True)
page_views["bgg_id"] = page_views["bgg_id"].astype(int)
page_views.reset_index(inplace=True)
page_views.shape

# %%
by_month = (
    page_views.groupby(["month", "bgg_id"])["page_views"]
    .sum()
    .reset_index()
    .join(games["name"], on="bgg_id", how="left")
    .sort_values(
        by=["month", "page_views"],
        ascending=[True, False],
    )
)
by_month["rank"] = (
    by_month.groupby("month")["page_views"]
    .rank(method="min", ascending=False)
    .astype(int)
)

# %%
by_month[by_month["month"] == "2021-10"].head(50)

# %%
out_dir = Path().resolve() / "stats"
out_dir.mkdir(parents=True, exist_ok=True)

# %%
for month, group in by_month.groupby("month"):
    print(month, group.shape)
    out_path = out_dir / f"{month}.csv"
    group[["rank", "bgg_id", "page_views"]].to_csv(out_path, index=False)
