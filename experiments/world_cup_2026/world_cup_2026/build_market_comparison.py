"""Join model probabilities (team_probabilities.csv) with market odds
(market_odds.csv) into outputs/market_comparison.csv.

For each team:
  model_p_winner       - probability from the Monte Carlo simulator
  market_p_winner      - de-vigged Polymarket implied probability
  value_edge           - model_p_winner - market_p_winner; positive means
                         the model thinks the team is undervalued
  value_ratio          - model_p_winner / market_p_winner; useful for
                         Kelly-style bet sizing
  model_rank, market_rank, rank_difference - ranks by p_winner

Sorted by value_edge descending so the article's "model vs market"
narrative reads top-to-bottom.
"""

from __future__ import annotations

import argparse
import csv

from world_cup_2026 import config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditional",
        action="store_true",
        help="Join the conditional model probs against the conditional market odds",
    )
    parser.add_argument(
        "--tag",
        default="conditional",
        metavar="TAG",
        help="Output subdirectory tag for the conditional run (default: 'conditional'). "
             "Use e.g. 'conditional_r32' to preserve earlier conditional outputs.",
    )
    args = parser.parse_args()

    if args.conditional:
        cpaths = config.conditional_paths(args.tag)
        team_probs = cpaths.outputs / "team_probabilities.csv"
        market_csv = cpaths.market_odds_csv
        output = cpaths.outputs / "market_comparison.csv"
    else:
        team_probs = config.OUTPUTS / "team_probabilities.csv"
        market_csv = config.MARKET_ODDS_CSV
        output = config.OUTPUTS / "market_comparison.csv"

    model = {r["team_id"]: r for r in csv.DictReader(open(team_probs))}
    market = {r["team_id"]: r for r in csv.DictReader(open(market_csv))}
    if set(model) != set(market):
        raise RuntimeError(
            f"Team mismatch: only in model = {set(model) - set(market)}, "
            f"only in market = {set(market) - set(model)}"
        )

    rows = []
    for tid, m in model.items():
        mk = market[tid]
        model_p = float(m["p_winner"])
        market_p = float(mk["polymarket_p_winner"])
        rows.append(
            {
                "team_id": tid,
                "team_name": m["team_name"],
                "group": m["group"],
                "elo": int(m["elo"]),
                "model_p_winner": model_p,
                "market_p_winner": market_p,
                "value_edge": model_p - market_p,
                "value_ratio": (model_p / market_p) if market_p > 0 else float("nan"),
                "model_decimal_odds": (1.0 / model_p) if model_p > 0 else float("nan"),
                "market_decimal_odds": float(mk["polymarket_decimal_odds"]),
            }
        )

    rows.sort(key=lambda r: -r["model_p_winner"])
    for i, r in enumerate(rows, start=1):
        r["model_rank"] = i
    rows.sort(key=lambda r: -r["market_p_winner"])
    for i, r in enumerate(rows, start=1):
        r["market_rank"] = i
    for r in rows:
        r["rank_difference"] = r["market_rank"] - r["model_rank"]

    rows.sort(key=lambda r: -r["value_edge"])

    fields = [
        "team_id",
        "team_name",
        "group",
        "elo",
        "model_p_winner",
        "market_p_winner",
        "value_edge",
        "value_ratio",
        "model_decimal_odds",
        "market_decimal_odds",
        "model_rank",
        "market_rank",
        "rank_difference",
    ]
    with output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            for col in ("model_p_winner", "market_p_winner", "value_edge"):
                r[col] = f"{r[col]:.6f}"
            for col in ("value_ratio", "model_decimal_odds", "market_decimal_odds"):
                r[col] = f"{r[col]:.4f}"
            writer.writerow(r)
    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
