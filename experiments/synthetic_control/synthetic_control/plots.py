import math

import seaborn as sns
from matplotlib import pyplot as plt

sns.set_style("dark")


def plot_ratings(data, game, y_pred=None, ax=None):
    if ax is None:
        _, ax = plt.subplots()

    sns.lineplot(
        x=data["timestamp"],
        y=data[str(game.bgg_id)],
        label=game.name,
        color="purple",
        lw=3,
        ax=ax,
    )

    if y_pred is not None:
        sns.lineplot(
            x=data["timestamp"],
            y=y_pred,
            label="Synthetic Control",
            color="crimson",
            lw=3,
            ax=ax,
        )
        y_pred_min = y_pred.min()
        y_pred_max = y_pred.max()

    else:
        y_pred_min = math.inf
        y_pred_max = -math.inf

    ax.vlines(
        x=game.date_review,
        ymin=min(data[str(game.bgg_id)].min(), y_pred_min),
        ymax=max(data[str(game.bgg_id)].max(), y_pred_max),
        label="SU&SD video",
        linestyle=":",
        color="purple",
        lw=2,
    )

    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_xlabel(None)
    ax.set_ylabel("Num Ratings")
    ax.set_title(None)
    ax.legend()

    return ax
