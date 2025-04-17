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
import jupyter_black
from parsel import Selector

jupyter_black.load()

# %%
# Load HTML file
with open("results/snooker/oddschecker.html", encoding="utf-8") as f:
    html = f.read()

# %%
selector = Selector(text=html)

for row in selector.css("tr.diff-row"):
    name = row.xpath("@data-bname").get()
    print(name)

    odds = {
        td.xpath("@data-bk").get(): float(td.xpath("@data-odig").get())
        for td in row.xpath("td[@data-bk and @data-odig]")
    }

    print(odds)
    print(max(odds.values()))
    print()
