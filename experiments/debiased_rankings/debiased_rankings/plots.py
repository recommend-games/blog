import logging
from pathlib import Path
from typing import Literal
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import animation, colors as mcolors, pyplot as plt
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
    clip_quantiles: tuple[float, float] | None = None,
    invert_x: bool = False,
    plot_kwargs: dict[str, any] | None = None,
    ax: Axes | None = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if top_k and top_k_column:
        data = data.top_k(by=top_k_column, k=top_k)

    plot_kwargs = plot_kwargs.copy() if plot_kwargs else {}
    plot_kwargs["data"] = data
    plot_kwargs["x"] = x_column
    plot_kwargs["y"] = y_column
    plot_kwargs.setdefault("color", "purple")
    plot_kwargs["ax"] = ax

    if kind == "reg":
        alphas = data.select(
            pl.max_horizontal(
                pl.col(top_k_column) / pl.max(top_k_column),
                0.01,
            ),
        )[top_k_column]
        colors = mcolors.to_rgba_array(c=plot_kwargs.pop("color"), alpha=alphas)
        sns.regplot(
            **plot_kwargs,
            scatter_kws={
                "color": colors,
                "s": 10,
            },
            line_kws={
                "lw": 3,
                "color": "crimson",
            },
            seed=seed,
        )
        if clip_quantiles:
            plt.ylim(
                data.select(pl.col(y_column).quantile(clip_quantiles[0])).item(),
                data.select(pl.col(y_column).quantile(clip_quantiles[1])).item(),
            )
    elif kind == "cat":
        plot_kwargs.setdefault(
            "order",
            data.group_by(y_column)
            .agg(pl.col(x_column).mean())
            .sort(x_column)[y_column],
        )
        sns.violinplot(**plot_kwargs)
        if clip_quantiles:
            plt.xlim(
                data.select(pl.col(x_column).quantile(clip_quantiles[0])).item(),
                data.select(pl.col(x_column).quantile(clip_quantiles[1])).item(),
            )
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
    clip_quantiles: tuple[float, float] | None = None,
    plot_kwargs: dict[str, any] | None = None,
    fps: int = 25,
    duration_pre: float | None = None,
    duration_main: float = 2.0,
    duration_post: float | None = None,
    dpi: int = 100,
    progress: bool = False,
):
    if top_k and top_k_column:
        data = data.top_k(by=top_k_column, k=top_k)

    column = y_column if kind == "reg" else x_column
    column_debiased = f"{column}_debiased"
    assert column_debiased in data.columns, f"Column {column_debiased} not found"
    column_weighted = f"{column}_weighted"

    if clip_quantiles:
        min_value = data.select(
            pl.min_horizontal(
                pl.col(column).quantile(clip_quantiles[0]),
                pl.col(column_debiased).quantile(clip_quantiles[0]),
            ),
        ).item()
        max_value = data.select(
            pl.max_horizontal(
                pl.col(column).quantile(clip_quantiles[1]),
                pl.col(column_debiased).quantile(clip_quantiles[1]),
            ),
        ).item()
    else:
        min_value, max_value = None, None

    alphas = np.linspace(0.0, 1.0, int(duration_main * fps))
    if progress:
        alphas = tqdm(alphas)

    if plot_kwargs:
        plot_kwargs = plot_kwargs.copy()
        plot_kwargs.pop("x_jitter", None)
        plot_kwargs.pop("y_jitter", None)
    else:
        plot_kwargs = {}

    if kind == "cat":
        plot_kwargs.setdefault(
            "order",
            data.group_by(y_column)
            .agg(pl.col(x_column).mean())
            .sort(x_column)[y_column],
        )

    writer = animation.PillowWriter(fps=fps)
    fig, ax = plt.subplots(figsize=figsize)
    LOGGER.info("Animating %s plot to <%s>", kind, path)
    with writer.saving(fig=fig, outfile=path, dpi=dpi):
        if duration_pre:
            ax.clear()
            plot(
                data=data,
                x_column=x_column,
                y_column=y_column,
                kind=kind,
                seed=seed,
                title=title,
                x_label=x_label,
                y_label=y_label,
                invert_x=invert_x,
                plot_kwargs=plot_kwargs,
                ax=ax,
            )
            if min_value is not None and max_value is not None:
                if kind == "reg":
                    plt.ylim(min_value, max_value)
                else:
                    plt.xlim(min_value, max_value)
            plt.tight_layout()
            for _ in range(int(duration_pre * fps)):
                writer.grab_frame()
        for alpha in alphas:
            ax.clear()
            plot(
                data=data.with_columns(
                    (
                        (1 - alpha) * pl.col(column) + alpha * pl.col(column_debiased)
                    ).alias(column_weighted),
                ),
                x_column=x_column if kind == "reg" else column_weighted,
                y_column=column_weighted if kind == "reg" else y_column,
                kind=kind,
                seed=seed,
                title=title,
                x_label=x_label,
                y_label=y_label,
                invert_x=invert_x,
                plot_kwargs=plot_kwargs,
                ax=ax,
            )
            if min_value is not None and max_value is not None:
                if kind == "reg":
                    plt.ylim(min_value, max_value)
                else:
                    plt.xlim(min_value, max_value)
            plt.tight_layout()
            writer.grab_frame()
        if duration_post:
            ax.clear()
            plot(
                data=data,
                x_column=x_column if kind == "reg" else column_debiased,
                y_column=column_debiased if kind == "reg" else y_column,
                kind=kind,
                seed=seed,
                title=title,
                x_label=x_label,
                y_label=y_label,
                invert_x=invert_x,
                plot_kwargs=plot_kwargs,
                ax=ax,
            )
            if min_value is not None and max_value is not None:
                if kind == "reg":
                    plt.ylim(min_value, max_value)
                else:
                    plt.xlim(min_value, max_value)
            plt.tight_layout()
            for _ in range(int(duration_post * fps)):
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
    clip_quantiles: tuple[float, float] | None = None,
    plot_kwargs: dict[str, any] | None = None,
    show: bool = False,
    save_animation: bool = False,
    progress: bool = False,
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
        clip_quantiles=clip_quantiles,
        plot_kwargs=plot_kwargs,
    )

    plt.tight_layout()
    if path:
        plt.savefig(path.parent / f"{path.stem}_{kind}.png")
        plt.savefig(path.parent / f"{path.stem}_{kind}.svg")
    if show:
        plt.show()
    plt.close()

    if save_animation and path:
        animate(
            path=path.parent / f"{path.stem}_{kind}_animated.gif",
            data=data,
            x_column=x_column,
            y_column=y_column,
            kind=kind,
            top_k_column=top_k_column,
            top_k=top_k * 10 if top_k else None,
            figsize=figsize,
            seed=seed,
            title=title,
            x_label=x_label,
            y_label=y_label,
            invert_x=invert_x,
            clip_quantiles=clip_quantiles,
            plot_kwargs=plot_kwargs,
            progress=progress,
            duration_pre=1.0,
            duration_main=2.0,
            duration_post=2.0,
        )
