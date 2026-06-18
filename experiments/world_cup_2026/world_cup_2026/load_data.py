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
    """Load already-played results (match_id, home_goals, away_goals, winner).

    home_goals/away_goals are in team_a/team_b orientation: home == team_a_slot,
    away == team_b_slot, matching group_matches.csv.

    Group rows (match_id 1-72) pin the scoreline and leave ``winner`` empty.
    Knockout rows (match_id >= 73) pin which team advances via ``winner`` (a
    team_id); the recorded goals are the regulation/extra-time score and are
    kept for the record but the simulator only uses ``winner``. The ``winner``
    column is optional in the file when no knockout rows are present.
    """
    df = pl.read_csv(path)
    required = {"match_id", "home_goals", "away_goals"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"results: missing columns {missing}")
    extra = set(df.columns) - (required | {"winner"})
    if extra:
        raise RuntimeError(f"results: unexpected columns {extra}")
    if "winner" not in df.columns:
        df = df.with_columns(pl.lit("").alias("winner"))
    df = df.with_columns(pl.col("winner").cast(pl.Utf8).fill_null(""))

    if df["match_id"].n_unique() != df.height:
        raise RuntimeError("results: match_id values are not unique")
    if df.height and not df["match_id"].is_between(1, 104).all():
        raise RuntimeError("results: match_id outside the 1-104 tournament range")
    if df.height and ((df["home_goals"] < 0).any() or (df["away_goals"] < 0).any()):
        raise RuntimeError("results: goals must be non-negative")

    is_ko = pl.col("match_id") > 72
    blank = pl.col("winner").str.len_chars() == 0
    if df.filter(is_ko & blank).height:
        raise RuntimeError("results: knockout rows (match_id >= 73) need a winner team_id")
    if df.filter(~is_ko & ~blank).height:
        raise RuntimeError("results: group rows (match_id <= 72) must leave winner empty")
    return df
