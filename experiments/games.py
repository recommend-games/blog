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


def _playable_with(dataframe, counts, prefix="", more_column=False):
    min_col, max_col = dataframe.columns
    result = pd.DataFrame(index=dataframe.index)

    count = 0  # just in case counts is empty
    for count in counts:
        playable = (dataframe[min_col] <= count) & (dataframe[max_col] >= count)
        column = f"{prefix}{count:02d}"
        result[column] = playable

    if more_column:
        playable = dataframe[max_col] > count
        column = f"{prefix}{count+1:02d}+"
        result[column] = playable

    return result


def make_transformer(
    list_columns,
    player_count_columns=("min_players", "max_players"),
    min_df=0.01,
):
    """Game transformer."""

    list_pipeline = make_pipeline(
        FunctionTransformer(_list_dataframe),
        FunctionTransformer(_combine_lists),
        CountVectorizer(analyzer=set, min_df=min_df, binary=True, dtype=np.uint8),
        FunctionTransformer(csr_matrix.todense),
    )
    playable_transformer = FunctionTransformer(
        _playable_with,
        kw_args={
            "counts": range(1, 11),
            "prefix": "playable_with_",
            "more_column": True,
        },
    )

    transformer = make_column_transformer(
        (list_pipeline, clear_list(arg_to_iter(list_columns))),
        (playable_transformer, clear_list(arg_to_iter(player_count_columns))),
        remainder="passthrough",
    )

    return transformer


def matrix_to_dataframe(matrix, transformer, original_columns, index=None):
    """Take the transformed matrix and turn it back into a dataframe."""

    _, list_pipeline, old_list_columns = transformer.transformers_[0]
    _, playable_transformer, old_playable_columns = transformer.transformers_[1]
    old_columns = frozenset(old_list_columns + old_playable_columns)

    vectorizer = list_pipeline.named_steps.countvectorizer
    _, transformed_list_columns = zip(
        *sorted((v, k) for k, v in vectorizer.vocabulary_.items())
    )

    prefix = playable_transformer.kw_args["prefix"]
    counts = playable_transformer.kw_args["counts"]
    more_column = playable_transformer.kw_args.get("more_column")
    transformed_playable_columns = [f"{prefix}{count:02d}" for count in counts]
    if more_column:
        count = max(counts)
        transformed_playable_columns.append(f"{prefix}{count+1:02d}+")

    columns = (
        list(transformed_list_columns)
        + transformed_playable_columns
        + [column for column in original_columns if column not in old_columns]
    )

    dataframe = pd.DataFrame(data=matrix, columns=columns, index=index)
    return dataframe.infer_objects()


def transform(
    data,
    list_columns,
    player_count_columns=("min_players", "max_players"),
    min_df=0.01,
):
    """Transform the data."""

    transformer = make_transformer(
        list_columns=list_columns,
        player_count_columns=player_count_columns,
        min_df=min_df,
    )
    matrix = transformer.fit_transform(data)
    return matrix_to_dataframe(
        matrix=matrix,
        transformer=transformer,
        original_columns=data.columns,
        index=data.index,
    )
