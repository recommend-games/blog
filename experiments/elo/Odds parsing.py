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
import polars as pl
from parsel import Selector

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
# Load HTML file
with open("results/snooker/oddschecker.html", encoding="utf-8") as f:
    html = f.read()

# %%
selector = Selector(text=html)

odds_list = []

for row in selector.css("tr.diff-row"):
    name = row.xpath("@data-bname").get()

    result = {
        td.xpath("@data-bk").get(): float(td.xpath("@data-odig").get())
        for td in row.xpath("td[@data-bk and @data-odig]")
    }
    best_odds = max(result.values())
    result["Name"] = name
    result["BestOdds"] = best_odds

    odds_list.append(result)

len(odds_list)

# %%
odds = (
    pl.DataFrame(odds_list)
    .select("Name", "BestOdds", pl.exclude("Name", "BestOdds"))
    .sort("BestOdds")
)
odds.shape

# %%
odds

# %%
odds.write_csv("results/snooker/wsc_odds.csv")
