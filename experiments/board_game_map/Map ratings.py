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
import jupyter_black
import polars as pl
import umap
from bokeh.embed import json_item
from bokeh.io import output_notebook
from bokeh.plotting import show
from sklearn.decomposition import FactorAnalysis, FastICA, PCA
from sklearn.manifold import Isomap, LocallyLinearEmbedding, SpectralEmbedding, TSNE
from board_game_map.data import load_latent_vectors,process_game_data
from board_game_map.plots import plot_embedding

jupyter_black.load()
output_notebook()

# %% [markdown]
# ## Game types

# %%
rankings = pl.read_csv("data/boardgames_ranks.csv")
rankings.shape

# %%
game_types = process_game_data(rankings)
game_types.shape

# %%
game_types.select(pl.col("game_type").value_counts(sort=True))

# %% [markdown]
# ## Latent vectors

# %%
latent_vectors = load_latent_vectors("data/recommender_light.npz", game_types["bgg_id"])
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
plot_tsne = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_tsne_embedded,
    title="t-SNE",
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
    random_state=None,
)

# %%
latent_vectors_umap_embedded = umap_embedding.fit_transform(latent_vectors)
latent_vectors_umap_embedded.shape

# %%
plot_umap = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_umap_embedded,
    title="UMAP",
)
show(plot_umap)

# %%
with open("plots/ratings_umap.json", "w") as f:
    json.dump(json_item(plot_umap), f, indent=4)

# %% [markdown]
# ### Isomap

# %%
isomap_embedding = Isomap(n_components=2, metric="cosine")

# %%
latent_vectors_isomap_embedded = isomap_embedding.fit_transform(latent_vectors)
latent_vectors_isomap_embedded.shape

# %%
plot_isomap = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_isomap_embedded,
    title="Isomap",
)
show(plot_isomap)

# %%
with open("plots/ratings_isomap.json", "w") as f:
    json.dump(json_item(plot_isomap), f, indent=4)

# %% [markdown]
# ### Spectral embedding

# %%
spectral_embedding = SpectralEmbedding(n_components=2)

# %%
latent_vectors_spectral_embedded = spectral_embedding.fit_transform(latent_vectors)
latent_vectors_spectral_embedded.shape

# %%
plot_spectral = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_spectral_embedded,
    title="Spectral embedding",
)
show(plot_spectral)

# %%
with open("plots/ratings_spectral.json", "w") as f:
    json.dump(json_item(plot_spectral), f, indent=4)

# %% [markdown]
# ### Locally linear embedding

# %%
locally_linear_embedding = LocallyLinearEmbedding(n_components=2)

# %%
latent_vectors_locally_linearly_embedded = locally_linear_embedding.fit_transform(
    latent_vectors,
)
latent_vectors_locally_linearly_embedded.shape

# %%
plot_locally_linear = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_locally_linearly_embedded,
    title="Locally linear embedding",
)
show(plot_locally_linear)

# %%
with open("plots/ratings_locally_linear.json", "w") as f:
    json.dump(json_item(plot_locally_linear), f, indent=4)

# %% [markdown]
# ### PCA

# %%
pca_embedding = PCA(n_components=2)

# %%
latent_vectors_pca_embedded = pca_embedding.fit_transform(latent_vectors)
latent_vectors_pca_embedded.shape

# %%
plot_pca = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_pca_embedded,
    title="PCA",
)
show(plot_pca)

# %%
with open("plots/ratings_pca.json", "w") as f:
    json.dump(json_item(plot_pca), f, indent=4)

# %% [markdown]
# ### FastICA

# %%
fastica_embedding = FastICA(n_components=2)

# %%
latent_vectors_fastica_embedded = fastica_embedding.fit_transform(latent_vectors)
latent_vectors_fastica_embedded.shape

# %%
plot_fastica = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_fastica_embedded,
    title="FastICA",
)
show(plot_fastica)

# %%
with open("plots/ratings_fastica.json", "w") as f:
    json.dump(json_item(plot_fastica), f, indent=4)

# %% [markdown]
# ### Factor analysis

# %%
factor_analysis_embedding = FactorAnalysis(n_components=2)

# %%
latent_vectors_factor_analysis_embedded = factor_analysis_embedding.fit_transform(
    latent_vectors,
)
latent_vectors_factor_analysis_embedded.shape

# %%
plot_factor_analysis = plot_embedding(
    data=game_types,
    latent_vectors=latent_vectors_factor_analysis_embedded,
    title="Factor analysis",
)
show(plot_factor_analysis)

# %%
with open("plots/ratings_factor_analysis.json", "w") as f:
    json.dump(json_item(plot_factor_analysis), f, indent=4)