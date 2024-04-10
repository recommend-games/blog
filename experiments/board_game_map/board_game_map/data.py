import math
import polars as pl
import polars.selectors as cs


def process_game_data(rankings_data: pl.DataFrame) -> pl.DataFrame:
    rank_columns = rankings_data.select(cs.ends_with("_rank")).columns
    columns_map = {i: col[:-5] for i, col in enumerate(rank_columns)}

    return (
        rankings_data.filter(pl.any_horizontal(cs.ends_with("_rank").is_not_null()))
        .with_columns(cs.ends_with("_rank") / cs.ends_with("_rank").max())
        .fill_null(math.inf)
        .select(
            bgg_id="id",
            name="name",
            num_ratings="usersrated",
            game_type=pl.concat_list(rank_columns).list.arg_min().replace(columns_map),
        )
    )
