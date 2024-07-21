# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import json
import jupyter_black
from tqdm import tqdm

jupyter_black.load()

# %%
in_path = "../../../board-game-data/scraped/bgg_GameItem.jl"
out_path = "./titles.txt"


# %%
def load_titles(path):
    with open(path, encoding="utf-8") as file:
        for line in file:
            game = json.loads(line)
            if name := game.get("name"):
                yield f"{name}\n"


# %%
titles = load_titles(in_path)
with open(out_path, mode="w", encoding="utf-8") as file:
    file.writelines(tqdm(titles))
