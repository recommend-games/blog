"""Main entry point for the Orchard experiment."""

from orchard.game import OrchardGame


def main():
    """Run the experiment."""

    game = OrchardGame()
    num_games = 100_000
    mean_win, mean_rounds = game.analyse_games(num_games)

    print(f"Number of games: {num_games}")
    print(f"Win rate: {mean_win:.2%}")
    print(f"Mean game length: {mean_rounds:.2f}")


if __name__ == "__main__":
    main()
