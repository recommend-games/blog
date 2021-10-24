from itertools import tee
from dateutil.rrule import MONTHLY, WEEKLY, YEARLY, rrule
from snaptime import snap


def pairwise(iterable):
    it1, it2 = tee(iterable)
    next(it2, None)
    return zip(it1, it2)


def gen_start_and_end_dates(min_date, max_date, freq):
    if freq == "week":
        instruction = "@week1"  # previous Monday
        freq = WEEKLY
    elif freq == "month":
        instruction = "@month"  # beginning of the month
        freq = MONTHLY
    elif freq == "year":
        instruction = "@year"  # beginning of the year
        freq = YEARLY
    else:
        raise ValueError(f"Unknow frequency <{freq}>")

    return pairwise(
        rrule(
            dtstart=snap(min_date, instruction),
            until=max_date,
            freq=freq,
        )
    )
