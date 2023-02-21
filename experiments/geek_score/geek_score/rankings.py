from collections import defaultdict
from itertools import groupby

from more_itertools import first, last


def print_rankings_report(rankings, games):
    total = defaultdict(int)
    cleaned = rankings.resample("D").last().fillna(method="ffill")

    print("*** #1 games timeline ***\n")
    for bgg_id, group in groupby(cleaned.itertuples(), key=lambda x: x.bgg_id):
        name = games.loc[bgg_id]["name"]
        timestamps = (row.Index for row in group)
        begin = first(timestamps)
        end = last(timestamps, default=begin)
        diff = end - begin
        days = round(diff.total_seconds() / 60 / 60 / 24) + 1
        print(
            f"{name:25}: {days:>4} day{'s' if days > 1 else ' '} ({begin.date()} to {end.date()})"
        )
        total[bgg_id] += days

    print("\n\n\n*** #1 games by number of days ***\n")
    for bgg_id, days in sorted(total.items(), key=lambda x: -x[1]):
        name = games.loc[bgg_id]["name"]
        print(f"{name:25}: {days:>4} day{'s' if days > 1 else ''}")
