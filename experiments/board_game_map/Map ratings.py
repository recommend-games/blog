# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json
import math
from collections import defaultdict
from functools import reduce
from operator import or_

import jupyter_black
import numpy as np
import polars as pl
import polars.selectors as cs
import seaborn as sns
import umap
from bokeh.embed import json_item
from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.transform import jitter
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE

jupyter_black.load()
output_notebook()

# %% [markdown]
# ## Game types

# %%
rankings = pl.read_csv("data/boardgames_ranks.csv")
rankings.shape

# %%
rankings.head()

# %%
columns = rankings.select(cs.ends_with("_rank")).columns
columns_map = {i: col[:-5] for i, col in enumerate(columns)}
columns_map

# %%
game_types = (
    rankings.filter(reduce(or_, (pl.col(col).is_not_null() for col in columns)))
    .with_columns(cs.ends_with("_rank") / cs.ends_with("_rank").max())
    .fill_null(math.inf)
    .select(
        bgg_id="id",
        name="name",
        num_ratings="usersrated",
        game_type=pl.concat_list(columns).list.arg_min().replace(columns_map),
    )
)
game_types.shape

# %%
game_types.select(pl.col("game_type").value_counts(sort=True))

# %% [markdown]
# ## Latent vectors

# %%
with open("data/recommender_light.npz", "rb") as f:
    files = np.load(file=f)
    items_labels = files["items_labels"]
    items_factors = files["items_factors"]
items_indexes = defaultdict(
    lambda: -1,
    zip(items_labels, range(len(items_labels))),
)

# %%
idxs = np.array([items_indexes[bgg_id] for bgg_id in game_types["bgg_id"]])
idxs.shape, (idxs < 0).sum()
# TODO: Filter out idx -1

# %%
latent_vectors = items_factors[:, idxs].T
latent_vectors.shape

# %% [markdown]
# ## Embeddings

# %% [markdown]
# ### t-SNE

# %%
tsne_embedding = TSNE(
    n_components=2,
    perplexity=30,
    early_exaggeration=12,
    metric="cosine",
    init="pca",
    learning_rate="auto",
)

# %%
latent_vectors_tsne_embedded = tsne_embedding.fit_transform(latent_vectors)
latent_vectors_tsne_embedded.shape

# %%
sns.scatterplot(
    x=latent_vectors_tsne_embedded[:, 0],
    y=latent_vectors_tsne_embedded[:, 1],
    hue=game_types["game_type"],
)
plt.axis("off")
plt.title("t-SNE")
plt.legend(title="Game type", bbox_to_anchor=(1, 0.5), loc="center left")
plt.tight_layout()
plt.savefig("plots/ratings_tsne.svg")
plt.savefig("plots/ratings_tsne.png")
plt.show()

# %%
source_tsne = game_types.clone().with_columns(
    x=latent_vectors_tsne_embedded[:, 0],
    y=latent_vectors_tsne_embedded[:, 1],
    size=pl.col("num_ratings").log(10) * 2 + 1,
    color=pl.col("game_type").replace(
        old=list(columns_map.values()),
        new=sns.color_palette("bright", len(columns_map)).as_hex(),
        default=None,
    ),
)
source_tsne.shape

# %%
TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save,box_select"
plot_tsne = figure(
    title="t-SNE",
    tools=TOOLS,
    tooltips=[
        ("Name", "@name"),
        ("ID", "@bgg_id"),
        ("Type", "@game_type"),
        ("Num ratings", "@num_ratings"),
    ],
)
plot_tsne.scatter(
    x=jitter("x", width=0.25, distribution="normal"),
    y=jitter("y", width=0.25, distribution="normal"),
    size="size",
    source=source_tsne.to_pandas(),
    color="color",
    alpha=0.5,
)
show(plot_tsne)

# %%
with open("plots/ratings_tsne.json", "w") as f:
    json.dump(json_item(plot_tsne), f, indent=4)

# %% [markdown]
# ### UMAP

# %%
umap_embedding = umap.UMAP(
    init="spectral",
    learning_rate=1.0,
    local_connectivity=1.0,
    low_memory=False,
    metric="cosine",
    min_dist=0.1,
    n_components=2,
    n_epochs=None,
    n_neighbors=15,
    negative_sample_rate=5,
    output_metric="euclidean",
    output_metric_kwds=None,
    random_state=13,
)

# %%
latent_vectors_umap_embedded = umap_embedding.fit_transform(latent_vectors)
latent_vectors_umap_embedded.shape

# %%
sns.scatterplot(
    x=latent_vectors_umap_embedded[:, 0],
    y=latent_vectors_umap_embedded[:, 1],
    hue=game_types["game_type"],
)
plt.axis("off")
plt.title("UMAP")
plt.legend(title="Game type", bbox_to_anchor=(1, 0.5), loc="center left")
plt.tight_layout()
plt.savefig("plots/ratings_umap.svg")
plt.savefig("plots/ratings_umap.png")
plt.show()

# %%
source_umap = game_types.clone().with_columns(
    x=latent_vectors_umap_embedded[:, 0],
    y=latent_vectors_umap_embedded[:, 1],
    size=pl.col("num_ratings").log(10) * 2 + 1,
    color=pl.col("game_type").replace(
        old=list(columns_map.values()),
        new=sns.color_palette("bright", len(columns_map)).as_hex(),
        default=None,
    ),
)
source_umap.shape

# %%
TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save,box_select"
plot_umap = figure(
    title="UMAP",
    tools=TOOLS,
    tooltips=[
        ("Name", "@name"),
        ("ID", "@bgg_id"),
        ("Type", "@game_type"),
        ("Num ratings", "@num_ratings"),
    ],
)
plot_umap.scatter(
    x=jitter("x", width=0.25, distribution="normal"),
    y=jitter("y", width=0.25, distribution="normal"),
    size="size",
    source=source_umap.to_pandas(),
    color="color",
    alpha=0.5,
)
show(plot_umap)

# %%
with open("plots/ratings_umap.json", "w") as f:
    json.dump(json_item(plot_umap), f, indent=4)
