# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
from datetime import datetime
from itertools import batched
from pathlib import Path
from tqdm import tqdm

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
in_dir = Path("results").resolve()
out_dir = in_dir / "arrow"
out_dir.mkdir(parents=True, exist_ok=True)
in_dir, out_dir

# %%
file_batch_size = 10
ts = datetime.now().replace(microsecond=0).isoformat().replace(":", "-")
suffix = f"{ts}-euler-"
file_batch_size, suffix

# %%
schema = {
    "id": pl.String,
    "timestamp": pl.String,
    "game_id": pl.Int64,
    "players": pl.List(
        pl.Struct(
            {
                "player_id": pl.Int64,
                "place": pl.Int64,
                "score": pl.Float64,
            }
        )
    ),
    "scraped_at": pl.String,
}

# %%
for i, batch in enumerate(batched(tqdm(in_dir.glob("matches-*.jl")), file_batch_size)):
    df = (
        pl.scan_ndjson(list(batch), schema=schema)
        .with_columns(
            pl.col("id").cast(pl.Int64),
            pl.col("timestamp").cast(pl.Int64),
        )
        .with_columns(
            pl.from_epoch("timestamp").dt.convert_time_zone(time_zone="UTC"),
            pl.col("scraped_at").str.to_datetime(time_zone="UTC"),
        )
    )
    df.sink_ipc(out_dir / f"matches-{suffix}{i:05d}.arrow")
