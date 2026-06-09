This document describes a deliberately simple implementation plan for predicting the winner of the 2026 FIFA World Cup using established Elo ratings and a Poisson goal model.

The goal is to build a reproducible Monte Carlo simulator quickly, not to build a fully optimised football forecasting system.

**Status as of 2026-06-08:** The tournament opens on 2026-06-11. Data must be captured and the simulation must be runnable before the first group matches kick off.

## 1. Scope

### Main idea

Use this pipeline:

```text
Established World Football Elo ratings
    -> Elo-based expected result
    -> Poisson scoreline model
    -> group-stage simulation
    -> official knockout-path simulation
    -> title and round-reaching probabilities
```

### Included

- Use established public Elo ratings.
- Use a simple Poisson model for football scores.
- Simulate all group-stage matches as scorelines.
- Apply group ranking and best-third qualification rules.
- Simulate the round of 32 through the final.
- Run many Monte Carlo simulations.
- Produce CSV outputs and simple analysis tables.

### Excluded

- No custom Elo implementation.
- No player-level or squad-strength modelling.
- No injury modelling.
- No bookmaker odds integration for the first version.
- No backtesting for the first version.
- No card/conduct simulation.
- No detailed extra-time goal model.
- No Elo updates inside simulated tournaments.

## 2. Sources of truth

Use these sources or local snapshots derived from them:

1. World Football Elo Ratings
   - Main team-strength input.
   - Source: https://www.eloratings.net/
   - Mirror/snapshot-friendly table: https://www.international-football.net/elo-ratings-table

2. FIFA World Cup 2026 regulations
   - Source of tournament structure, group ranking, knockout rules, and third-place mapping.
   - Source: https://digitalhub.fifa.com/

3. FIFA World Cup 2026 official fixtures and groups
   - Source of groups, fixtures, venue countries, and knockout slots.
   - Source: https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026

**Important:** save local copies of all scraped or manually entered data. The simulation must not depend on live web access at runtime.

**Immediate action before 2026-06-11:** capture the Elo ratings snapshot and all fixture/group data now, while teams are still in their pre-tournament state. Rating any group-stage result back into the snapshot would invalidate the pre-tournament forecast.

## 3. Repository structure

This lives in the `world-cup-2026` branch of the existing `elo` repository, under a `world_cup_2026/` subdirectory at the repo root.

```text
world_cup_2026/
  data/
    raw/
      elo_snapshot.csv
      elo_snapshot_date.txt
      fifa_teams_groups.csv
      fifa_fixtures.csv
      third_place_lookup.csv
    processed/
      teams.csv
      group_matches.csv
      knockout_slots.csv
  src/
    __init__.py
    config.py
    load_data.py
    poisson_model.py
    group_stage.py
    knockout.py
    simulate.py
    analyse.py
  outputs/
    team_probabilities.csv
    group_probabilities.csv
    simulation_summary.csv
  scripts/
    run_simulation.py
    make_tables.py
  tests/
    test_poisson_model.py
    test_group_stage.py
    test_third_place_lookup.py
    test_knockout.py
```

Python 3.13 (as required by `pyproject.toml`). Use NumPy for all simulation sampling. Use Polars for loading, transforming, and outputting tabular data. Do not use Polars inside the hot simulation loop.

## 4. Input data files

### 4.1 `teams.csv`

One row per team.

Required columns:

```text
team_id              stable internal identifier, e.g. ARG, ESP, USA
team_name            display name
elo_name             name in the Elo source, if different
group                group letter, A-L
group_slot           group slot, e.g. A1, A2, ..., L4
elo                  Elo rating snapshot value
fifa_ranking         FIFA ranking, only used as rare tie-break fallback
is_host              boolean: true for Canada, Mexico, USA
host_country         Canada, Mexico, USA, or empty
```

Example:

```csv
team_id,team_name,elo_name,group,group_slot,elo,fifa_ranking,is_host,host_country
ARG,Argentina,Argentina,J,J1,2140,1,false,
USA,United States,United States,D,D1,1830,16,true,USA
```

The exact teams, groups, slots, ratings, and rankings must be filled from the frozen data snapshot. Watch for name mismatches between the FIFA fixtures and the Elo source (e.g. "United States" vs "USA"); resolve via the `elo_name` column.

### 4.2 `group_matches.csv`

One row per group-stage fixture.

