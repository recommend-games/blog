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
from datetime import date
import jupyter_black
import pandas as pd
from bokeh.plotting import figure, output_notebook, show

jupyter_black.load()

pd.options.display.max_columns = 100
pd.options.display.max_rows = 1000
pd.options.display.float_format = "{:.6g}".format

output_notebook()

this_year = date.today().year

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
games.drop(index=games[games["compilation_of"].notna()].index, inplace=True)
games["cooperative"] = games["cooperative"].fillna(False).astype(bool)
games.shape

# %%
games["cooperative"].mean()

# %%
games[games["cooperative"]].sort_values("year").head(10)

# %%
years = games.groupby("year")["cooperative"].agg(["size", "sum", "mean"])
years["total"] = years["size"]
years["co-operative"] = years["sum"]
years["competitive"] = years["total"] - years["co-operative"]
years[(years.index >= 1900) & (years.index <= this_year)]

# %%
year_from = 2000
year_to = this_year
year_range = [str(year) for year in range(year_from, year_to + 1)]
year_df = years[(years.index >= year_from) & (years.index <= year_to)]

# %%
data = {
    "years": year_range,
    "co-operative": list(year_df["co-operative"]),
    "competitive": list(year_df["competitive"]),
}

p = figure(
    x_range=year_range,
    height=250,
    title="Co-operative games",
    toolbar_location=None,
    tools="",
)
cat = ["co-operative", "competitive"]
colors = ["#c9d9d3", "#718dbf"]
p.vbar_stack(cat, x="years", width=0.9, color=colors, source=data, legend_label=cat)
p.legend.location = "top_left"
p.legend.orientation = "horizontal"
p.xaxis.major_label_orientation = 1
show(p)

# %%
data = {
    "years": year_range,
    "co-operative": list(year_df["co-operative"] / year_df["total"]),
    "competitive": list(year_df["competitive"] / year_df["total"]),
}

p = figure(
    x_range=year_range,
    height=250,
    title="Co-operative games",
    toolbar_location=None,
    tools="",
)
cat = ["co-operative", "competitive"]
colors = ["#c9d9d3", "#718dbf"]
p.vbar_stack(cat, x="years", width=0.9, color=colors, source=data, legend_label=cat)
p.legend.location = "top_left"
p.legend.orientation = "horizontal"
p.xaxis.major_label_orientation = 1
show(p)
