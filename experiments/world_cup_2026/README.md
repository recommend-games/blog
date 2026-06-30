# World Cup 2026 Elo + Poisson predictor

A reproducible Monte Carlo simulator for the 2026 FIFA World Cup, built
around established World Football Elo ratings and a fixed-total Poisson
goal model. The aim is a clear, testable, article-ready first version
rather than an optimised forecasting system. The full design lives in
[`notes/World Cup 2026 Elo + Poisson Prediction Plan.md`](notes/World%20Cup%202026%20Elo%20+%20Poisson%20Prediction%20Plan.md).

This experiment is self-contained inside
`experiments/world_cup_2026/` — all data snapshots, the simulator
source, the runner scripts, the plan document and the published
outputs live here, and `pyproject.toml` pins the only runtime
dependencies (`numpy`, `polars`, `scipy`, `tqdm`).

Outputs cover the full bracket (group stage through the final), per-team
title probabilities, per-fixture score predictions, and a comparison
against a live Polymarket prediction market.

## What the model does

```
Established World Football Elo ratings
    -> Elo expected score per fixture
    -> Poisson scoreline model (lambdas summing to ~2.6)
    -> group-stage simulation
    -> FIFA tie-break ranking
    -> best-third selection + R32 placement (495-row lookup)
    -> knockout simulation (extra time decided by Elo expected score)
    -> per-team round-reaching and title probabilities
```

A single tournament samples 72 group-stage scorelines plus 31 knockout
matches; the Monte Carlo loop runs this end-to-end ten million times
with a fixed seed (`20260611`) so the published outputs are exactly
reproducible.

## Reasoning behind the choices

- **Elo as the team-strength input.** Public ratings from
  eloratings.net already integrate decades of match data, are updated
  daily, and let the simulator avoid a custom rating model. Pre-tournament
  Elo is frozen on snapshot day so a result inside the tournament never
  feeds back into the baseline forecast. The `--conditional` re-run
  (see "Conditional re-run on results so far") deliberately relaxes this:
  it refreshes Elo and pins the played scorelines to re-forecast mid-tournament.
- **Fixed-total Poisson, not bivariate.** A single tunable goal budget
  (default `TOTAL_GOALS = 2.6`) is enough to map Elo expected score onto a
  scoreline distribution. There is no Dixon-Coles correction, no separate
  attack/defence ratings — every uplift on Elo's accuracy is treated as
  out of scope for v1. Lambdas are fitted analytically per Elo gap with
  `scipy.brentq` and cached by rounded Elo difference (≈1200 unique
  keys in practice).
- **Underdog floor + truncated-grid renormalisation.** When the Elo gap
  exceeds what the goal budget can represent, the underdog's λ is pinned
  at `MIN_LAMBDA = 0.25` and the dominant side's λ rises above
  `TOTAL_GOALS - MIN_LAMBDA`. The truncated Poisson PMFs are
  renormalised so the joint grid is a proper distribution. Without this,
  Spain vs Cape Verde used to predict (2.6, 0.0) — Cape Verde literally
  couldn't score.
- **Vectorised group-stage sampling.** All 72 × N_SIMULATIONS group
  goals are drawn in one numpy call before the loop, so the per-sim
  Python work is just ranking + bracket propagation, parallelised across
  CPU cores. The full 10M run takes ≈8 minutes on a 16-core machine.
- **FIFA tie-break ladder, simplified.** Plan §7's full recursive
  resolution is replaced with a composite sort key. The 2026 rules apply
  head-to-head before overall (unlike previous tournaments), so the key is
  H2H points / GD / GF on the tied subset, then overall GD / GF, then
  November-2025 FIFA rank. Card/conduct score is intentionally not modelled.
- **Knockout-tie tie-break by Elo expected score.** Plan §9 deliberately
  avoids modelling extra time and penalties. If 90-minute goals are
  level, the advancing team is drawn from `s_A`, the team-A Elo expected
  score — the same number that drives the Poisson model. This keeps the
  full simulator Elo-consistent.
- **Modal bracket for score predictions.** The simulator marginalises
  over all paths; the per-fixture score predictions instead walk a
  single concrete "favourites win" bracket so the published scorelines
  answer "if the modal bracket plays out, what does each match look
  like?"
