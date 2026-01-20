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
from bokeh.embed import json_item
from bokeh.io import output_notebook, show
from bokeh.models import (
    BooleanFilter,
    CDSView,
    GeoJSONDataSource,
    GroupFilter,
    HoverTool,
)
from bokeh.palettes import TolYlOrBr9, interp_palette
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
data = (
    pl.scan_csv("countries.csv")
    .sort(
        "total_ratings_rank",
        "ratings_per_capita_rank",
        "population_rank",
        "country_code",
        nulls_last=True,
    )
    .with_columns(
        pl.col("total_ratings") // 1_000,
        pl.col("population") / 1_000_000,
    )
    .collect()
)
data.shape

# %%
data.head(10)

# %%
data.sort("ratings_per_capita_rank", nulls_last=True).head(10)

# %%
url = "https://raw.githubusercontent.com/AshKyd/geojson-regions/main/public/countries/110m/all.geojson"
response = requests.get(url)
response.raise_for_status()
geo_json = response.json()

# %%
for feature in geo_json["features"]:
    properties = feature["properties"]
    country_code = properties["ISO_A2_EH"].lower()
    try:
        row = data.row(by_predicate=pl.col("country_code") == country_code, named=True)
        properties.update(row)
    except pl.exceptions.NoRowsReturnedError:
        properties["flag"] = get_flag_emoji(properties["ISO_A2"])

# %%
geo_source = GeoJSONDataSource(geojson=json.dumps(geo_json))
antarctica_filter = GroupFilter(column_name="ISO_A2", group="AQ")
unranked_country_filter = BooleanFilter(
    booleans=[
        not feature["properties"].get("top_game_name")
        for feature in geo_json["features"]
    ]
)
unranked_view = CDSView(filter=~antarctica_filter & unranked_country_filter)
ranked_view = CDSView(filter=~antarctica_filter & ~unranked_country_filter)

# %%
palette = interp_palette(TolYlOrBr9, 256)

plot = figure(
    title="World of board games",
    width=750,
    aspect_ratio=2,
    match_aspect=True,
    background_fill_color="lightblue",
    x_range=(-180, 180),
    y_range=(-60, 85),
)

unranked_renderer = plot.patches(
    "xs",
    "ys",
    source=geo_source,
    view=unranked_view,
    line_color="black",
    line_width=0.5,
    fill_color="white",
    fill_alpha=1,
)

unranked_tooltips = [
    ("Country", "@flag @ADMIN (@ISO_A2_EH)"),
    ("Population", "@population{0,0.0} mil (#@population_rank)"),
]

plot.add_tools(HoverTool(renderers=[unranked_renderer], tooltips=unranked_tooltips))

ranked_renderer = plot.patches(
    "xs",
    "ys",
    source=geo_source,
    view=ranked_view,
    line_color="black",
    line_width=0.5,
    fill_color=log_cmap(
        "total_ratings",
        palette=palette,
        low=10,
        high=data["total_ratings"].max(),
        nan_color="white",
    ),
    fill_alpha=1,
)

ranked_tooltips = unranked_tooltips + [
    ("#1 game", "@top_game_name (@top_game_year)"),
    ("Number of users", "@num_users{0,0}"),
    ("Total ratings", "@total_ratings{0,0}k (#@total_ratings_rank)"),
    (
        "Ratings per capita",
        "@ratings_per_capita{0,0} per 100k (#@ratings_per_capita_rank)",
    ),
]

plot.add_tools(HoverTool(renderers=[ranked_renderer], tooltips=ranked_tooltips))
color_bar = ranked_renderer.construct_color_bar(title="Total ratings", padding=1)
plot.add_layout(color_bar, "left")

plot.axis.visible = False
plot.grid.visible = False

show(plot)

# %%
plot_dir = PROJECT_DIR / "plots"
plot_dir.mkdir(parents=True, exist_ok=True)
with (plot_dir / "board_games_world_map.json").open("w") as f:
    json.dump(json_item(plot), f, indent=4)
