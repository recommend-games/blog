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
            "min_players",  # also max_players
            "min_time",  # also max_time
            "min_age",  # add +
            "complexity",  # category?
            (pl.col("kennerspiel_score") * 100).round(),  # format
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
