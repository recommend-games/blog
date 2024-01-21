"""Main entry point for the Orchard experiment."""

import argparse
import logging
import sys
from orchard.game import OrchardGame


def parse_args():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Run the Orchard experiment.")

    parser.add_argument(
        "--num-games",
        "-n",
        type=int,
        default=100_000,
        help="Number of games to simulate.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Verbosity level (repeat for more verbosity).",
    )

    return parser.parse_args()


def main():
    """Run the experiment."""

    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    game = OrchardGame()
    mean_win, mean_rounds = game.analyse_games(args.num_games)

    print(f"Number of games: {args.num_games}")
    print(f"Win rate: {mean_win:.2%}")
    print(f"Mean game length: {mean_rounds:.2f}")


if __name__ == "__main__":
    main()
