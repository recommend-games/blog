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
import json
from pathlib import Path
import jupyter_black
import polars as pl
import requests
from bokeh.io import output_notebook, show
from bokeh.models import GeoJSONDataSource, GroupFilter, CDSView
from bokeh.palettes import Plasma256
from bokeh.plotting import figure
from bokeh.transform import log_cmap
from rankings_by_country.countries import get_flag_emoji

jupyter_black.load()

output_notebook()

PROJECT_DIR = Path(".").resolve()
BASE_DIR = PROJECT_DIR.parent.parent
DATA_DIR = BASE_DIR.parent / "board-game-data"
PROJECT_DIR, BASE_DIR, DATA_DIR

# %%
game_data = pl.scan_csv(DATA_DIR / "scraped" / "bgg_GameItem.csv").select(
    "bgg_id",
    "name",
    "year",
)
ranking_data = pl.scan_csv("rankings/*.csv")
country_stats = (
    ranking_data.group_by("country_code")
    .agg(num_games=pl.len(), total_ratings=pl.col("num_ratings").sum())
    .with_columns(flag=pl.col("country_code").map_elements(get_flag_emoji))
)
top_games = (
    ranking_data.sort("country_code", "rank")
    .filter(pl.int_range(0, pl.len()).over("country_code") < 1)
    .drop("rank")
    .join(game_data, on="bgg_id", how="inner")
)
data = (
    country_stats.join(top_games, on="country_code", how="inner")
    .sort("total_ratings", descending=True)
    .collect()
)
data.shape

# %%
data.head(10)

# %%
response = requests.get(
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
)
response.raise_for_status()
geo_json = response.json()

# %%
for feature in geo_json["features"]:
    properties = feature["properties"]
    country_code = properties["ISO_A2"].lower()
    try:
        row = data.row(by_predicate=pl.col("country_code") == country_code, named=True)
    except pl.exceptions.NoRowsReturnedError:
        properties["flag"] = get_flag_emoji(properties["ISO_A2"])
        continue
    properties.update(row)

# %%
geo_source = GeoJSONDataSource(geojson=json.dumps(geo_json))
view = CDSView(filter=~GroupFilter(column_name="ISO_A2", group="AQ"))

# %%
plot = figure(
    title="World of board games",
    tooltips=[
        ("Country", "@flag @ADMIN (@ISO_A2)"),
        ("#1 game", "@name (@year)"),
        ("Total ratings", "@total_ratings"),
    ],
    aspect_ratio=1.5,
)

plot.patches(
    "xs",
    "ys",
    source=geo_source,
    view=view,
    line_color="black",
    line_width=0.5,
    fill_alpha=1,
    fill_color=log_cmap(
        "total_ratings",
        palette=Plasma256,
        low=data["total_ratings"].min(),
        high=data["total_ratings"].max(),
        nan_color="white",
    ),
)

plot.axis.visible = False
plot.grid.visible = False

show(plot)
