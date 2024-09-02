import logging
from pathlib import Path
from typing import Literal
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

sns.set_style("dark")

LOGGER = logging.getLogger(__name__)


def plot(
    data: pl.DataFrame,
    x_column: str,
    y_column: str,
    kind: Literal["reg", "cat"] = "reg",
    *,
    top_k_column: str = "num_votes",
    top_k: int | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    plot_kwargs: dict[str, any] | None = None,
    ax: Axes | None = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if top_k and top_k_column:
        data = data.top_k(by=top_k_column, k=top_k)

    plot_kwargs = plot_kwargs or {}
    plot_kwargs["data"] = data
    plot_kwargs["x"] = x_column
    plot_kwargs["y"] = y_column
    plot_kwargs.setdefault("color", "purple")
    plot_kwargs["ax"] = ax

    if kind == "reg":
        sns.regplot(
            **plot_kwargs,
            scatter_kws={
                "alpha": 0.5,
                "s": 10,
            },
            line_kws={
                "lw": 3,
                "color": "crimson",
            },
            seed=seed,
        )
    elif kind == "cat":
        sns.violinplot(**plot_kwargs)
    else:
        raise ValueError(f"Unknown kind: {kind}")

    ax.set_title(title or f"{y_column} vs {x_column}")
    ax.set_xlabel(x_label or x_column)
    ax.set_ylabel(y_label or y_column)

    return ax


def save_plot(
    data: pl.DataFrame,
    x_column: str,
    y_column: str,
    kind: Literal["reg", "cat"] = "reg",
    path: str | Path | None = None,
    *,
    top_k_column: str = "num_votes",
    top_k: int | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    plot_kwargs: dict[str, any] | None = None,
    show: bool = False,
) -> None:
    if not path and not show:
        raise ValueError("Neither path nor show is set")

    if path:
        path = Path(path).resolve()
        LOGGER.info("Saving %s plot to <%s>", kind, path)
        path.parent.mkdir(parents=True, exist_ok=True)

    plot(
        data=data,
        x_column=x_column,
        y_column=y_column,
        kind=kind,
        top_k_column=top_k_column,
        top_k=top_k,
        figsize=figsize,
        seed=seed,
        title=title,
        x_label=x_label,
        y_label=y_label,
        plot_kwargs=plot_kwargs,
    )

    plt.tight_layout()
    if path:
        plt.savefig(path.parent / f"{path.stem}_{kind}.png")
        plt.savefig(path.parent / f"{path.stem}_{kind}.svg")
    if show:
        plt.show()
    plt.close()
