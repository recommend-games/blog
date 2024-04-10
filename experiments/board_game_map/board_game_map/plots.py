import numpy as np
import polars as pl
import seaborn as sns
from bokeh.plotting import figure
from bokeh.transform import jitter

TOOLS = "hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save,box_select"


def plot_embedding(
    data: pl.DataFrame,
    latent_vectors: np.ndarray,
    *,
    title: str | None = None,
    tools: str = TOOLS,
) -> figure:
    assert latent_vectors.shape == (
        len(data),
        2,
    ), "Latent vectors must have shape (n, 2)"

    game_types = data["game_type"].unique().sort()

    source = data.with_columns(
        x=latent_vectors[:, 0].tolist(),
        y=latent_vectors[:, 1].tolist(),
        size=pl.col("num_ratings").log(10) * 2 + 1,
        color=pl.col("game_type").replace(
            old=game_types,
            new=sns.color_palette("bright", len(game_types)).as_hex(),
            default=None,
        ),
    )

    plot = figure(
        title=title,
        tools=tools,
        tooltips=[
            ("Name", "@name"),
            ("ID", "@bgg_id"),
            ("Type", "@game_type"),
            ("Num ratings", "@num_ratings"),
        ],
    )

    plot.scatter(
        x=jitter("x", width=0.25, distribution="normal"),
        y=jitter("y", width=0.25, distribution="normal"),
        size="size",
        source=source.to_pandas(),
        color="color",
        alpha=0.5,
    )

    plot.axis.visible = False
    plot.grid.visible = False

    return plot
