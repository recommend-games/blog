# World Cup 2026 Elo + Poisson predictor

A reproducible Monte Carlo simulator for the 2026 FIFA World Cup, built
around established World Football Elo ratings and a fixed-total Poisson
goal model. The aim is a clear, testable, article-ready first version
rather than an optimised forecasting system. The full design lives in
[`../notes/World Cup 2026 Elo + Poisson Prediction Plan.md`](../notes/World%20Cup%202026%20Elo%20+%20Poisson%20Prediction%20Plan.md).

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
matches; the Monte Carlo loop runs this end-to-end one million times
with a fixed seed (`20260611`) so the published outputs are exactly
reproducible.

## Reasoning behind the choices

- **Elo as the team-strength input.** Public ratings from
  eloratings.net already integrate decades of match data, are updated
  daily, and let the simulator avoid a custom rating model. Pre-tournament
  Elo is frozen on snapshot day so a result inside the tournament never
  feeds back into the forecast.
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
  Python work is just ranking + bracket propagation. 1M tournaments run
  in ≈4 minutes on a laptop.
- **FIFA tie-break ladder, simplified.** Plan §7's full recursive
  resolution is replaced with a composite sort key (H2H points / GD / GF
  on the tied subset, then overall GD / GF, then November-2025 FIFA
  rank). Card/conduct score is intentionally not modelled.
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
world_cup_2026/
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
  src/
    config.py                            # tunables + data paths
    load_data.py                         # csv loaders with shape checks
    poisson_model.py                     # Elo expected score + lambda fit
    group_stage.py                       # per-sim group + FIFA tie-breaks
    qualifiers.py                        # third-place lookup + R32 build
    knockout.py                          # R32 through FINAL sampling
    simulate.py                          # Monte Carlo loop + outputs
    score_predictions.py                 # analytical score-grid helpers
  scripts/
    parse_groups.py                      # build fifa_teams_groups.csv
    parse_fixtures.py                    # build fifa_fixtures.csv
    parse_knockout.py                    # build processed knockout_slots.csv
    build_teams.py                       # join FIFA groups <-> Elo snapshot
    build_group_matches.py               # add slot refs + venue country
    build_third_place_lookup.py          # parse Wikipedia's 495-row table
    run_simulation.py                    # main Monte Carlo runner
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

- Python 3.13 (matches the repo's top-level `pyproject.toml`).
- The project's `uv` environment, with `numpy`, `scipy`, `polars`,
  `tqdm`. From the repo root, `uv sync` once installs them. All later
  commands assume `uv run` so they pick up the right venv.

## Running each component

All commands below are run from the repository root (`elo/`).

### One-time data capture (snapshots already committed)

Re-running these only matters when you want a fresher snapshot. The
committed `data/raw/` files date from 2026-06-08.

#### Elo ratings snapshot (eloratings.net)

```bash
curl -sSL 'https://eloratings.net/World.tsv' \
  -H 'Referer: https://eloratings.net/' \
  -o world_cup_2026/data/raw/eloratings_world.tsv

curl -sSL 'https://eloratings.net/en.teams.tsv' \
  -H 'Referer: https://eloratings.net/' \
  -o world_cup_2026/data/raw/eloratings_teams.tsv

date -u +"%Y-%m-%dT%H:%M:%SZ" > world_cup_2026/data/raw/elo_snapshot_date.txt
```

#### Wikipedia HTML snapshots

```bash
UA='Mozilla/5.0 (compatible; world-cup-2026-research/1.0; you@example.com)'
cd world_cup_2026/data/raw

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
uv run python world_cup_2026/scripts/fetch_market_odds.py
```

### Building the canonical input tables

These are deterministic transforms of `data/raw/` into
`data/processed/`. Re-run after refreshing any snapshot.

```bash
uv run python world_cup_2026/scripts/parse_groups.py
uv run python world_cup_2026/scripts/parse_fixtures.py
uv run python world_cup_2026/scripts/parse_knockout.py
uv run python world_cup_2026/scripts/build_teams.py
uv run python world_cup_2026/scripts/build_group_matches.py
uv run python world_cup_2026/scripts/build_third_place_lookup.py
uv run python world_cup_2026/scripts/build_market_odds.py
```

Shape-check invariants are baked into `src/load_data.py` (48 teams,
72 group matches, 31 knockout slots, 495 third-place rows); each builder
also runs row-level sanity checks before writing its CSV.

### Running the simulation

Defaults (`-n 1_000_000`, `--seed 20260611`) come from `src/config.py`.
Use a smaller count during development; the simulator runs at ≈4,000
sim/s on a modern laptop.

```bash
# 10k for a quick debug pass
uv run python world_cup_2026/scripts/run_simulation.py -n 10000 --quiet

# 100k for development checks (~30 seconds)
uv run python world_cup_2026/scripts/run_simulation.py -n 100000 --quiet

# 1M for the published outputs (~4 minutes)
uv run python world_cup_2026/scripts/run_simulation.py
```

Writes to `outputs/`:

- `team_probabilities.csv` — per-team title and round-reaching probabilities, implied decimal odds, Elo rank vs title rank.
- `group_probabilities.csv` — per-team P(finish 1st/2nd/3rd/4th), qualification, elimination.
- `simulation_summary.csv` — run metadata (n, seed, Elo snapshot date, total goals, host advantage, created_at).

The plan's bracket invariants (`sum p_winner = 1`, `sum p_reach_sf = 4`,
…) are exact to six decimal places at 1M sims.

### Score predictions per fixture

These are analytical — no extra Monte Carlo. They read each match's
λ pair off the cache and compute the joint Poisson grid directly.

```bash
uv run python world_cup_2026/scripts/build_score_predictions.py
uv run python world_cup_2026/scripts/build_knockout_score_predictions.py
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
uv run python world_cup_2026/scripts/fetch_market_odds.py
uv run python world_cup_2026/scripts/build_market_odds.py
uv run python world_cup_2026/scripts/build_market_comparison.py
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
uv run python world_cup_2026/scripts/parse_groups.py
uv run python world_cup_2026/scripts/parse_fixtures.py
uv run python world_cup_2026/scripts/parse_knockout.py
uv run python world_cup_2026/scripts/build_teams.py
uv run python world_cup_2026/scripts/build_group_matches.py
uv run python world_cup_2026/scripts/build_third_place_lookup.py
uv run python world_cup_2026/scripts/build_market_odds.py
# 3. simulate
uv run python world_cup_2026/scripts/run_simulation.py
# 4. score predictions
uv run python world_cup_2026/scripts/build_score_predictions.py
uv run python world_cup_2026/scripts/build_knockout_score_predictions.py
# 5. market comparison
uv run python world_cup_2026/scripts/build_market_comparison.py
```

## Configuration

`src/config.py` exposes:

| Constant | Default | Meaning |
|---|---|---|
| `N_SIMULATIONS` | `1_000_000` | Number of Monte Carlo tournaments |
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
