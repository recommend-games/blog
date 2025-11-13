# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
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
in_dir = Path("../results").resolve()
out_dir = in_dir / "arrow"
match_dir = out_dir / "matches"
out_dir.mkdir(parents=True, exist_ok=True)
match_dir.mkdir(parents=True, exist_ok=True)
in_dir, out_dir, match_dir

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

# %%
matches = pl.scan_ipc(out_dir / "matches-*.arrow")
game_ids = matches.select(pl.col("game_id").unique()).collect()["game_id"]
game_ids.shape

# %%
for game_id in tqdm(game_ids):
    match_data = (
        matches.filter(pl.col("game_id") == game_id)
        .sort("scraped_at", "timestamp")
        .unique("id", keep="first")
        .select(
            num_players=pl.col("players").list.len(),
            player_ids=pl.col("players").list.eval(
                pl.element().struct.field("player_id")
            ),
            places=pl.col("players").list.eval(pl.element().struct.field("place")),
        )
        .filter(pl.col("num_players") >= 2)
        .filter(pl.col("player_ids").list.eval(pl.element().is_not_null()).list.all())
        .filter(
            pl.col("places")
            .list.eval(pl.element().is_not_null() & (pl.element() >= 1))
            .list.all()
        )
        .with_columns(payoffs=pl.col("places").list.eval(pl.len() - pl.element()))
        .filter(pl.col("payoffs").list.eval(pl.element() >= 0).list.all())
    )
    match_data.sink_ipc(match_dir / f"{game_id}.arrow")