Required columns:

```text
match_id
stage                 group
round_number          1, 2, or 3 within the group stage
group                 A-L
team_a_slot           e.g. A1
team_b_slot           e.g. A2
venue_country         Canada, Mexico, or USA
```

There are 6 matches per group × 12 groups = 72 group-stage fixtures in total.

### 4.3 `knockout_slots.csv`

One row per fixed knockout fixture slot. There are 16 R32 matches, 8 R16 matches, 4 QF, 2 SF, and 1 final = 31 knockout matches.

Required columns:

```text
match_id
stage                 R32, R16, QF, SF, FINAL
team_a_source         e.g. 1A, 2C, 3DEF, W49
team_b_source         e.g. 2B, 1F, W50
venue_country
winner_to             match_id of the next match, empty for FINAL
```

Source notation:

- `1A` = group winner of group A.
- `2C` = group runner-up of group C.
- `3DEF` = the third-placed team from groups D, E, or F that qualified (resolved via the third-place lookup).
- `W49` = winner of match 49.

The `team_a_source` / `team_b_source` values for third-placed teams use a notation like `3XYZ` that identifies the pool of groups a qualifying third-placed team can come from. The exact pool labels are fixed by the FIFA bracket and must be copied from the official regulations.

### 4.4 `third_place_lookup.csv`

This table maps each combination of eight qualified third-placed groups to the specific group letter assigned to each third-place slot in the R32.

Required columns:

```text
qualified_third_groups       sorted 8-character string, e.g. ABCDEFGH
<match_id_1>                 group letter of the third-placed team filling that slot, e.g. A
<match_id_2>
...
<match_id_8>
```

The column names for the slot columns are the `match_id` values of the 8 R32 fixtures that have a third-placed team source. Each value is a single group letter (A–L). To reconstruct the source team, look up the third-placed team of that group from the group-stage results.

Acceptance criterion:

```text
number of rows == 495
```

There are C(12, 8) = 495 possible combinations of qualified third-placed teams.

**Implementation note:** this table is the most complex piece of input data. Derive it entirely from the official FIFA 2026 bracket regulations, not by inference. The exact mapping is published by FIFA before the tournament and must be entered manually or verified line by line.

## 5. Match model

### 5.1 Elo difference

For each match between team A and team B:

```text
d = elo_A - elo_B + host_adjustment_A - host_adjustment_B
```

Use this simple host adjustment:

```text
host_adjustment = 100 if the team is one of the hosts and the match is played in that team's own country
host_adjustment = 0 otherwise
```

Examples:

- USA playing in the USA: +100 for USA.
- Mexico playing in Mexico: +100 for Mexico.
- Canada playing in Canada: +100 for Canada.
- USA playing in Mexico: no host adjustment in the first version.
- Argentina vs Spain in the USA: no host adjustment.

For knockout matches, `venue_country` in `knockout_slots.csv` must be respected when computing the host adjustment.

### 5.2 Elo expected score

Convert Elo difference to expected score:

```text
s_A = 1 / (1 + 10 ** (-d / 400))
s_B = 1 - s_A
```

Interpretation:

```text
s_A = P(A wins) + 0.5 * P(draw)
```

This is not the same as pure win probability.

### 5.3 Poisson goal model

Use a fixed expected total number of goals:

```text
total_goals = 2.6
```

For each match, find `lambda_A` and `lambda_B` such that:

```text
lambda_A + lambda_B = total_goals
PoissonExpectedScore(lambda_A, lambda_B) ≈ s_A
```

where:

```text
PoissonExpectedScore(lambda_A, lambda_B)
    = P(goals_A > goals_B) + 0.5 * P(goals_A == goals_B)
```

Compute this efficiently using a (max_goals+1) × (max_goals+1) score matrix:

```python
import numpy as np

def poisson_expected_score(lambda_a, lambda_b, max_goals=10):
    g = np.arange(max_goals + 1)
    p_a = np.exp(-lambda_a) * lambda_a**g / np.array([np.math.factorial(i) for i in g])
    p_b = np.exp(-lambda_b) * lambda_b**g / np.array([np.math.factorial(i) for i in g])
    # Equivalently: from scipy.stats import poisson; p_a = poisson.pmf(g, lambda_a)
    m = np.outer(p_a, p_b)           # m[i,j] = P(A scores i, B scores j)
    p_win = np.tril(m, k=-1).sum()   # rows > cols means A scores more
    p_draw = np.trace(m)
    return p_win + 0.5 * p_draw
```

