# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
import json

from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.embed import json_item
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    Span,
    CDSView,
    GroupFilter,
    Label,
    LabelSet,
    NumeralTickFormatter,
)

jupyter_black.load()

output_notebook()
pl.Config.set_tbl_rows(100)
pl.Config.set_tbl_width_chars(100)
pl.Config.set_fmt_str_lengths(100)

seed = 13

# %%
columns = [
    "bga_id",
    "bgg_id",
    "display_name_en",
    "games_played",
    "num_all_matches",
    "ratio",
    "num_regular_players",
    "premium",
    "is_ranking_disabled",
    "locked",
    "elo_k",
    "std_dev",
    "p_deterministic",
    "rank",
    "avg_rating",
    "bayes_rating",
    "num_votes",
    "year",
    "complexity",
    "cooperative",
    "game_type",
]
len(columns)

# %%
bga = pl.scan_ndjson("../csv/games.jl").rename({"id": "bga_id"})
id_mapping = pl.scan_csv("../csv/bga_bgg_map.csv")
skills = (
    pl.scan_csv("../csv/game_skills.csv")
    .with_columns(pl.col("game_id").str.to_integer(strict=False).alias("bga_id"))
    .drop_nulls("bga_id")
)
bgg = pl.scan_ndjson("~/Recommend.Games/board-game-data/scraped/v3/bgg_GameItem.jl")
bgg_types = (
    bgg.select("bgg_id", "add_rank")
    .explode("add_rank")
    .unnest("add_rank")
    .group_by("bgg_id")
    .agg(
        game_type=pl.col("name")
        .sort_by("rank", "bayes_rating", descending=[False, True], nulls_last=True)
        .first()
    )
)
all_games = (
    bga.join(id_mapping, on="bga_id", how="left")
    .with_columns(pl.coalesce("bgg_id_right", "bgg_id").alias("bgg_id"))
    .drop("bgg_id_right", "name_right")
    .join(
        skills,
        on="bga_id",
        how="full",
        coalesce=True,
    )
    .with_columns(pl.coalesce("bgg_id", "bgg_id_right"))
    .drop("bgg_id_right", "name_right")
    .join(bgg, how="left", on="bgg_id", coalesce=True)
    .drop("game_type")
    .join(bgg_types, how="left", on="bgg_id", coalesce=True)
    .with_columns(
        ratio=pl.col("num_all_matches").fill_null(0) / pl.col("games_played"),
    )
    .select(columns)
    .with_columns(
        pl.col(pl.Boolean).fill_null(False),
        pl.col("game_type").fill_null("Uncategorized"),
    )
    .collect()
)
all_games.shape

# %%
all_games.sample(10, seed=seed)

# %%
all_games.describe()

# %%
df = (
    all_games.remove(pl.col("bgg_id").is_null())
    .remove(pl.len().over("bgg_id") > 1)
    .remove(pl.col("num_regular_players") < 100)
    .remove(pl.col("is_ranking_disabled") & pl.col("cooperative"))
)
df.shape

# %%
df.sample(10, seed=seed)

# %%
df.describe()

# %%
plot_df = df.remove(pl.col("num_votes") < 1000)
plot_df.shape


# %%
def format_int_col(col: str) -> pl.Expr:
    return (
        pl.when(pl.col(col) >= 10_000)
        .then(
            (pl.col(col) // 1000).map_elements(
                lambda v: f"{v:,}k",
                return_dtype=pl.String,
            ),
        )
        .otherwise(
            pl.col(col).map_elements(
                lambda v: f"{v:,}",
                return_dtype=pl.String,
            ),
        )
    )


min_size, max_size = 5, 18
bokeh_columns = [
    "p_deterministic",
    "complexity",
    "size",
    "display_name_en",
    "year",
    "game_type",
    "rank",
    "bayes_rating",
    "num_all_matches",
    "num_regular_players",
]

# Collapsed game type categories and their display order / colours
GAME_TYPE_COLORS = {
    "Family Game": "#4e79a7",  # blue
    "Strategy Game": "#f28e2b",  # orange
    "Abstract Game": "#59a14f",  # green
    "Party Game": "#e15759",  # red
    "Children's Game": "#b07aa1",  # purple
    "Other": "#bab0ac",  # grey — Thematic, War, Customizable, Uncategorized
}
TYPE_COLLAPSE = {
    "Thematic": "Other",
    "War Game": "Other",
    "Customizable": "Other",
    "Uncategorized": "Other",
}

label_games = (
    "7 Wonders Duel",
    "Abalone",
    "Ark Nova",
    "Azul",
    "Backgammon",
    "CATAN",
    # "Can't Stop",
    "Carcassonne",
    "Caylus",
    "Challengers!",
    "Chess",
    "Connect Four",
    # "Copenhagen",
    "Coup",
    "Expeditions: Around the World",
    "Flip 7",
    "Gaia Project",
    # "Go",
    # "Incan Gold",
    "Kingdomino",
    # "LLAMA",
    # "Living Forest",
    "No Thanks!",
    "Panic Lab",
    "Patchwork",
    "Pax Pamir: Second Edition",
    # "Photosynthesis",
    "Poker Texas Hold'em",
    "Race for the Galaxy",
    "Skat",
    # "Skull",
    "Spot it",
    "Stone Age",
    "Terraforming Mars",
    # "The Werewolves of Miller's Hollow",
    # "Tichu",
    "Ubongo",
    "Wingspan",
    "Yahtzee",
)

