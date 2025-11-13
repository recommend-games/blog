# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
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
with open("../results/snooker/oddschecker.html", encoding="utf-8") as f:
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
name_mapping = {
    "Allister Carter": "Ali Carter",
    "Barry Hawkins": "Barry Hawkins",
    "Ben Woollaston": "Ben Woollaston",
    "Chris Wakelin": "Chris Wakelin",
    "Daniel Wells": "Daniel Wells",
    "David Gilbert": "David Gilbert",
    "Ding Junhui": "Ding Junhui",
    "Fan Zhengyi": "Fan Zhengyi",
    "Hossein Vafaei": "Hossein Vafaei",
    "Jak Jones": "Jak Jones",
    "Joe OConnor": "Joe O'Connor",
    "John Higgins": "John Higgins",
    "Judd Trump": "Judd Trump",
    "Kyren Wilson": "Kyren Wilson",
    "Peifan Lei": "Lei Peifan",
    "Luca Brecel": "Luca Brecel",
    "Mark Allen": "Mark Allen",
    "Mark Selby": "Mark Selby",
    "Mark Williams": "Mark Williams",
    "Matthew Selt": "Matthew Selt",
    "Neil Robertson": "Neil Robertson",
    "Pang Junxu": "Pang Junxu",
    "Ronnie OSullivan": "Ronnie O'Sullivan",
    "Ryan Day": "Ryan Day",
    "Shaun Murphy": "Shaun Murphy",
    "Si Jiahui": "Si Jiahui",
    "Wu Yize": "Wu Yize",
    "Xiao Guodong": "Xiao Guodong",
    "Zak Surety": "Zak Surety",
    "Zhang Anda": "Zhang Anda",
    "Zhao Xintong": "Zhao Xintong",
    "Zhou Yuelong": "Zhou Yuelong",
}

# %%
odds = (
    pl.DataFrame(odds_list)
    .select("Name", "BestOdds", pl.exclude("Name", "BestOdds"))
    .with_columns(pl.col("Name").replace(name_mapping))
    .sort("BestOdds")
)
odds.shape

# %%
odds

# %%
odds.write_csv("../csv/snooker/wsc_odds.csv")