Solve for `lambda_A` using `scipy.optimize.brentq` rather than a manual binary search:

```python
from scipy.optimize import brentq

def fit_lambdas(s_a, total_goals, max_goals=10):
    def objective(lam_a):
        return poisson_expected_score(lam_a, total_goals - lam_a, max_goals) - s_a
    lam_a = brentq(objective, 1e-9, total_goals - 1e-9)
    return lam_a, total_goals - lam_a
```

Recommended truncation:

```text
max_goals = 10
```

Probability mass above 10 goals is negligible for realistic Poisson rates.

### 5.4 Caching and precomputation

Cache lambdas by rounded Elo difference:

```python
rounded_d = round(d)   # integer, matches elo_difference_cache_rounding = 1
```

With Elo differences in the plausible range ±600, the cache holds at most ~1200 entries. A plain dict is sufficient; no LRU eviction is needed.

**Precompute the full cache before the simulation loop.** Collect all unique rounded Elo differences from all group-stage and knockout fixtures, compute lambdas for each, and store in the dict. This ensures `fit_lambdas` is never called inside the hot loop.

## 6. Group-stage simulation

For each group match:

1. Look up `lambda_A`, `lambda_B` from the precomputed cache.
2. Sample goals:

```text
goals_A ~ Poisson(lambda_A)
goals_B ~ Poisson(lambda_B)
```

3. Award points:

```text
win  -> 3 points
draw -> 1 point each
loss -> 0 points
```

Track per team:

```text
points
goals_for
goals_against
goal_difference
head-to-head results against each group opponent
```

## 7. Group ranking rules

Implement these tie-breaks in this order:

1. Points.
2. Head-to-head points among tied teams.
3. Head-to-head goal difference among tied teams.
4. Head-to-head goals scored among tied teams.
5. Overall goal difference.
6. Overall goals scored.
7. FIFA ranking fallback (deterministic, no randomness).

The official regulations include team conduct score before the FIFA-ranking fallback. Do not simulate cards. Go directly to FIFA ranking as the final deterministic fallback.

**Implementation note:**

- Ties can involve two, three, or four teams.
- Apply the head-to-head criteria only to the tied subset.
- If a criterion separates some but not all tied teams, resolve the separated positions and apply the next criterion recursively to the remaining tied subset.
- For the first version, a stable sort over all criteria applied to the tied subset is acceptable, as long as tests cover two-team and three-team tied cases explicitly.

## 8. Selecting teams for the knockout stage

From each group:

```text
rank 1 -> qualifies directly
rank 2 -> qualifies directly
rank 3 -> candidate for best-third qualification
rank 4 -> eliminated
```

Rank the twelve third-placed teams by:

1. Points.
2. Overall goal difference.
3. Overall goals scored.
4. FIFA ranking fallback.

Select the top eight. Then use `third_place_lookup.csv` to assign each qualifying third-placed team to the correct R32 slot. The lookup key is the sorted 8-letter string of the qualifying groups (e.g. `ABCDFGIJ`).

## 9. Knockout simulation

Use the same Poisson model for 90 minutes.

For each knockout match:

