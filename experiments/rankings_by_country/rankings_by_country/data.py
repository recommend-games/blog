import functools
import io
from typing import Iterable
import requests
import polars as pl
from rankings_by_country.countries import get_country_code


@functools.cache
def load_population_csv(
    url: str = "https://raw.githubusercontent.com/datasets/population/main/data/population.csv",
    *,
    add_rows: Iterable[str] | None = None,
) -> str:
    add_rows = tuple(add_rows) if add_rows is not None else ()
    pop_response = requests.get(url)
    pop_response.raise_for_status()
    if not add_rows:
        return pop_response.text
    add_rows += ("",)
    return pop_response.text + "\n".join(add_rows)


@functools.cache
def load_population_data(
    url: str = "https://raw.githubusercontent.com/datasets/population/main/data/population.csv",
) -> pl.LazyFrame:
    csv_str = load_population_csv(
        url,
        add_rows=(
            "Taiwan,TWN,2022,23894394",
            "Antarctica,ATA,2022,5000",
            "Vatican City,VAT,2024,524",
        ),
    )
    return (
        pl.read_csv(io.StringIO(csv_str))
        .lazy()
        .select(
            country_name="Country Name",
            year="Year",
            population="Value",
        )
        .sort("country_name", "year", descending=[False, True])
        .filter(pl.int_range(0, pl.len()).over("country_name") == 0)
        .with_columns(
            country_code=pl.col("country_name")
            .map_elements(
                get_country_code,
                return_dtype=pl.String,
            )
            .str.to_lowercase()
        )
        .drop("country_name", "year")
        .drop_nulls()
        .group_by("country_code")
        .agg(pl.col("population").max())
    )