- **Polymarket for market odds.** Most bookmaker APIs are
  anti-scrape; Polymarket's Gamma API is public, JSON, and runs a
  yes/no market per team with only ~2.9% margin (much tighter than the
  typical 5–8% sportsbook overround). De-vigging is a simple sum-
  normalise across the 48 qualifying teams.

## Sources

| Source | Used for | URL |
|---|---|---|
| eloratings.net | Team Elo ratings (snapshot June 2026) | https://eloratings.net/ |
| Wikipedia "2026 FIFA World Cup" | Main article and links to per-group articles | https://en.wikipedia.org/wiki/2026_FIFA_World_Cup |
| Wikipedia per-group articles | Teams, draw slots, FIFA-rank (Nov 2025), 72 group fixtures with venues | https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_A …`_Group_L` |
| Wikipedia knockout stage | 31 R32→FINAL fixtures, source notation, full 495-row third-place lookup | https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage |
| Polymarket Gamma API | Live outright-winner market odds | https://gamma-api.polymarket.com/events?slug=world-cup-winner |

Every external response is snapshotted under `data/raw/` so the rest of
the pipeline runs offline against the frozen inputs.

## Repository layout

```
experiments/world_cup_2026/
  pyproject.toml                         # PEP 621 project + hatchling build
  README.md                              # this file
  notes/
    World Cup 2026 Elo + Poisson Prediction Plan.md   # source-of-truth design doc
  data/
    raw/                                 # frozen external inputs
      eloratings_world.tsv               # all teams + current Elo
      eloratings_teams.tsv               # eloratings.net code -> name(s)
      elo_snapshot_date.txt              # ISO timestamp of the Elo capture
      wikipedia_2026_world_cup.html      # main FIFA WC 2026 article
      wikipedia_2026_world_cup_group_{A..L}.html
      wikipedia_2026_world_cup_knockout_stage.html
      fifa_teams_groups.csv              # parsed from group articles
      fifa_fixtures.csv                  # parsed from group articles
      polymarket_world_cup_winner.json   # live market snapshot
      market_odds_snapshot_date.txt
    processed/                           # canonical inputs to the model
      teams.csv                          # 48 rows
      group_matches.csv                  # 72 rows
      knockout_slots.csv                 # 31 rows
      third_place_lookup.csv             # 495 rows
      market_odds.csv                    # 48 rows, de-vigged Polymarket
  world_cup_2026/                        # installable Python package
    config.py                            # tunables + data paths
    load_data.py                         # csv loaders with shape checks
    poisson_model.py                     # Elo expected score + lambda fit
    group_stage.py                       # per-sim group + FIFA tie-breaks
    qualifiers.py                        # third-place lookup + R32 build
    knockout.py                          # R32 through FINAL sampling
    simulate.py                          # Monte Carlo loop + outputs
    score_predictions.py                 # analytical score-grid helpers
    parse_groups.py                      # build fifa_teams_groups.csv
    parse_fixtures.py                    # build fifa_fixtures.csv
    parse_knockout.py                    # build processed knockout_slots.csv
    parse_results.py                     # group-stage scorelines -> results.csv
    parse_knockout_results.py            # knockout scorelines -> results.csv (wc26-parse-knockout-results)
    build_teams.py                       # join FIFA groups <-> Elo snapshot
    build_group_matches.py               # add slot refs + venue country
    build_third_place_lookup.py          # parse Wikipedia's 495-row table
    run_simulation.py                    # main Monte Carlo runner (wc26-simulate)
    build_score_predictions.py           # group-stage modal scorelines
    build_knockout_score_predictions.py  # knockout modal bracket scorelines
    fetch_market_odds.py                 # refresh Polymarket snapshot
    build_market_odds.py                 # de-vig market snapshot
    build_market_comparison.py           # model vs market join
  outputs/                               # published artefacts
    team_probabilities.csv               # one row per team (48)
    group_probabilities.csv              # per-team group-finish probs
    simulation_summary.csv               # run metadata
    group_score_predictions.csv          # one row per group fixture (72)
    knockout_score_predictions.csv       # one row per knockout fixture (31)
    market_comparison.csv                # model vs market edge
```

## Requirements