1. Look up `lambda_A`, `lambda_B` from the precomputed cache (using the match's `venue_country` for host adjustment).
2. Sample 90-minute goals.
3. If one team has more goals, that team advances.
4. If the score is tied, decide the advancing team by drawing from the Elo expected score:

```text
P(A advances after extra time / penalties) = s_A
P(B advances after extra time / penalties) = s_B
```

This intentionally avoids detailed extra-time and penalty modelling.

Track each team's furthest stage reached.

Recommended stage labels:

```text
GROUP_ELIMINATED
R32
R16
QF
SF
FINAL
WINNER
```

Interpretation:

- `R32` means the team reached the round of 32 but was eliminated there.
- `R16` means eliminated in the round of 16.
- `QF` means eliminated in the quarter-finals.
- `SF` means eliminated in the semi-finals.
- `FINAL` means lost the final.
- `WINNER` means won the tournament.

## 10. Monte Carlo loop

### Structure

```python
rng = np.random.default_rng(seed)

for sim_idx in range(n_simulations):
    group_results = simulate_group_stage(
        teams=teams,
        group_matches=group_matches,
        lambda_cache=lambda_cache,
        rng=rng,
    )

    group_rankings = rank_all_groups(group_results)

    qualifiers = select_qualifiers(
        group_rankings=group_rankings,
        third_place_lookup=third_place_lookup,
    )

    bracket = build_round_of_32(
        qualifiers=qualifiers,
        knockout_slots=knockout_slots,
    )

    tournament_result = simulate_knockout_stage(
        bracket=bracket,
        lambda_cache=lambda_cache,
        rng=rng,
    )

    accumulator.update(group_rankings, tournament_result)
```

Always use `numpy.random.default_rng(seed)` for the RNG. Do not use the legacy `numpy.random` global interface.

### Vectorised goal sampling

The most expensive operation is Poisson sampling. Amortise it by sampling all goals for all group matches across all simulations in a single call before the simulation loop:

```python
# lambdas_a and lambdas_b: arrays of shape (n_group_matches,)
# Broadcast to shape (n_simulations, n_group_matches)
all_goals_a = rng.poisson(lambdas_a, size=(n_simulations, n_group_matches))
all_goals_b = rng.poisson(lambdas_b, size=(n_simulations, n_group_matches))
```

Then pass `all_goals_a[sim_idx]` and `all_goals_b[sim_idx]` into the per-simulation ranking logic. This avoids repeated Python-level Poisson draws and is the dominant performance gain.

The same pattern applies to knockout matches, though the bracket is not fixed in advance (it depends on group results), so knockout sampling must remain inside the loop.

### Simulation counts and performance

```text
10,000     for first debugging (seconds)
100,000    for development checks (tens of seconds)
1,000,000  for final article outputs (minutes)
```

With vectorised group-stage sampling, 1M simulations should complete in under five minutes on a modern laptop. The bottleneck is the per-simulation Python ranking loop, not the Poisson sampling. If runtime exceeds ten minutes, consider reducing to 100k simulations — the probability estimates stabilise well below that.

Use a fixed random seed for reproducibility:

```text
seed = 20260611
```

## 11. Outputs

### 11.1 `team_probabilities.csv`

One row per team.

Columns:

```text
team_id
team_name
group
elo
fifa_ranking
p_group_winner
p_qualify_group
p_reach_r32
p_reach_r16
p_reach_qf
p_reach_sf
p_reach_final
p_winner
implied_decimal_odds
elo_rank
title_probability_rank
rank_difference
```

Notes:

- `p_reach_r32` is the probability of qualifying from the group stage and therefore equals `p_qualify_group` by definition.
- `implied_decimal_odds = 1 / p_winner`. If `p_winner == 0` (no wins in n simulations), set to `NaN` rather than dividing by zero.
- `rank_difference = elo_rank - title_probability_rank`. Positive means the team's title probability rank is better than its Elo rank (the draw helped them). Negative means the draw/path hurt them.

### 11.2 `group_probabilities.csv`

One row per team.

Columns:

```text
group
team_id
team_name
p_finish_1st
p_finish_2nd
p_finish_3rd
p_finish_4th
p_qualify
p_eliminated
```

### 11.3 `simulation_summary.csv`

Useful metadata:

```text
n_simulations
seed
elo_snapshot_date
total_goals
host_advantage
created_at
```

## 12. Suggested tables for the article

### Main title-probability table

```text
Team | Elo | Group | R32 | R16 | QF | SF | Final | Winner | Implied odds
```

Sort by `p_winner` descending.

### Group-by-group table

```text
Group | Team | 1st | 2nd | 3rd | Qualify | Eliminated
```

Sort by group, then by qualification probability descending within each group.

### Draw benefit / path difficulty table

```text
Team | Elo rank | Title-probability rank | Difference
```

This is the most interesting narrative angle: which teams are helped or hurt by their draw.

## 13. Tests and acceptance criteria

### Data tests

- Exactly 48 teams.
- Exactly 12 groups.
- Exactly 4 teams per group.
- Every team has an Elo rating.
- Every team has a FIFA ranking fallback.
- Every group-stage fixture references valid group slots.
- Third-place lookup has exactly 495 rows.
- Every third-place lookup key contains exactly 8 distinct group letters from A–L.
- Every knockout slot source is either a valid group-placement reference, a valid third-place slot reference, or a `W<match_id>` reference to an earlier knockout match.

### Poisson model tests

- For equal Elo ratings and no host advantage, `s_A` is approximately 0.5.
- For equal Elo ratings, `lambda_A ≈ lambda_B ≈ total_goals / 2`.
- `lambda_A + lambda_B == total_goals` within floating-point tolerance.
- Larger Elo difference produces larger `lambda_A` and smaller `lambda_B`.
- `poisson_expected_score(lambda_A, lambda_B)` recovers `s_A` to within 1e-5.

### Group-stage tests

Create small synthetic groups with known results and verify:

- Points are calculated correctly.
- Goal difference is calculated correctly.
- Goals scored are calculated correctly.
- Two-team head-to-head tie-break works.
- Three-team tied mini-table works.
- FIFA-ranking fallback is deterministic and consistent across runs.

### Qualification tests

- Top two from every group qualify.
- Exactly eight third-placed teams qualify.
- Exactly 32 teams enter the round of 32.
- The selected third-placed teams are placed in the correct R32 slots according to the lookup table.

### Knockout tests

- Every knockout match produces exactly one winner.
- Exactly one tournament winner per simulation.
- No eliminated team reappears in a later round.
- Stage-reaching counts are internally consistent.

### Simulation output tests

For a run of at least 100,000 simulations:

- Sum of `p_winner` over all teams ≈ 1 (within 0.001).
- Sum of `p_reach_final` over all teams ≈ 2.
- Sum of `p_reach_sf` over all teams ≈ 4.
- Sum of `p_reach_qf` over all teams ≈ 8.
- Sum of `p_reach_r16` over all teams ≈ 16.
- Sum of `p_reach_r32` over all teams ≈ 32.

### Performance test

- 10,000 simulations complete in under 30 seconds.

## 14. Implementation priorities

Build in this order:

0. Capture data snapshot (Elo ratings, groups, fixtures, third-place lookup) and save raw files. Do this before 2026-06-11.
1. Load and validate static data.
2. Implement Elo expected score.
3. Implement Poisson lambda fitting and precompute the lambda cache.
4. Implement group-stage simulation (goal sampling + point tracking).
5. Implement group ranking with tie-breaks.
6. Implement best-third selection.
7. Implement third-place bracket mapping from the lookup table.
8. Implement knockout simulation.
9. Implement accumulator for probabilities.
10. Add vectorised group-stage goal sampling.
11. Export CSV outputs.
12. Add article-ready tables.
13. Add tests around all tournament-structure edge cases.

## 15. Configuration defaults

Expose these in `src/config.py`:

```python
N_SIMULATIONS = 1_000_000
SEED = 20260611
TOTAL_GOALS = 2.6
HOST_ADVANTAGE = 100
MAX_GOALS = 10
ELO_DIFFERENCE_CACHE_ROUNDING = 1
```

The RNG must be constructed as:

```python
import numpy as np
rng = np.random.default_rng(SEED)
```

Do not use the legacy `np.random.seed()` interface.

## 16. Possible later extensions

Do not implement these for the first version, but keep the code flexible enough that they can be added later:

- Calibrate `total_goals` from recent international matches.
- Calibrate host advantage from historical tournament data.
- Use different goal expectations for knockout and group-stage matches.
- Model extra time and penalties separately.
- Add bookmaker odds comparison and de-vigging.
- Add a simple custom Elo model as a robustness check.
- Add sensitivity analysis for `total_goals` and `host_advantage`.
- Backtest on the 2014, 2018, and 2022 World Cups.
- Update the simulation with real group-stage results as the tournament progresses.

## 17. Summary for implementation agent

Implement a deterministic, reproducible World Cup simulator using established Elo ratings and a simple Poisson score model.

The most important correctness risks are:

1. Team/name mapping between FIFA data and Elo data — resolve via the `elo_name` column in `teams.csv`.
2. Group tie-break logic — especially three-team and four-team tied subsets.
3. Best-third qualification — sorting 12 teams by points/GD/GF, selecting 8.
4. Third-place round-of-32 mapping — must be derived from official FIFA regulations, not inferred.
5. Correct bracket progression — `winner_to` links in `knockout_slots.csv` must form a consistent binary tree.

Do not over-engineer the predictive model. The first version should be clear, testable, and article-ready before the tournament begins on 2026-06-11.
