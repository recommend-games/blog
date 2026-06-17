"""Load and validate the processed CSV tables for the simulator."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from . import config


def load_teams(path: Path = config.TEAMS_CSV) -> pl.DataFrame:
    df = pl.read_csv(path)
    if df.height != 48:
        raise RuntimeError(f"teams: expected 48 rows, got {df.height}")
    if df["team_id"].n_unique() != 48:
        raise RuntimeError("teams: team_id values are not unique")
    if df["group_slot"].n_unique() != 48:
        raise RuntimeError("teams: group_slot values are not unique")
    return df


def load_group_matches() -> pl.DataFrame:
    df = pl.read_csv(config.GROUP_MATCHES_CSV)
    if df.height != 72:
        raise RuntimeError(f"group_matches: expected 72 rows, got {df.height}")
    return df


def load_knockout_slots() -> pl.DataFrame:
    df = pl.read_csv(
        config.KNOCKOUT_SLOTS_CSV,
        schema_overrides={"winner_to": pl.Utf8},
    )
    if df.height != 31:
        raise RuntimeError(f"knockout_slots: expected 31 rows, got {df.height}")
    return df


def load_third_place_lookup() -> pl.DataFrame:
    df = pl.read_csv(config.THIRD_PLACE_LOOKUP_CSV)
    if df.height != 495:
        raise RuntimeError(f"third_place_lookup: expected 495 rows, got {df.height}")
    if df["qualified_third_groups"].n_unique() != 495:
        raise RuntimeError("third_place_lookup: keys are not unique")
    return df


def load_results(path: Path = config.RESULTS_CSV) -> pl.DataFrame:
    """Load already-played group results (match_id, home_goals, away_goals).

    home_goals/away_goals are in team_a/team_b orientation: home == team_a_slot,
    away == team_b_slot, matching group_matches.csv.
    """
    df = pl.read_csv(path)
    expected = {"match_id", "home_goals", "away_goals"}
    if set(df.columns) != expected:
        raise RuntimeError(f"results: expected columns {expected}, got {set(df.columns)}")
    if df["match_id"].n_unique() != df.height:
        raise RuntimeError("results: match_id values are not unique")
    if df.height and not df["match_id"].is_between(1, 72).all():
        raise RuntimeError("results: match_id outside the 1-72 group range")
    if df.height and ((df["home_goals"] < 0).any() or (df["away_goals"] < 0).any()):
        raise RuntimeError("results: goals must be non-negative")
    return df
