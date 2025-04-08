# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl

jupyter_black.load()

seed = 13

# %%
events = (
    pl.scan_ndjson("results/snooker/events*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(
        pl.col("StartDate", "EndDate").str.to_date().cast(pl.Datetime(time_zone="UTC")),
    )
    .collect()
)
matches = (
    pl.scan_ndjson("results/snooker/matches*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(
        pl.col(
            "InitDate",
            "ModDate",
            "ScheduledDate",
            "StartDate",
            "EndDate",
        ).str.to_datetime("%+", strict=False, time_zone="UTC")
    )
    .collect()
)
players = (
    pl.scan_ndjson("results/snooker/players*.jl")
    .sort("scraped_at")
    .drop("scraped_at", "type")
    .group_by("ID", maintain_order=True)
    .last()
    .with_columns(pl.col(pl.String).replace("", None))
    .with_columns(pl.col("Born", "Died").str.to_date(strict=False))
    .collect()
)
events.shape, matches.shape, players.shape

# %%
events.sample(10, seed=seed)

# %%
events.describe()

# %%
matches.sample(10, seed=seed)

# %%
matches.describe()

# %%
players.sample(10, seed=seed)

# %%
players.describe()
