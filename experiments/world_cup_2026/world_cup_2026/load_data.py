"""Load and validate the processed CSV tables for the simulator."""

from __future__ import annotations

import polars as pl

from . import config


def load_teams() -> pl.DataFrame:
    df = pl.read_csv(config.TEAMS_CSV)
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