- Python 3.13 (pinned in this experiment's `pyproject.toml`).
- `numpy`, `polars`, `scipy`, `tqdm` (the only runtime dependencies).

From `experiments/world_cup_2026/`:

```bash
uv sync
```

`uv` reads the PEP 621 `[project]` section of the local
`pyproject.toml` and provisions a virtual environment under `.venv/`.
All command snippets below assume you are inside this directory and
prefix Python invocations with `uv run` so they pick up the right
interpreter. If you prefer pip, `pip install -e .` against the same
`pyproject.toml` works too.

## Running each component

All commands below are run from `experiments/world_cup_2026/`
(the directory you `cd`'d into for `uv sync`).

### One-time data capture (snapshots already committed)

Re-running these only matters when you want a fresher snapshot. The
committed `data/raw/` files date from 2026-06-08.

#### Elo ratings snapshot (eloratings.net)

```bash
curl -sSL 'https://eloratings.net/World.tsv' \
  -H 'Referer: https://eloratings.net/' \
  -o data/raw/eloratings_world.tsv

curl -sSL 'https://eloratings.net/en.teams.tsv' \
  -H 'Referer: https://eloratings.net/' \
  -o data/raw/eloratings_teams.tsv

date -u +"%Y-%m-%dT%H:%M:%SZ" > data/raw/elo_snapshot_date.txt
```

#### Wikipedia HTML snapshots

```bash
UA='Mozilla/5.0 (compatible; world-cup-2026-research/1.0; you@example.com)'
cd data/raw

curl -sSL -A "$UA" \
  'https://en.wikipedia.org/wiki/2026_FIFA_World_Cup' \
  -o wikipedia_2026_world_cup.html

curl -sSL -A "$UA" \
  'https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage' \
  -o wikipedia_2026_world_cup_knockout_stage.html

for g in A B C D E F G H I J K L; do
  curl -sSL -A "$UA" \
    "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_${g}" \
    -o "wikipedia_2026_world_cup_group_${g}.html"
done

cd -
```

#### Polymarket odds (live, ≈3% vig)

```bash
uv run python -m world_cup_2026.fetch_market_odds
```

### Building the canonical input tables

These are deterministic transforms of `data/raw/` into
`data/processed/`. Re-run after refreshing any snapshot.

```bash
uv run python -m world_cup_2026.parse_groups
uv run python -m world_cup_2026.parse_fixtures
uv run python -m world_cup_2026.parse_knockout
uv run python -m world_cup_2026.build_teams
uv run python -m world_cup_2026.build_group_matches
uv run python -m world_cup_2026.build_third_place_lookup
uv run python -m world_cup_2026.build_market_odds
```

Shape-check invariants are baked into `world_cup_2026/load_data.py` (48 teams,
72 group matches, 31 knockout slots, 495 third-place rows); each builder
also runs row-level sanity checks before writing its CSV.

### Running the simulation

Defaults (`-n 10_000_000`, `--seed 20260611`) come from `world_cup_2026/config.py`.
The loop parallelises across CPU cores (see `-w`); on a 16-core machine it
runs at ≈22,000 tournaments/s, so use a smaller count during development.

```bash
# 10k for a quick debug pass (well under a second)
uv run wc26-simulate -n 10000 --quiet

# 100k for development checks (~5 seconds)
uv run wc26-simulate -n 100000 --quiet

# 10M for the published outputs (~8 minutes on 16 cores)
uv run wc26-simulate
```

(`wc26-simulate` is the console-script entry point declared in
`pyproject.toml`. `uv run python -m world_cup_2026.run_simulation` works
identically.)

Writes to `outputs/`:

- `team_probabilities.csv` — per-team title and round-reaching probabilities, implied decimal odds, Elo rank vs title rank.
- `group_probabilities.csv` — per-team P(finish 1st/2nd/3rd/4th), qualification, elimination.
- `simulation_summary.csv` — run metadata (n, seed, Elo snapshot date, total goals, host advantage, created_at).

The plan's bracket invariants (`sum p_winner = 1`, `sum p_reach_sf = 4`,
…) are exact to six decimal places at 10M sims.

### Score predictions per fixture

These are analytical — no extra Monte Carlo. They read each match's
λ pair off the cache and compute the joint Poisson grid directly.

```bash
uv run python -m world_cup_2026.build_score_predictions
uv run python -m world_cup_2026.build_knockout_score_predictions
```

Outputs:

- `group_score_predictions.csv` — 72 rows. Per fixture: expected goals, W/D/L split, modal scoreline, top-5 scorelines.
- `knockout_score_predictions.csv` — 31 rows along a single "modal bracket" path (favourites advance round-by-round). Includes `p_team_a_advances` with the Elo extra-time tie-break baked in, plus the modal score and top-5 list for 90 minutes.

The simulator's `team_probabilities.csv` remains the source of truth for
marginal probabilities; the knockout score predictions answer "if the
modal bracket plays out, what scoreline is most likely in each match?"

### Market comparison

Refresh the Polymarket snapshot then rebuild:

```bash
uv run python -m world_cup_2026.fetch_market_odds
uv run python -m world_cup_2026.build_market_odds
uv run python -m world_cup_2026.build_market_comparison
```

`outputs/market_comparison.csv` joins model `p_winner` against the
de-vigged Polymarket `p_winner` and reports `value_edge =
model - market`, `value_ratio = model / market`, and a market-rank
vs model-rank diff. Sorted by `value_edge` descending so the article's
"undervalued by the market" picks read top-down.

### Full rebuild from scratch

```bash
# 1. capture data (see commands above) or use the committed snapshots
# 2. build processed inputs
uv run python -m world_cup_2026.parse_groups
uv run python -m world_cup_2026.parse_fixtures
uv run python -m world_cup_2026.parse_knockout
uv run python -m world_cup_2026.build_teams
uv run python -m world_cup_2026.build_group_matches
uv run python -m world_cup_2026.build_third_place_lookup
uv run python -m world_cup_2026.build_market_odds
# 3. simulate
uv run wc26-simulate
# 4. score predictions
uv run python -m world_cup_2026.build_score_predictions
uv run python -m world_cup_2026.build_knockout_score_predictions
# 5. market comparison
uv run python -m world_cup_2026.build_market_comparison
# 6. article charts, bracket heatmap and animation
uv run wc26-build-article-charts
uv run wc26-bracket-heatmap
uv run python -m world_cup_2026.animate_combined
```

### Conditional re-run on results so far

Once the tournament is under way the simulator can re-forecast from where
things actually stand, in a way that never overwrites the frozen
pre-tournament outputs. Two things change relative to the baseline:

1. **Played matches are pinned** to their real scoreline in every
   simulation, so the standings, FIFA tie-breaks and qualification that
   flow from them are conditioned on what has happened.
2. **Elo is refreshed** from a fresh eloratings.net snapshot, so the
   *remaining* matches are priced off current ratings. A played match
   therefore enters twice — locked to its real score here, and folded into
   the updated Elo that prices the teams' future games. That is deliberate.

The conditional scenario lives in parallel files so the baseline stays
reproducible:

| Conditional artefact | Baseline counterpart |
|---|---|
| `data/raw/conditional/eloratings_world.tsv` | `data/raw/eloratings_world.tsv` |
| `data/raw/conditional/wikipedia_2026_world_cup_group_{A..L}.html` | `data/raw/wikipedia_2026_world_cup_group_{A..L}.html` |
| `data/processed/teams_conditional.csv` | `data/processed/teams.csv` |
| `data/processed/results.csv` | — (only exists post-kickoff) |
| `outputs/conditional/` | `outputs/` |

```bash
# 1. refresh the conditional snapshots (fresh Elo + group pages with scores)
mkdir -p data/raw/conditional
curl -sSL 'https://eloratings.net/World.tsv' -H 'Referer: https://eloratings.net/' \
  -o data/raw/conditional/eloratings_world.tsv
date -u +"%Y-%m-%dT%H:%M:%SZ" > data/raw/conditional/elo_snapshot_date.txt

UA='Mozilla/5.0 (compatible; world-cup-2026-research/1.0; you@example.com)'
for g in A B C D E F G H I J K L; do
  curl -sSL -A "$UA" "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_${g}" \
    -o "data/raw/conditional/wikipedia_2026_world_cup_group_${g}.html"
done
date -u +"%Y-%m-%dT%H:%M:%SZ" > data/raw/conditional/results_snapshot_date.txt

# 2. build the conditional inputs
uv run python -m world_cup_2026.build_teams \
  --world-tsv data/raw/conditional/eloratings_world.tsv \
  --output data/processed/teams_conditional.csv
uv run python -m world_cup_2026.parse_results   # -> data/processed/results.csv

# 3. simulate, conditioned on results so far, into outputs/conditional/
uv run wc26-simulate --conditional

# 3b. per-fixture score predictions: played games carry their actual score
#     (played/actual_score columns); the KO modal bracket walks the
#     conditional group_probabilities off refreshed Elo
uv run python -m world_cup_2026.build_score_predictions --conditional
uv run python -m world_cup_2026.build_knockout_score_predictions --conditional

# 4. refresh the market and rebuild the comparison against the new model
uv run python -m world_cup_2026.fetch_market_odds --conditional
uv run python -m world_cup_2026.build_market_odds --conditional
uv run python -m world_cup_2026.build_market_comparison --conditional

# 5. regenerate the article charts into plots/conditional/
uv run wc26-build-article-charts --conditional

# 6. regenerate the knockout bracket heatmap
uv run wc26-bracket-heatmap --conditional

# 7. regenerate the combined bracket + counter animation
uv run python -m world_cup_2026.animate_combined --conditional
```

The same `--conditional` flag runs through the whole chain. Every script
also accepts `--tag TAG` (default: `conditional`) to write into a named
subdirectory instead of the default `outputs/conditional/`. Use this to
preserve earlier snapshots when re-running mid-tournament:

```bash
TAG=conditional_knockout

# 0. fetch fresh inputs into data/raw/$TAG/
mkdir -p data/raw/$TAG
curl -sSL 'https://eloratings.net/World.tsv' -H 'Referer: https://eloratings.net/' \
  -o data/raw/$TAG/eloratings_world.tsv
date -u +"%Y-%m-%dT%H:%M:%SZ" > data/raw/$TAG/elo_snapshot_date.txt
UA='Mozilla/5.0 (compatible; world-cup-2026-research/1.0; you@example.com)'
for g in A B C D E F G H I J K L; do
  curl -sSL -A "$UA" "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_${g}" \
    -o "data/raw/$TAG/wikipedia_2026_world_cup_group_${g}.html"
done
curl -sSL -A "$UA" 'https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_knockout_stage' \
  -o data/raw/$TAG/wikipedia_2026_world_cup_knockout_stage.html
date -u +"%Y-%m-%dT%H:%M:%SZ" > data/raw/$TAG/results_snapshot_date.txt

# 1. rebuild teams from the fresh Elo snapshot
uv run python -m world_cup_2026.build_teams \
  --world-tsv data/raw/$TAG/eloratings_world.tsv \
  --output data/processed/teams_$TAG.csv

# 2. parse group results into results.csv (group rows only)
uv run python -m world_cup_2026.parse_results

# 3. first-pass simulate + build knockout score predictions
#    (needed so parse_knockout_results can map team names to match IDs)
uv run wc26-simulate --conditional --tag $TAG
uv run python -m world_cup_2026.build_score_predictions --conditional --tag $TAG
uv run python -m world_cup_2026.build_knockout_score_predictions --conditional --tag $TAG

# 4. parse played knockout matches — reads outputs/$TAG/knockout_score_predictions.csv
#    to resolve team names, then appends winner rows to results.csv
uv run wc26-parse-knockout-results --tag $TAG

# 5. second-pass simulate + rebuild everything with knockout results pinned
uv run wc26-simulate --conditional --tag $TAG
uv run python -m world_cup_2026.build_score_predictions --conditional --tag $TAG
uv run python -m world_cup_2026.build_knockout_score_predictions --conditional --tag $TAG
uv run python -m world_cup_2026.fetch_market_odds --conditional --tag $TAG
uv run python -m world_cup_2026.build_market_odds --conditional --tag $TAG
uv run python -m world_cup_2026.build_market_comparison --conditional --tag $TAG
uv run wc26-build-article-charts --conditional --tag $TAG
uv run wc26-bracket-heatmap --conditional --tag $TAG
uv run python -m world_cup_2026.animate_combined --conditional --tag $TAG
```

Tags use underscores, not hyphens (e.g. `conditional_knockout`, not `conditional-knockout`).
Each tag gets its own raw-data directory (`data/raw/{tag}/`) alongside the output and plot
directories, so the exact inputs used for each snapshot are preserved independently:

| Tag | Scope |
|---|---|
| `conditional` | Post-group-stage: all 72 group matches pinned, Elo refreshed after the group phase |
| `conditional_knockout` | Post-R32: group results plus each played knockout match pinned as the round progresses |

The chain keeps a parallel set of files so the frozen baseline stays reproducible:
`data/raw/conditional/polymarket_world_cup_winner.json`,
`data/processed/market_odds_conditional.csv`,
`outputs/conditional/market_comparison.csv` and `plots/conditional/`.

`parse_results.py` reads the score out of each footballbox's
`<th class="fscore">` (a played match shows e.g. `2–1`, an unplayed one
still shows `Match N`) and maps home/away to the canonical `match_id` via
`group_matches.csv`. `simulation_summary.csv` in the conditional output
records `results_snapshot_date` and `n_results_fixed` so the run is
self-describing.

`results.csv` schema is `match_id, home_goals, away_goals, winner`:

- **Group rows** (`match_id` 1-72) pin the scoreline; `winner` is left
  empty. These are written automatically by `parse_results.py`.
- **Knockout rows** (`match_id` >= 73; 73-88 R32, 89-96 R16, 97-100 QF,
  101-102 SF, 104 final) pin *which team advances* via `winner` (a
  `team_id`). The goals are the regulation/extra-time score and are kept
  for the record, but the simulator only reads `winner`, so a penalty
  shootout is captured correctly (e.g. `1-1` with the shootout winner in
  `winner`). These rows are written by `wc26-parse-knockout-results`
  (see above), which reads the Wikipedia knockout-stage HTML and appends
  any played matches not yet in the file. A rerun of `parse_results.py`
  or `wc26-parse-knockout-results` never overwrites already-recorded rows.

Pin knockout results **cumulatively** — every played knockout match up to
the current point. Once the group stage is complete the bracket is
deterministic across simulations, so each pinned winner is always a real
participant; in the simulator a pin whose team isn't in that match (an
out-of-order or stale entry) is ignored rather than forced.

