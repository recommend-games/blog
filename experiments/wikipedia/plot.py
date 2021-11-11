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
from datetime import datetime
from pathlib import Path
import pandas as pd
from bokeh.io import output_notebook
from bokeh.palettes import plasma
from bokeh.plotting import figure, show
from pytility import parse_date

output_notebook()

# %load_ext nb_black
# %load_ext lab_black

# %%
data_path = Path("../../../board-game-data").resolve()
bgg_path = data_path / "scraped" / "bgg_GameItem.csv"
stats_path = Path().resolve() / "stats" / "weekly"

# %%
games = pd.read_csv(
    bgg_path,
    index_col="bgg_id",
    low_memory=False,
)
games.shape


# %%
def load_ranks(path_dir):
    for path_file in sorted(path_dir.glob("*.csv")):
        date = str(parse_date(path_file.stem).date())
        yield pd.read_csv(path_file, index_col="bgg_id")["rank"].rename(date)


# %%
df = pd.concat(load_ranks(stats_path), axis=1)
df.drop(columns=df.columns[-1], inplace=True)
df.sort_values(by=sorted(df.columns, reverse=True), inplace=True)
df.shape

# %%
df[df.columns[-10:]].head(10)

# %%
dates = df.columns.map(datetime.fromisoformat)
top = 50

p = figure(
    title="Wiki stats",
    # tools=[HoverTool()],
    tooltips="$name",
    x_range=(dates[-11], dates[-1]),
    y_range=(top + 0.5, 0.5),
    x_axis_type="datetime",
    x_axis_label="Date",
    y_axis_label="rank",
    # sizing_mode="stretch_width",
    height=800,
)
# p.y_range.flipped = True

for (bgg_id, row), color in zip(df.head(top * 2).T.items(), plasma(top * 2)):
    p.line(
        dates,
        row,
        name=f"{games['name'][bgg_id]}",
        color=color,
        line_width=2,
    )
    p.circle(
        dates,
        row,
        name=f"{games['name'][bgg_id]}",
        color=color,
    )

# p.legend.visible = False

show(p)
