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

jupyter_black.load()

pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_rows(100)

COMPLEXITIES = (None, "light", "medium light", "medium", "medium heavy", "heavy")
comp_cat = pl.lit(COMPLEXITIES)

# %%
with open("template.md") as f:
    template = f.read()

# %%
predictions = (
    pl.scan_csv("predictions.csv", infer_schema_length=None)
    .filter(pl.col("sdj_rank") <= 12)
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
            comp_cat.list.get(pl.col("complexity").round().cast(pl.Int64)),
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
            pl.lit("TODO: description"),
        ),
    )
    .collect()
)
predictions.shape

# %%
for lit in predictions["literal"]:
    print(lit)
    print()
