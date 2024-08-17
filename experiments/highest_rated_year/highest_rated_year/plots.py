import logging
import matplotlib
from pathlib import Path
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

sns.set_style("dark")

LOGGER = logging.getLogger(__name__)


def plot_average(
    data: pl.DataFrame,
    y_column: str,
    regression: bool = False,
    *,
    title: str | None = None,
    sizes_column: str | None = None,
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

    sizes = (
        data[sizes_column] * matplotlib.rcParams["lines.markersize"] ** 2
        if sizes_column
        else None
    )

    if regression:
        sns.regplot(
            **plot_kwargs,
            ci=95,
            scatter_kws={"s": sizes},
            seed=seed,
        )
    else:
        sns.scatterplot(
            **plot_kwargs,
            size=sizes,
            legend=False,
        )

    ax.set_title(title or y_column)
    ax.set_xlabel(None)
    ax.set_ylabel(None)

    return ax


def save_plots(
    data: pl.DataFrame,
    y_column: str,
    *,
    title: str | None = None,
    sizes_column: str | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    plot_dir: str | Path | None = None,
    file_name: str | None = None,
    show: bool = False,
) -> None:
    if plot_dir is None and show is False:
        raise ValueError("Neither plot_dir nor show is set")

    if plot_dir is not None:
        plot_dir = Path(plot_dir).resolve()
        plot_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Saving plots to <%s>", plot_dir)
        file_name = file_name or y_column

    plot_average(
        data=data,
        y_column=y_column,
        regression=False,
        title=title,
        sizes_column=sizes_column,
        figsize=figsize,
        seed=seed,
    )
    plt.tight_layout()
    if plot_dir:
        plt.savefig(plot_dir / f"{file_name}_scatter.png")
        plt.savefig(plot_dir / f"{file_name}_scatter.svg")
    if show:
        plt.show()
    plt.close()

    plot_average(
        data=data,
        y_column=y_column,
        regression=True,
        title=title,
        sizes_column=sizes_column,
        figsize=figsize,
        seed=seed,
    )
    plt.tight_layout()
    if plot_dir:
        plt.savefig(plot_dir / f"{file_name}_reg.png")
        plt.savefig(plot_dir / f"{file_name}_reg.svg")
    if show:
        plt.show()
    plt.close()
