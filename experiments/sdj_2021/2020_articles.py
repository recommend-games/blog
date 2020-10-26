# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import csv
import re

from pathlib import Path

# %load_ext nb_black
# %load_ext lab_black

# %%
regex = re.compile(r"\{\{% game (\d+) %\}\}([^{]+)\{\{% /game %\}\}")

# %%
directory = Path("../../content/posts/").resolve()

# %%
for path in directory.glob("sdj*/*.md"):
    with path.open() as file:
        for line in file:
            for match in regex.finditer(line):
                print(match.group(1), match.group(2))
