# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Living Forest card costs

# %%
import pandas as pd
from sklearn.linear_model import LinearRegression

pd.options.display.max_columns = 150
pd.options.display.max_rows = 150

# %load_ext nb_black
# %load_ext lab_black

# %% [markdown]
# ## Data

# %%
data = pd.read_csv("cards.csv", index_col="name")
data["flames"] = data["stage"] + 1
data.shape

# %%
data.sample(10)

# %% [markdown]
# ## Model training

# %%
elements = ["white", "sun", "water", "plant", "spiral", "lotus"]
X = data[elements]
y = data["price"]
X.shape, y.shape

# %%
model = LinearRegression(fit_intercept=True)
model.fit(X, y)

# %%
model.intercept_

# %%
for element, price in zip(elements, model.coef_):
    print(f"{element}:\t{price:6.3f}")

# %% [markdown]
# ## Over and underpriced cards

# %%
data["over_price"] = data["price"] - model.predict(data[elements])
data.sort_values("over_price")

# %%
# TODO what would be the costs of starting cards?
