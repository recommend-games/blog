# -*- coding: utf-8 -*-

"""Game utilities."""

from itertools import chain

import numpy as np
import pandas as pd

from pytility import arg_to_iter, clear_list, parse_int
from scipy.sparse import csr_matrix
from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer


def _parse_list(value, prefix=None):
    if isinstance(value, str):
        value = value.split(",")
    values = clear_list(map(parse_int, arg_to_iter(value)))
    return [f"{prefix}{v}" for v in values] if prefix else values


def _list_series(series):
    return series.apply(_parse_list, prefix=series.name + ":")


def _list_dataframe(dataframe):
    return dataframe.apply(_list_series)


def _concat_lists(iterable):
    return list(chain.from_iterable(iterable))


def _combine_lists(dataframe):
    return dataframe.apply(_concat_lists, axis=1)


def make_transformer(columns, min_df=0.01):
    """Game transformer."""

    pipeline = make_pipeline(
        FunctionTransformer(_list_dataframe),
        FunctionTransformer(_combine_lists),
        CountVectorizer(analyzer=set, min_df=min_df, binary=True, dtype=np.uint8),
        FunctionTransformer(csr_matrix.todense),
    )

    transformer = make_column_transformer(
        (pipeline, clear_list(arg_to_iter(columns))),
        remainder="passthrough",
    )

    return transformer


def matrix_to_dataframe(matrix, transformer, original_columns, index=None):
    """Take the transformed matrix and turn it back into a dataframe."""

    _, pipeline, old_columns = transformer.transformers_[0]
    vectorizer = pipeline.named_steps.countvectorizer
    _, transformed_columns = zip(
        *sorted((v, k) for k, v in vectorizer.vocabulary_.items())
    )
    columns = transformed_columns + tuple(
        column for column in original_columns if column not in old_columns
    )
    dataframe = pd.DataFrame(data=matrix, columns=columns, index=index)
    return dataframe.infer_objects()


def transform(data, columns, min_df=0.01):
    """Transform the data."""

    transformer = make_transformer(columns=columns, min_df=min_df)
    matrix = transformer.fit_transform(data)
    return matrix_to_dataframe(
        matrix=matrix,
        transformer=transformer,
        original_columns=data.columns,
        index=data.index,
    )
