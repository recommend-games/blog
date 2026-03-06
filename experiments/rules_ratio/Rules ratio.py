# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
import polars as pl
import statsmodels.api as sm
from pathlib import Path

jupyter_black.load()

pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_rows(100)

seed = 13

# %%
# Additive smoothing
alpha = 0.5
beta = 0.5
# File paths
results_dir = Path("./results").resolve()
data_dir = Path("../../../board-game-data").resolve()
results_dir, data_dir

# %%
forums = (
    pl.scan_ndjson(results_dir / "*.jl")
    .unique("forum_id", keep="any")
    .select("bgg_id", "title", "num_threads")
)
rules_ratios = (
    forums.group_by("bgg_id")
    .agg(
        num_forums=pl.len(),
        num_threads_rules=pl.when(title="Rules").then("num_threads").otherwise(0).sum(),
        num_threads_total=pl.col("num_threads").sum(),
    )
    .remove(pl.col("num_forums") < 10)
    .remove(pl.col("num_threads_total") < 10)
    .with_columns(
        rules_ratio=(pl.col("num_threads_rules") + alpha)
        / (pl.col("num_threads_total") + alpha + beta)
    )
)
games = (
    pl.scan_ndjson(data_dir / "scraped" / "bgg_GameItem.jl", infer_schema_length=10_000)
    .remove(pl.col("compilation"))
    .select("bgg_id", "name", "year", "num_votes", "complexity")
    .remove(pl.col("num_votes") < 100)
    .remove(pl.col("complexity").is_null())
)
rrw = (
    rules_ratios.join(games, on="bgg_id", how="inner")
    .with_columns(rules_ratio_by_weight=pl.col("rules_ratio") / pl.col("complexity"))
    .sort(
        "rules_ratio_by_weight",
        "rules_ratio",
        "num_threads_total",
        descending=[True, True, False],
    )
    .collect()
)
rrw.shape

# %%
forums.group_by("title").agg(pl.len()).sort(
    "len",
    "title",
    descending=[True, False],
).collect()

# %%
rrw.sample(10, seed=seed)

# %%
rrw.describe()

# %%
rrw.head(10)

# %%
rrw.tail(10)


# %%
def add_residual_metric(df: pl.DataFrame) -> pl.DataFrame:
    # Basic hygiene
    d = (
        df.lazy()
        .filter(
            (pl.col("num_threads_total") >= 10)  # kill small-number chaos; tune this
            & (pl.col("complexity") > 0)
            & (pl.col("num_votes") > 0)
        )
        # shrink away from exact 0/1 so logit doesn't explode
        .select(
            "bgg_id",
            rr=pl.col("rules_ratio").clip(1e-6, 1 - 1e-6),
            w=pl.col("complexity"),
            log_votes=(pl.col("num_votes") + 1).log(),
            log_total_threads=(pl.col("num_threads_total") + 1).log(),
            # centre year to make intercept saner
            year_c=(pl.col("year") - pl.col("year").median()),
        )
        # logit(rr) = log(rr / (1-rr))
        .with_columns(y=(pl.col("rr") / (1 - pl.col("rr"))).log())
        .collect()
    )

    # Pull to numpy for statsmodels
    y = d["y"].to_pandas()
    X = d.select(
        "w",
        # "log_votes",
        # "year_c",
    ).to_pandas()
    # np.column_stack(
    #     [
    #         d["w"].to_numpy(),
    #         d["log_votes"].to_numpy(),
    #         d["log_total_threads"].to_numpy(),
    #         d["year_c"].to_numpy(),
    #     ]
    # )
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    y_hat = model.predict(X)
    resid = y - y_hat  # residuals in logit space

    # Attach back: residual > 0 means "more rules-chatter than expected"
    out = d.with_columns(
        pl.Series("rr_hat_logit", y_hat),
        pl.Series("rr_resid_logit", resid),
    )

    # Optional: map prediction back to ratio space for interpretability
    # sigmoid(z) = 1/(1+exp(-z))
    out = out.with_columns(
        (1 / (1 + (-pl.col("rr_hat_logit")).exp())).alias("rr_hat"),
    ).with_columns(
        (pl.col("rr") - pl.col("rr_hat")).alias("rr_resid"),
    )

    print(model.summary())
    return out


# %%
rrrw = add_residual_metric(rrw)

# %%
rrrw.sort("rr_resid", descending=True).head(10)

# %%
rrrw.sort("rr_resid", descending=False).head(10)