The knockout score-prediction builder also follows reality in
`--conditional` mode: once the whole group stage is in `results.csv` it
resolves the R32 fixtures from the *actual* final standings (reusing the
simulator's group + qualifier code) and propagates each played knockout
match's *actual* winner, reverting to the modal Elo favourite beyond the
played front. Its conditional output gains `bracket_basis`
(`actual`/`modal`), `played`, `actual_score` and `actual_winner` columns,
with the model's `predicted_winner` reported alongside. A pinned knockout
winner that isn't one of its bracket participants raises an error here
(rather than being silently ignored), since this is a single concrete
bracket and a stale entry would otherwise corrupt later rounds.

### Blow-out rate analysis

`blowout_analysis.py` reproduces the historical group-stage blow-out
table published in the article. It reads the
[martj42 international-results dataset](https://github.com/martj42/international_results)
(not bundled here) and the project's own `data/processed/results.csv`:

```bash
uv run wc26-blowout-analysis --results path/to/martj42/results.csv
```

A "blow-out" is any match won by three or more goals. The script prints
the rate for each 32-team World Cup (1998–2022, 48 group matches each)
plus the 2026 figure derived from `results.csv`.

## Configuration

`world_cup_2026/config.py` exposes:

| Constant | Default | Meaning |
|---|---|---|
| `N_SIMULATIONS` | `10_000_000` | Number of Monte Carlo tournaments |
| `SEED` | `20260611` | RNG seed (tournament start date) |
| `TOTAL_GOALS` | `2.6` | Goal budget per match |
| `HOST_ADVANTAGE` | `100` | Elo bonus when a host plays at home |
| `MAX_GOALS` | `10` | Poisson grid truncation |
| `MIN_LAMBDA` | `0.25` | Underdog floor on λ for lopsided matches |
| `ELO_DIFFERENCE_CACHE_ROUNDING` | `1` | Bucket size for the lambda cache |

## Intentional limitations

These are excluded from v1 by design (see plan §1.2 / §16):

- No custom Elo recalculation — eloratings.net is used as-is.
- No squad / injury / player-level modelling.
- No bookmaker-odds integration as a model input (only for comparison).
- No backtesting on 2014 / 2018 / 2022 tournaments.
- No card/conduct score in tie-breaks (FIFA-rank fallback only).
- No detailed extra-time goal model (Elo coin-flip on ties).
- No Elo updates inside a simulated tournament.
- Third-place play-off (Match 103) is not modelled — it does not affect
  title probabilities and the plan's stage labels stop at FINAL/WINNER.
