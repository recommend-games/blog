"""Reconstruct the model-vs-market probability trajectory across the whole
tournament by walking the git history of market_comparison.csv in each of
the three output phases:

  outputs/                          pre-tournament (article: elo_2c)
  outputs/conditional/               group-stage re-forecasts (elo_2d)
  outputs/conditional_knockout/      knockout-stage re-forecasts (this run)

Each market_comparison.csv already joins model_p_winner and market_p_winner
per team (see build_market_comparison.py). This walks every commit that
touched that file within each phase, oldest first, and stacks the per-team
rows into one long-format CSV so a trajectory chart/table can show how model
conviction and market pricing moved over the course of the tournament.
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path

import git

from world_cup_2026 import config

PHASES = {
    "pre_tournament": "outputs/market_comparison.csv",
    "group_stage": "outputs/conditional/market_comparison.csv",
    "knockout": "outputs/conditional_knockout/market_comparison.csv",
}
SIMULATION_SUMMARY = {
    "pre_tournament": "outputs/simulation_summary.csv",
    "group_stage": "outputs/conditional/simulation_summary.csv",
    "knockout": "outputs/conditional_knockout/simulation_summary.csv",
}
REQUIRED_COLUMNS = {"team_id", "team_name", "model_p_winner", "market_p_winner"}


def _open_repo() -> tuple[git.Repo, Path]:
    """Return the repo plus this project's path relative to the repo root,
    since commit trees are indexed relative to the repo root, not config.ROOT.
    """
    repo = git.Repo(config.ROOT, search_parent_directories=True)
    prefix = config.ROOT.relative_to(Path(repo.working_dir).resolve())
    return repo, prefix


def _read_csv_at(commit: git.Commit, path: str) -> list[dict[str, str]]:
    """Read a CSV blob at a commit; [] if the path didn't exist there yet."""
    try:
        blob = commit.tree[path]
    except KeyError:
        return []
    content = blob.data_stream.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(content)))


def build_trajectory() -> list[dict[str, str]]:
    repo, prefix = _open_repo()

    rows: list[dict[str, str]] = []
    for phase, rel_path in PHASES.items():
        comparison_path = str(prefix / rel_path)
        summary_path = str(prefix / SIMULATION_SUMMARY[phase])
        commits = repo.iter_commits(paths=comparison_path, reverse=True)
        for commit in commits:
            comparison = _read_csv_at(commit, comparison_path)
            if not comparison or not REQUIRED_COLUMNS.issubset(comparison[0]):
                print(f"skipping {phase} {commit.hexsha[:8]}: missing/old schema")
                continue
            summary = _read_csv_at(commit, summary_path)
            elo_snapshot_date = summary[0].get("elo_snapshot_date", "") if summary else ""
            n_results_fixed = summary[0].get("n_results_fixed", "") if summary else ""
            for team in comparison:
                rows.append(
                    {
                        "phase": phase,
                        "commit": commit.hexsha[:8],
                        "commit_date": commit.authored_datetime.isoformat(),
                        "elo_snapshot_date": elo_snapshot_date,
                        "n_results_fixed": n_results_fixed,
                        "commit_subject": commit.summary,
                        "team_id": team["team_id"],
                        "team_name": team["team_name"],
                        "model_p_winner": team["model_p_winner"],
                        "market_p_winner": team["market_p_winner"],
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=config.OUTPUTS / "probability_trajectory.csv",
        type=Path,
        help="Where to write the combined long-format trajectory CSV",
    )
    args = parser.parse_args()

    rows = build_trajectory()

    fields = [
        "phase",
        "commit",
        "commit_date",
        "elo_snapshot_date",
        "n_results_fixed",
        "commit_subject",
        "team_id",
        "team_name",
        "model_p_winner",
        "market_p_winner",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    n_snapshots = len({(r["phase"], r["commit"]) for r in rows})
    print(f"Wrote {len(rows)} rows across {n_snapshots} snapshots to {args.output}")


if __name__ == "__main__":
    main()
