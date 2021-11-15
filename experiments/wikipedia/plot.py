# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from bokeh.io import output_notebook
from bokeh.palettes import Colorblind8
from bokeh.plotting import figure, show
from pytility import parse_date
from scipy.interpolate import PchipInterpolator

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
def ts_to_epoch(ts, anchor=pd.Timestamp("1970-01-01"), freq="1s"):
    ts = pd.to_datetime(ts)
    anchor = pd.Timestamp(ts[0] if anchor is None else anchor)
    return (ts - anchor) / pd.Timedelta(freq)


def epoch_to_ts(epochs, anchor=pd.Timestamp("1970-01-01"), freq="1s"):
    epochs = pd.Series(epochs).astype(float)
    anchor = pd.Timestamp(anchor)
    return epochs * pd.Timedelta(freq) + anchor


# %%
top = 20
data = df[df.columns[-50:]]
dates = data.columns.map(datetime.fromisoformat)

anchor = dates[0]
freq = "1w"
x = ts_to_epoch(dates, anchor, freq)
x = pd.Series([x[0] - 1] + list(x) + [x[-1] + 1])
xs = np.arange(x.iloc[0] + 0.5, x.iloc[-1] - 0.5, 0.05)
xs_dates = epoch_to_ts(xs, anchor, freq)

p = figure(
    title="Wiki stats",
    # tools=[HoverTool()],
    tooltips="$name",
    x_range=(dates[-11], dates[-1]),
    y_range=(20.5, 0.5),
    x_axis_type="datetime",
    x_axis_label="Date",
    y_axis_label="Rank",
    # sizing_mode="stretch_width",
    height=800,
)
# p.y_range.flipped = True

for i, (bgg_id, row) in enumerate(data.head(top * 2).T.items()):
    name = games["name"][bgg_id]
    color = Colorblind8[i % 8]
    y = pd.Series([row[0]] + list(row) + [row[-1]]).fillna(101)
    cs = PchipInterpolator(x, y)

    p.line(
        xs_dates,
        cs(xs),
        name=name,
        color=color,
        line_width=2,
    )
    p.circle(
        dates,
        row,
        name=name,
        color=color,
    )

# p.legend.visible = False

show(p)
