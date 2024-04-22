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
import io
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
from bokeh.palettes import Plasma256
from bokeh.plotting import figure
from bokeh.transform import log_cmap
from rankings_by_country.countries import get_country_code, get_flag_emoji

jupyter_black.load()

output_notebook()

PROJECT_DIR = Path(".").resolve()
BASE_DIR = PROJECT_DIR.parent.parent
DATA_DIR = BASE_DIR.parent / "board-game-data"
PROJECT_DIR, BASE_DIR, DATA_DIR

# %%
pop_response = requests.get(
    "https://raw.githubusercontent.com/datasets/population/main/data/population.csv"
)
pop_response.raise_for_status()
country_population = (
    pl.read_csv(io.StringIO(pop_response.text + "Taiwan,TWN,2022,23894394\n"))
    .lazy()
    .select(
        country_name=pl.col("Country Name"),
        year=pl.col("Year"),
        population=pl.col("Value"),
    )
    .sort("country_name", "year", descending=[False, True])
    .filter(pl.int_range(0, pl.len()).over("country_name") < 1)
    .sort("population", descending=True)
    .with_columns(
        country_code=pl.col("country_name")
        .map_elements(
            get_country_code,
            return_dtype=pl.String,
        )
        .str.to_lowercase()
    )
    .drop("country_name", "year")
    .filter(pl.col("country_code").str.len_chars() == 2)
    .group_by("country_code")
    .agg(pl.col("population").max())
)

# %%
game_data = pl.scan_csv(DATA_DIR / "scraped" / "bgg_GameItem.csv").select(
    "bgg_id",
    "name",
    "year",
)
ranking_data = pl.scan_csv("rankings/*.csv")
country_stats = ranking_data.group_by("country_code").agg(
    num_games=pl.len(),
    total_ratings=pl.col("num_ratings").sum(),
)
top_games = (
    ranking_data.sort("country_code", "rank")
    .filter(pl.int_range(0, pl.len()).over("country_code") < 1)
    .drop("rank")
    .join(game_data, on="bgg_id", how="inner")
)
data = (
    country_stats.join(top_games, on="country_code", how="inner")
    .join(country_population, on="country_code", how="outer")
    .with_columns(
        country_code=pl.coalesce("country_code", "country_code_right"),
        ratings_per_capita=pl.col("total_ratings") * 100_000 // pl.col("population"),
    )
    .drop("country_code_right")
    .with_columns(
        pl.col("total_ratings") // 1_000,
        pl.col("population") / 1_000_000,
        flag=pl.col("country_code").map_elements(
            get_flag_emoji,
            return_dtype=pl.String,
        ),
    )
    .sort("total_ratings", "population", descending=True, nulls_last=True)
    .collect()
)
data.shape

# %%
data.head(10)

# %%
data.sort("ratings_per_capita", descending=True, nulls_last=True).head(10)

# %%
# url = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
# url = "https://raw.githubusercontent.com/simonepri/geo-maps/master/previews/countries-land.geo.json"
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
        not feature["properties"].get("total_ratings")
        for feature in geo_json["features"]
    ]
)
unranked_view = CDSView(filter=~antarctica_filter & unranked_country_filter)
ranked_view = CDSView(filter=~antarctica_filter & ~unranked_country_filter)

# %%
plot = figure(
    title="World of board games",
    width=1000,
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
    fill_alpha=1,
    fill_color=log_cmap(
        "total_ratings",
        palette=Plasma256,
        low=data["total_ratings"].min(),
        high=data["total_ratings"].max(),
        nan_color="white",
    ),
)

unranked_tooltips = [
    ("Country", "@flag @ADMIN (@ISO_A2_EH)"),
    ("Population", "@population{0,1} mil"),
]

plot.add_tools(HoverTool(renderers=[unranked_renderer], tooltips=unranked_tooltips))

ranked_renderer = plot.patches(
    "xs",
    "ys",
    source=geo_source,
    view=ranked_view,
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

ranked_tooltips = unranked_tooltips + [
    ("#1 game", "@name (@year)"),
    ("Total ratings", "@total_ratings{0,0}k"),
    ("Ratings per capita", "@ratings_per_capita{0,0} per 100k"),
]

plot.add_tools(HoverTool(renderers=[ranked_renderer], tooltips=ranked_tooltips))

plot.axis.visible = False
plot.grid.visible = False

show(plot)

# %%
plot_dir = PROJECT_DIR / "plots"
plot_dir.mkdir(parents=True, exist_ok=True)
with (plot_dir / "board_games_world_map.json").open("w") as f:
    json.dump(json_item(plot), f, indent=4)
