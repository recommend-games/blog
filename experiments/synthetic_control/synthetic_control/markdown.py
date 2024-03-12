from pathlib import Path
import polars as pl
import json


def markdown_function(
    bgg_id: int,
    results_file: str | Path,
    games_file: str | Path,
) -> str:
    results_file = Path(results_file).resolve()
    games_file = Path(games_file).resolve()

    with results_file.open("r") as f:
        results = json.load(f)

    game_result = next(
        (result for result in results if result["game_data"]["bgg_id"] == bgg_id),
        None,
    )

    if not game_result:
        raise ValueError(f"Game with bgg_id <{bgg_id}> not found in <{results_file}>")

    game_model = {int(k): float(v) for k, v in game_result["model"].items()}

    try:
        game_names_df = (
            pl.scan_ndjson(games_file)
            .select("bgg_id", "name")
            .filter(pl.col("bgg_id").is_in(game_model.keys()))
            .collect()
        )
    except Exception as exc:
        raise ValueError(
            f"Game with bgg_id <{bgg_id}> not found in <{games_file}>"
        ) from exc

    game_names = dict(zip(game_names_df["bgg_id"], game_names_df["name"]))

    model_strs = (
        f"* {v:+6.1%} ⋅ {{{{% game {k} %}}}}{game_names[k]}{{{{% /game %}}}}"
        for k, v in game_model.items()
    )

    return "\n".join(model_strs)


if __name__ == "__main__":
    print(
        markdown_function(
            bgg_id=332686,
            results_file="results/results.json",
            games_file="../../../board-game-data/scraped/bgg_GameItem.jl",
        )
    )
