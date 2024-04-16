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
from pathlib import Path
import jupyter_black
import polars as pl
import umap
from bokeh.embed import json_item
from bokeh.io import output_notebook
from bokeh.plotting import show
from sklearn.feature_extraction.text import CountVectorizer  # TfidfVectorizer
from sklearn.manifold import TSNE
from board_game_map.data import process_game_data
from board_game_map.plots import plot_embedding

jupyter_black.load()
output_notebook()

PROJECT_DIR = Path(".").resolve()
BASE_DIR = PROJECT_DIR.parent.parent

# %%
data_dir = PROJECT_DIR / "data"
plot_dir = PROJECT_DIR / "plots" / "games_by_mechanics"
plot_dir.mkdir(parents=True, exist_ok=True)
data_dir, plot_dir

# %% [markdown]
# ## Game types

# %%
rankings = pl.read_csv(data_dir / "boardgames_ranks.csv")
rankings.shape

# %%
game_types = process_game_data(rankings)
game_types.shape

# %%
game_types.select(pl.col("game_type").value_counts(sort=True))

# %% [markdown]
# ## Mechanics

# %%
games_file = BASE_DIR.parent / "board-game-data" / "scraped" / "bgg_GameItem.csv"
games_data = (
    pl.scan_csv(games_file)
    .select("bgg_id", "mechanic")
    .drop_nulls()
    .join(game_types.lazy(), on="bgg_id", how="inner")
    .collect()
)
games_data.shape

# %%
games_data.head()

# %%
cv = CountVectorizer(binary=True)
mechanics = cv.fit_transform(games_data["mechanic"])
mechanics.shape

# %% [markdown]
# ## Embeddings

# %% [markdown]
# ### t-SNE

# %%
tsne_embedding = TSNE(
    n_components=2,
    perplexity=30,
    early_exaggeration=12,
    metric="jaccard",
    init="pca",
    learning_rate="auto",
)

# %%
mechanics_tsne_embedded = tsne_embedding.fit_transform(mechanics.toarray())
mechanics_tsne_embedded.shape

# %%
plot_tsne = plot_embedding(
    data=games_data,
    latent_vectors=mechanics_tsne_embedded,
    title="t-SNE",
)
show(plot_tsne)

# %%
with (plot_dir / "tsne.json").open("w") as f:
    json.dump(json_item(plot_tsne), f, indent=4)

# %% [markdown]
# ### UMAP

# %%
umap_embedding = umap.UMAP(
    init="spectral",
    learning_rate=1.0,
    local_connectivity=1.0,
    low_memory=False,
    metric="jaccard",
    min_dist=0.1,
    n_components=2,
    n_epochs=None,
    n_neighbors=15,
    negative_sample_rate=5,
    output_metric="euclidean",
    output_metric_kwds=None,
    random_state=None,
)

# %%
mechanics_umap_embedded = umap_embedding.fit_transform(mechanics)
mechanics_umap_embedded.shape

# %%
plot_umap = plot_embedding(
    data=games_data,
    latent_vectors=mechanics_umap_embedded,
    title="UMAP",
)
show(plot_umap)

# %%
with (plot_dir / "umap.json").open("w") as f:
    json.dump(json_item(plot_umap), f, indent=4)
