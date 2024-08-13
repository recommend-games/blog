import matplotlib
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

sns.set_style("dark")


def plot_average(
    data: pl.DataFrame,
    y_column: str,
    regression: bool = False,
    *,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    ax: Axes | None = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    plot_kwargs = {
        "data": data,
        "x": "year",
        "y": y_column,
        "color": "purple",
        "ax": ax,
    }

    if regression:
        sns.regplot(
            **plot_kwargs,
            ci=95,
            scatter_kws={
                "s": data["rel_num_games"]
                * matplotlib.rcParams["lines.markersize"] ** 2,
            },
            seed=seed,
        )
    else:
        sns.scatterplot(**plot_kwargs)

    ax.set_title("TODO")

    return ax
