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
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE

jupyter_black.load()

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

# %%
latent_vectors = items_factors[:, idxs].T
latent_vectors.shape

# %% [markdown]
# ## Embeddings

# %% [markdown]
# ### t-SNE

# %%
embedding = TSNE(
    n_components=2,
    perplexity=30,
    early_exaggeration=12,
    metric="cosine",
    init="pca",
    learning_rate="auto",
)

# %%
latent_vectors_embedded = embedding.fit_transform(latent_vectors)
latent_vectors_embedded.shape

# %%
sns.scatterplot(
    x=latent_vectors_embedded[:, 0],
    y=latent_vectors_embedded[:, 1],
    hue=game_types["game_type"],
)
plt.axis("off")
plt.legend(title="Game type", bbox_to_anchor=(1, 0.5), loc="center left")

# %% [markdown]
# ### UMAP

# %%
embedding = umap.UMAP(
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
)

# %%
latent_vectors_embedded = embedding.fit_transform(latent_vectors)
latent_vectors_embedded.shape

# %%
sns.scatterplot(
    x=latent_vectors_embedded[:, 0],
    y=latent_vectors_embedded[:, 1],
    hue=game_types["game_type"],
)
plt.axis("off")
plt.legend(title="Game type", bbox_to_anchor=(1, 0.5), loc="center left")
