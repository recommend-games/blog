"""Configuration constants and data paths for the World Cup 2026 simulator."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

TEAMS_CSV = DATA_PROCESSED / "teams.csv"
GROUP_MATCHES_CSV = DATA_PROCESSED / "group_matches.csv"
KNOCKOUT_SLOTS_CSV = DATA_PROCESSED / "knockout_slots.csv"
THIRD_PLACE_LOOKUP_CSV = DATA_PROCESSED / "third_place_lookup.csv"

# Conditional ("results so far") scenario. Refreshed Elo and the played
# scorelines live alongside the frozen pre-tournament snapshot so the
# original published outputs stay reproducible. The conditional run reads
# teams_conditional.csv + results.csv and writes into outputs/conditional/.
DATA_RAW_CONDITIONAL = DATA_RAW / "conditional"
TEAMS_CONDITIONAL_CSV = DATA_PROCESSED / "teams_conditional.csv"
RESULTS_CSV = DATA_PROCESSED / "results.csv"
OUTPUTS_CONDITIONAL = OUTPUTS / "conditional"

# Polymarket snapshot + de-vigged odds, baseline and conditional.
POLYMARKET_SNAPSHOT = DATA_RAW / "polymarket_world_cup_winner.json"
POLYMARKET_SNAPSHOT_CONDITIONAL = (
    DATA_RAW_CONDITIONAL / "polymarket_world_cup_winner.json"
)
MARKET_ODDS_SNAPSHOT_DATE = DATA_RAW / "market_odds_snapshot_date.txt"
MARKET_ODDS_SNAPSHOT_DATE_CONDITIONAL = (
    DATA_RAW_CONDITIONAL / "market_odds_snapshot_date.txt"
)
MARKET_ODDS_CSV = DATA_PROCESSED / "market_odds.csv"
MARKET_ODDS_CONDITIONAL_CSV = DATA_PROCESSED / "market_odds_conditional.csv"

PLOTS = ROOT / "plots"
PLOTS_CONDITIONAL = PLOTS / "conditional"


def conditional_paths(tag: str = "conditional") -> SimpleNamespace:
    """Return all file paths for a tagged conditional run.

    The tag replaces 'conditional' in every output path so multiple
    mid-tournament snapshots can coexist without overwriting each other.
    The default tag 'conditional' reproduces the existing layout exactly.

    Fields:
        data_raw           data/raw/{tag}/
        polymarket_snapshot  data/raw/{tag}/polymarket_world_cup_winner.json
        market_odds_snapshot_date  data/raw/{tag}/market_odds_snapshot_date.txt
        teams_csv          data/processed/teams_{tag}.csv
        market_odds_csv    data/processed/market_odds_{tag}.csv
        outputs            outputs/{tag}/
        plots              plots/{tag}/
    """
    raw = DATA_RAW / tag
    return SimpleNamespace(
        data_raw=raw,
        polymarket_snapshot=raw / "polymarket_world_cup_winner.json",
        market_odds_snapshot_date=raw / "market_odds_snapshot_date.txt",
        teams_csv=DATA_PROCESSED / f"teams_{tag}.csv",
        market_odds_csv=DATA_PROCESSED / f"market_odds_{tag}.csv",
        outputs=OUTPUTS / tag,
        plots=PLOTS / tag,
    )

N_SIMULATIONS = 10_000_000
SEED = 20260611
TOTAL_GOALS = 2.6
HOST_ADVANTAGE = 100
MAX_GOALS = 10
ELO_DIFFERENCE_CACHE_ROUNDING = 1

# Floor on the underdog's Poisson lambda. When the Elo gap is so large that
# the requested expected score exceeds what the (lambda_a + lambda_b =
# total_goals) regime can produce, we pin the weaker team at MIN_LAMBDA and
# let the dominant team's lambda rise above total_goals - MIN_LAMBDA. This
# keeps a small but realistic upset chance in lopsided matches.
MIN_LAMBDA = 0.25
