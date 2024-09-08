import logging
from pathlib import Path
from typing import Literal
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import animation, pyplot as plt
from matplotlib.axes import Axes
from tqdm import tqdm

sns.set_style("dark")

LOGGER = logging.getLogger(__name__)


def plot(
    *,
    data: pl.DataFrame,
    x_column: str,
    y_column: str,
    kind: Literal["reg", "cat"] = "reg",
    top_k_column: str = "num_votes",
    top_k: int | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    title: str | bool | None = None,
    x_label: str | bool | None = None,
    y_label: str | bool | None = None,
    invert_x: bool = False,
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
        plot_kwargs.setdefault(
            "order",
            data.group_by(y_column)
            .agg(pl.col(x_column).mean())
            .sort(x_column)[y_column],
        )
        sns.violinplot(**plot_kwargs)
    else:
        raise ValueError(f"Unknown kind: {kind}")

    ax.set_title(None if title is False else (title or f"{y_column} vs {x_column}"))
    ax.set_xlabel(None if x_label is False else (x_label or x_column))
    ax.set_ylabel(None if y_label is False else (y_label or y_column))

    if invert_x:
        ax.invert_xaxis()

    return ax


def animate(
    *,
    path: str | Path,
    data: pl.DataFrame,
    x_column: str,
    y_column: str,
    kind: Literal["reg", "cat"] = "reg",
    top_k_column: str = "num_votes",
    top_k: int | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    title: str | bool | None = None,
    x_label: str | bool | None = None,
    y_label: str | bool | None = None,
    invert_x: bool = False,
    plot_kwargs: dict[str, any] | None = None,
    fps: int = 25,
    duration: float = 2.0,
    dpi: int = 100,
    progress: bool = False,
):
    if top_k and top_k_column:
        data = data.top_k(by=top_k_column, k=top_k)

    y_column_debiased = f"{y_column}_debiased"
    assert y_column_debiased in data.columns, f"Column {y_column_debiased} not found"
    y_column_weighted = f"{y_column}_weighted"

    y_min = data.select(
        pl.min_horizontal(
            pl.col(y_column).quantile(0.01),
            pl.col(y_column_debiased).quantile(0.01),
        ),
    ).item()
    y_max = data.select(
        pl.max_horizontal(
            pl.col(y_column).quantile(0.99),
            pl.col(y_column_debiased).quantile(0.99),
        ),
    ).item()

    alphas = np.linspace(0.0, 1.0, int(duration * fps))
    if progress:
        alphas = tqdm(alphas)

    writer = animation.PillowWriter(fps=fps)
    fig, ax = plt.subplots(figsize=figsize)
    with writer.saving(fig=fig, outfile=path, dpi=dpi):
        for alpha in alphas:
            ax.clear()
            plot(
                data=data.with_columns(
                    (
                        (1 - alpha) * pl.col(y_column)
                        + alpha * pl.col(y_column_debiased)
                    ).alias(y_column_weighted),
                ),
                x_column=x_column,
                y_column=y_column_weighted,
                kind=kind,
                seed=seed,
                title=title,
                x_label=x_label,
                y_label=y_label,
                invert_x=invert_x,
                plot_kwargs=plot_kwargs,
                ax=ax,
            )
            plt.tight_layout()
            plt.ylim(y_min, y_max)
            writer.grab_frame()
    plt.close()


def save_plot(
    *,
    data: pl.DataFrame,
    x_column: str,
    y_column: str,
    kind: Literal["reg", "cat"] = "reg",
    path: str | Path | None = None,
    top_k_column: str = "num_votes",
    top_k: int | None = None,
    figsize: tuple[int, int] | None = None,
    seed: int | None = None,
    title: str | bool | None = None,
    x_label: str | bool | None = None,
    y_label: str | bool | None = None,
    invert_x: bool = False,
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
        invert_x=invert_x,
        plot_kwargs=plot_kwargs,
    )

    plt.tight_layout()
    if path:
        plt.savefig(path.parent / f"{path.stem}_{kind}.png")
        plt.savefig(path.parent / f"{path.stem}_{kind}.svg")
    if show:
        plt.show()
    plt.close()
