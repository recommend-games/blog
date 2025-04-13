# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
import jupyter_black
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

jupyter_black.load()
sns.set_style("dark")

# %%
plot_dir = (Path(".") / "plots").resolve()
plot_dir.mkdir(parents=True, exist_ok=True)
plot_dir

# %%
x = np.linspace(-5, 5, 10_000)
y = 1 / (1 + np.exp(-x))

_, ax = plt.subplots(figsize=(6, 4))
ax.spines["left"].set_position("zero")
ax.spines["left"].set_color("black")
ax.spines["bottom"].set_position("zero")
ax.spines["bottom"].set_color("black")
ax.spines["right"].set_color(None)
ax.spines["top"].set_color(None)
ax.xaxis.set_ticks_position("bottom")
ax.yaxis.set_ticks_position("left")
ax.grid(True, which="both", linestyle="--", linewidth=0.5)
sns.lineplot(x=x, y=y, color="purple", lw=3, ax=ax)
ax.set_title("Sigmoid")
ax.set_xlabel(None)
ax.set_ylabel(None)
plt.tight_layout()
plt.savefig(plot_dir / "sigmoid.png")
plt.savefig(plot_dir / "sigmoid.svg")
plt.show()
