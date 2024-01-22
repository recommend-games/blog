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
        "--num-trees",
        "-t",
        type=int,
        default=4,
        help="Number of trees.",
    )

    parser.add_argument(
        "--fruits-per-tree",
        "-f",
        type=int,
        default=4,
        help="Number of fruits per tree.",
    )

    parser.add_argument(
        "--fruits-per-basket-roll",
        "-b",
        type=int,
        default=1,
        help="Number of fruits picked per basket roll.",
    )

    parser.add_argument(
        "--raven-steps",
        "-r",
        type=int,
        default=6,
        help="Number of steps the raven takes.",
    )

    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=None,
        help="Random seed.",
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

    game = OrchardGame(
        num_trees=args.num_trees,
        fruits_per_tree=args.fruits_per_tree,
        fruits_per_basket_roll=args.fruits_per_basket_roll,
        raven_steps=args.raven_steps,
        random_seed=args.seed,
    )

    full, wins, losses = game.analyse_games(args.num_games)

    print(f"Number of games: {args.num_games}")

    print("Full results:")
    print(full)

    print("Round lengths of wins:")
    print(wins)

    print("Round lengths of losses:")
    print(losses)


if __name__ == "__main__":
    main()
