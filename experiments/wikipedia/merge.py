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
import logging
import sys
from datetime import timezone
from itertools import groupby
from pathlib import Path
from tempfile import TemporaryDirectory
from pytility import parse_date
from tqdm import tqdm
from board_game_scraper.merge import merge_data, _spark_session

LOGGER = logging.getLogger(__name__)

# %load_ext nb_black
# %load_ext lab_black

# %%
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s",
)

# %%
spark = _spark_session(log_level="WARN")

# %%
wiki_stats = merge_data(
    in_paths="/Users/markus/Recommend.Games/board-game-scraper/feeds/wiki_stats/GameItem/2021-11-05T11-13-58-riemann.jl",
    keys=("url", "published_at"),
    key_types=("str", "date"),
    latest="scraped_at",
    latest_types="date",
    latest_required=True,
    fieldnames=("url", "published_at", "page_views", "scraped_at"),
    log_level="WARN",
)

# %%
wiki_bgg = spark.read.csv(
    path="/Users/markus/Recommend.Games/recommend-games-blog/experiments/wikipedia/wiki_bgg_links.csv",
    header=True,
    inferSchema=True,
).withColumnRenamed("wikipedia_url", "url")

# %%
agg_lang = (
    wiki_stats.join(wiki_bgg, on="url", how="inner")
    .groupBy("published_at", "bgg_id", "lang")
    .sum("page_views")
    .withColumnRenamed("sum(page_views)", "page_views")
    .cache()
)

# %%
all_views = (
    agg_lang.groupBy("published_at", "bgg_id")
    .sum("page_views")
    .withColumnRenamed("sum(page_views)", "_all")
)

# %%
lang_views = agg_lang.groupBy("published_at", "bgg_id").pivot("lang").sum("page_views")

# %%
full_df = lang_views.join(all_views, on=["published_at", "bgg_id"], how="inner").sort(
    "published_at", "bgg_id"
)


# %%
def all_rows(path_dir, glob="part-*"):
    path_dir = Path(path_dir).resolve()
    for path_file in sorted(path_dir.glob(glob)):
        with path_file.open() as lines:
            yield from map(json.loads, lines)


# %%
out_dir = Path().resolve() / "stats" / "raw"

with TemporaryDirectory() as temp_dir:
    temp_dir = Path(temp_dir).resolve() / "out"

    full_df.write.json(path=str(temp_dir), ignoreNullFields=True)

    for published_at, group in groupby(
        tqdm(all_rows(temp_dir)),
        key=lambda row: row.pop("published_at"),
    ):
        published_at = parse_date(published_at, tzinfo=timezone.utc)
        out_path = (
            out_dir
            / published_at.strftime("%Y")
            / published_at.strftime("%m")
            / published_at.strftime("%Y%m%d-%H%M%S.jl")
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w") as out_file:
            for row in group:
                json.dump(row, out_file)
                out_file.write("\n")
