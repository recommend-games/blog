import numpy as np
import polars as pl
import statsmodels.api as sm
from scipy.stats import t


def t_test(
    data: pl.DataFrame,
    y_column: str,
    sig_level: float = 0.05,
) -> pl.DataFrame:
    years = sm.add_constant(data["year"].to_numpy())
    model = sm.OLS(data[y_column].to_numpy(), years).fit()

    predictions = model.predict(years)
    influence = model.get_influence()
    resid = influence.resid
    resid_studentized = influence.resid_studentized_internal

    data = data.with_columns(
        pl.Series(f"{y_column}_pred", predictions),
        pl.Series(f"{y_column}_error", resid),
        pl.Series(f"{y_column}_error_studentized", resid_studentized),
        pl.Series(
            f"{y_column}_p_value",
            t.sf(x=np.abs(resid_studentized), df=model.df_resid) * 2,
        ),
    ).with_columns(
        (pl.col(f"{y_column}_p_value") <= sig_level).alias(f"{y_column}_significant"),
    )

    p_values = data[f"{y_column}_p_value"].to_numpy()
    adjusted_bonferroni = sm.stats.multipletests(
        pvals=p_values,
        alpha=sig_level,
        method="bonferroni",
    )
    adjusted_holm = sm.stats.multipletests(
        pvals=p_values,
        alpha=sig_level,
        method="holm",
    )
    adjusted_bh = sm.stats.multipletests(
        pvals=p_values,
        alpha=sig_level,
        method="fdr_bh",
    )

    data = data.with_columns(
        pl.Series(
            f"{y_column}_p_value_bonferroni",
            adjusted_bonferroni[1],
        ),
        pl.Series(
            f"{y_column}_significant_bonferroni",
            adjusted_bonferroni[0],
        ),
        pl.Series(
            f"{y_column}_p_value_holm",
            adjusted_holm[1],
        ),
        pl.Series(
            f"{y_column}_significant_holm",
            adjusted_holm[0],
        ),
        pl.Series(
            f"{y_column}_p_value_bh",
            adjusted_bh[1],
        ),
        pl.Series(
            f"{y_column}_significant_bh",
            adjusted_bh[0],
        ),
    )

    return data
