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
import importlib.resources
import jupyter_black
import numpy as np
import polars as pl
from pathlib import Path
from datetime import date

jupyter_black.load()

pl.Config.set_tbl_rows(50)

EXPERIMENT_DIR = Path(".").resolve().parent
FROM_YEAR = 2021
TO_YEAR = date.today().year

FROM_YEAR, TO_YEAR


# %%
def calculate_ndcg(
    jahrgang: int,
    *,
    experiment_dir: Path = EXPERIMENT_DIR,
    points_winner: int = 10,
    points_sonderpreis: int = 5,
    points_nominated: int = 3,
    points_recommended: int = 1,
) -> float:
    data_dir = importlib.resources.files("spiel_des_jahres") / "data"

    with (
        importlib.resources.as_file(data_dir / "sdj.csv") as sdj_path,
        importlib.resources.as_file(data_dir / "ksdj.csv") as ksdj_path,
    ):
        sdj = (
            pl.scan_csv([sdj_path, ksdj_path], infer_schema_length=None)
            .filter(jahrgang=jahrgang)
            .select(
                "bgg_id",
                points=pl.when(winner=1)
                .then(points_winner)
                .when(pl.col("sonderpreis").is_not_null())
                .then(points_sonderpreis)
                .when(nominated=1)
                .then(points_nominated)
                .when(recommended=1)
                .then(points_recommended)
                .otherwise(0),
            )
        )

        return (
            pl.scan_csv(
                experiment_dir / f"sdj_{jahrgang}" / "predictions.csv",
                infer_schema_length=None,
            )
            .select("bgg_id", "sdj_score")
            .join(sdj, on="bgg_id", how="full", coalesce=True)
            .with_columns(
                pl.col("points").fill_null(0),
                pl.col("sdj_score").fill_null(-np.inf),
            )
            .with_columns(
                rank_pred=pl.col("sdj_score").rank("ordinal", descending=True),
                rank_ideal=pl.col("points").rank("ordinal", descending=True),
            )
            .with_columns(
                dg=(2 ** pl.col("points") - 1) / (pl.col("rank_pred") + 1).log(2),
                idg=(2 ** pl.col("points") - 1) / (pl.col("rank_ideal") + 1).log(2),
            )
            .select(ndcg=pl.col("dg").sum() / pl.col("idg").sum())
            .collect()
            .item()
        )


# %%
for jahrgang in range(FROM_YEAR, TO_YEAR + 1):
    ndcg = calculate_ndcg(
        jahrgang,
        points_winner=1,
        points_sonderpreis=1,
        points_nominated=1,
        points_recommended=1,
    )
    print(f"{jahrgang}: {ndcg:.5f}")
