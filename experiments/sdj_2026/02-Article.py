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
from pathlib import Path
from tqdm import tqdm

jupyter_black.load()

pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_rows(100)

COMPLEXITIES = (None, "light", "medium light", "medium", "medium heavy", "heavy")

PREDICTIONS_PATH = Path("predictions.csv").resolve()
DESCRIPTIONS_PATH = Path("descriptions.csv").resolve()
TEMPLATE_PATH = Path("template.md").resolve()
ARTICLE_PATH = Path("predictions.md").resolve()
PREDICTIONS_PATH, DESCRIPTIONS_PATH, TEMPLATE_PATH, ARTICLE_PATH

# %%
with TEMPLATE_PATH.open() as f:
    template = f.read()

# %%
predictions = (
    pl.scan_csv(PREDICTIONS_PATH, infer_schema_length=None)
    .filter(pl.col("sdj_rank") <= 30)
    .select(
        "bgg_id",
        "name",
        "year",
        "complexity",
        "min_age",
        "min_time",
        "max_time",
        "min_players",
        "max_players",
        "kennerspiel_score",
        "kennerspiel",
        "sdj_score",
        "sdj_rank",
    )
)

if not DESCRIPTIONS_PATH.exists():
    predictions.select(
        "bgg_id",
        "name",
        description=pl.lit(""),
    ).collect().write_csv(DESCRIPTIONS_PATH)

# %%
descriptions = pl.scan_csv(DESCRIPTIONS_PATH, infer_schema_length=None).select(
    "bgg_id",
    "description",
)

predictions = (
    predictions.join(descriptions, on="bgg_id", how="left")
    .with_columns(
        pl.format(
            template,
            "sdj_rank",
            "bgg_id",
            "name",
            pl.when(pl.col("min_players") < pl.col("max_players"))
            .then(pl.format("{}–{}", "min_players", "max_players"))
            .otherwise("min_players"),
            pl.when(pl.col("min_time") < pl.col("max_time"))
            .then(pl.format("{}–{}", "min_time", "max_time"))
            .otherwise("min_time"),
            "min_age",
            pl.lit(COMPLEXITIES).list.get(pl.col("complexity").round().cast(pl.Int64)),
            pl.col("complexity").round(1),
            pl.when(pl.col("kennerspiel"))
            .then(
                pl.format(
                    "{}% {{% kdj %}}Kennerspiel{{% /kdj %}}",
                    (pl.col("kennerspiel_score") * 100).round().cast(pl.Int64),
                ),
            )
            .otherwise(
                pl.format(
                    "{}% {{% sdj %}}Spiel{{% /sdj %}}",
                    ((1 - pl.col("kennerspiel_score")) * 100).round().cast(pl.Int64),
                ),
            ),
            "bgg_id",
            "name",
            pl.coalesce("description", "name"),
        ),
    )
    .collect()
)
predictions.shape

# %%
with ARTICLE_PATH.open("w") as file:
    for lit in tqdm(predictions["literal"]):
        print(lit, file=file)
        print(file=file)
