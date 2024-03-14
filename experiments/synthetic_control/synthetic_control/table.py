import json
from pathlib import Path


def result_table(result_path: str | Path) -> str:
    result_path = Path(result_path).resolve()

    with result_path.open("r") as f:
        results = json.load(f)

    header = "| Game | Review date | SU&SD effect | Plot |"
    separator = "| :--- | :---------: | -----------: | :--: |"
    rows = []

    for result in results:
        bgg_id = result["game_data"]["bgg_id"]
        name = result["game_data"]["name"]
        review_date = result["game_data"]["date_review"]
        susd_effect = result["susd_effect_rel"]
        plot = result["plot_path_synthetic_control"]

        row = (
            f"| {{{{% game {bgg_id} %}}}}{name}{{{{% /game %}}}}"
            + f" | {review_date}"
            + f" | **{susd_effect:+.1%}**"
            + f" | [[link]]({plot}) |"
        )
        rows.append(row)

    return "\n".join([header, separator, *rows])


if __name__ == "__main__":
    print(result_table("results/results.json"))