bokeh_df = (
    plot_df.lazy()
    .drop_nulls(["p_deterministic", "complexity", "num_all_matches"])
    .with_columns(
        game_type=pl.col("game_type").replace(TYPE_COLLAPSE),
        log_matches=pl.col("num_all_matches").clip(1).log10(),
    )
    .with_columns(
        size=min_size
        + (pl.col("log_matches") - pl.col("log_matches").min())
        * (max_size - min_size)
        / (pl.col("log_matches").max() - pl.col("log_matches").min())
    )
    .select(bokeh_columns)
    .sort("num_all_matches")
)

# Fixed order: named types first, Other last — filter to only types actually present
present_types = set(bokeh_df.select(pl.col("game_type").unique()).collect().to_series())
game_types = [gt for gt in GAME_TYPE_COLORS if gt in present_types]

label_cols = ["p_deterministic", "complexity", "display_name_en"]
labels_df = (
    bokeh_df.select(label_cols)
    .filter(pl.col("display_name_en").is_in(label_games))
    .unique("display_name_en")
    .sort("display_name_en")
    .collect()
)

bokeh_df = bokeh_df.with_columns(
    num_all_matches=format_int_col("num_all_matches"),
    num_regular_players=format_int_col("num_regular_players"),
).collect()

source = ColumnDataSource(bokeh_df)
label_source = ColumnDataSource(labels_df)

bokeh_df.shape, len(game_types), labels_df.shape

# %%
p = figure(
    width=900,
    height=550,
    x_axis_label="Skill sensitivity p",
    y_axis_label="BGG complexity",
    tools="pan,wheel_zoom,box_zoom,reset,save",
    title="Skill vs complexity for BGA games",
)

# Median lines
median_p = bokeh_df["p_deterministic"].median()
median_c = bokeh_df["complexity"].median()

p.add_layout(
    Span(
        dimension="height",
        location=median_p,
        line_color="black",
        line_width=1.5,
        line_alpha=0.25,
        line_dash="dotted",
    )
)

p.add_layout(
    Span(
        dimension="width",
        location=median_c,
        line_color="black",
        line_width=1.5,
        line_alpha=0.25,
        line_dash="dotted",
    )
)

# Quadrant labels
x_min = bokeh_df["p_deterministic"].min()
x_max = bokeh_df["p_deterministic"].max()
y_min = bokeh_df["complexity"].min()
y_max = bokeh_df["complexity"].max()

x_left = 0.5 * (x_min + median_p)
x_right = 0.5 * (median_p + x_max)
y_bottom = y_min * 0.9
y_top = y_max

quadrant_labels = [
    (x_left, y_top, "complex but swingy"),
    (x_right, y_top, "complex and skillful"),
    (x_left, y_bottom, "simple and swingy"),
    (x_right, y_bottom, "simple but skillful"),
]

for x_q, y_q, text in quadrant_labels:
    p.add_layout(
        Label(
            x=x_q,
            y=y_q,
            text=text,
            text_align="center",
            text_baseline="middle",
            text_font_size="12pt",
            text_font_style="bold italic",
            text_alpha=0.25,
        )
    )

# One glyph per game_type with a CDSView so we can control legend order explicitly
for gt in game_types:
    view = CDSView(filter=GroupFilter(column_name="game_type", group=gt))
    p.scatter(
        x="p_deterministic",
        y="complexity",
        size="size",
        marker="circle",
        source=source,
        view=view,
        fill_alpha=0.75,
        line_color=None,
        color=GAME_TYPE_COLORS[gt],
        legend_label=gt,
    )

p.add_layout(
    LabelSet(
        x="p_deterministic",
        y="complexity",
        text="display_name_en",
        x_offset=5,
        y_offset=3,
        text_font_size="9pt",
        text_color="black",
        text_font_style="bold",
        text_alpha=0.5,
        background_fill_color="white",
        background_fill_alpha=0.5,
        source=label_source,
    )
)

hover = HoverTool(
    tooltips=[
        ("Game", "@display_name_en (@year)"),
        ("Skill sensitivity p", "@p_deterministic{0%}"),
        ("Complexity", "@complexity{0.0}"),
        ("Game type", "@game_type"),
        ("BGG rank (rating)", "@rank (@bayes_rating{0.0})"),
        ("Number of matches", "@num_all_matches"),
        ("Number of players", "@num_regular_players"),
    ],
)
p.add_tools(hover)

p.legend.location = "top_left"
p.legend.click_policy = "hide"
p.xaxis.formatter = NumeralTickFormatter(format="0%")

show(p)


# %%
# Export interactive plot to JSON for embedding
plot_json_path = "../plots/skill_vs_complexity.json"
with open(plot_json_path, "w") as f:
    json.dump(json_item(p, "skill-vs-complexity"), f, indent=4)
print(f"Exported Bokeh plot JSON to {plot_json_path}")


# %%
plot_df.sort("std_dev", descending=True, nulls_last=True).head(20)

# %%
plot_df.sort("std_dev", descending=False, nulls_last=True).head(20)
