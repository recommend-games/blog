from datetime import timezone
from itertools import groupby
from pathlib import Path
import numpy as np
import pandas as pd
from pytility import parse_date


def load_daily_hotness(
    path_dir,
    start_date,
    end_date,
    glob="*.csv",
    index_col="bgg_id",
):
    path_dir = Path(path_dir).resolve()
    start_date = parse_date(start_date, tzinfo=timezone.utc)
    end_date = parse_date(end_date, tzinfo=timezone.utc)

    for date, group in groupby(
        sorted(
            (date, path_file)
            for path_file in path_dir.glob(glob)
            if start_date
            <= (date := parse_date(path_file.stem, tzinfo=timezone.utc))
            < end_date
        ),
        key=lambda x: x[0].date(),
    ):
        _, path_file = min(group)
        series = pd.read_csv(path_file, index_col=index_col)["rank"]
        yield series.rename(date.isoformat())


def _compute_scores(
    path_dir,
    start_date,
    end_date,
    top=None,
):
    result = pd.concat(
        objs=load_daily_hotness(
            path_dir=path_dir,
            start_date=start_date,
            end_date=end_date,
        ),
        axis=1,
    )

    if top:
        return pd.Series(
            {
                bgg_id: np.exp2(1 - ranks.sort_values().head(top)).sum() / top
                for bgg_id, ranks in result.T.iteritems()
            }
        )

    full_scores = 2 ** (1 - result)
    return full_scores.sum(axis=1) / result.shape[1]


def aggregate_hotness(
    path_dir,
    start_date,
    end_date,
    top=None,
):
    return _compute_scores(
        path_dir=path_dir,
        start_date=start_date,
        end_date=end_date,
        top=top,
    ).sort_values(ascending=False)
