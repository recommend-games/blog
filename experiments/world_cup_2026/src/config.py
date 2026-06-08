"""Configuration constants and data paths for the World Cup 2026 simulator."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

TEAMS_CSV = DATA_PROCESSED / "teams.csv"
GROUP_MATCHES_CSV = DATA_PROCESSED / "group_matches.csv"
KNOCKOUT_SLOTS_CSV = DATA_PROCESSED / "knockout_slots.csv"
THIRD_PLACE_LOOKUP_CSV = DATA_PROCESSED / "third_place_lookup.csv"

N_SIMULATIONS = 1_000_000
SEED = 20260611
TOTAL_GOALS = 2.6
HOST_ADVANTAGE = 100
MAX_GOALS = 10
ELO_DIFFERENCE_CACHE_ROUNDING = 1
