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
    # model.summary().tables[1]

    # Bonferroni correction
    alpha = sig_level / len(data)

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
    ).with_columns((pl.col(f"{y_column}_p_value") < alpha).alias(f"{y_column}_sig"))

    return data
