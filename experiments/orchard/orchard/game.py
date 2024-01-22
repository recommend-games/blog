"""Orchard game implementation."""

import itertools
import logging
from typing import Generator

import numpy as np
import polars as pl
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)


class OrchardGame:
    """Orchard game implementation."""

    def __init__(
        self,
        *,
        num_trees: int = 4,
        fruits_per_tree: int = 4,
        fruits_per_basket_roll: int = 1,
        raven_steps: int = 6,
        random_seed: int | None = None,
    ) -> None:
        self.num_trees = num_trees
        self.fruits_per_tree = fruits_per_tree
        self.fruits_per_basket_roll = fruits_per_basket_roll
        self.raven_steps = raven_steps

        self.die_faces = num_trees + 2

        self.gen = np.random.default_rng(random_seed)

        self.reset()

    def reset(self) -> None:
        """Reset the game."""
        self.fruits = np.ones(self.num_trees, np.int8) * self.fruits_per_tree
        self.raven = self.raven_steps

    def game_round(self) -> None:
        """Play one round of the game."""

        die = self.gen.integers(0, self.die_faces)
        LOGGER.debug("Rolled a %d", die)

        if die < self.num_trees:  # Regular fruit
            if self.fruits[die] > 0:
                LOGGER.debug("Picked a fruit from tree %d", die)
                self.fruits[die] -= 1

        elif die == self.num_trees:  # Basket
            assert np.max(self.fruits) > 0, "Game was already won!"
            for _ in range(self.fruits_per_basket_roll):
                max_fruits = np.argmax(self.fruits)
                if self.fruits[max_fruits] == 0:
                    LOGGER.debug("No fruits left on tree %d", max_fruits)
                    break
                LOGGER.debug("Chose a fruit from tree %d", max_fruits)
                self.fruits[max_fruits] -= 1

        else:  # Raven
            assert self.raven > 0, "Game was already lost!"
            self.raven -= 1
            LOGGER.debug("Raven advanced to %d", self.raven)

    def run_game(self) -> tuple[bool, int]:
        """Run a single game."""

        for game_round in itertools.count():
            assert np.all(self.fruits >= 0), "Negative fruits!"
            assert self.raven >= 0, "Negative raven!"

            if np.max(self.fruits) == 0:
                LOGGER.debug("Game won after %d rounds", game_round)
                return True, game_round  # Game won

            if self.raven == 0:
                LOGGER.debug("Game lost after %d rounds", game_round)
                return False, game_round  # Game lost

            self.game_round()

        return False, 0  # Never reached

    def _run_games(self, num_games: int) -> Generator[tuple[bool, int], None, None]:
        """Run multiple games."""
        for _ in range(num_games):
            self.reset()
            yield self.run_game()

    def run_games(self, num_games: int, progress_bar: bool = True) -> pl.DataFrame:
        """Run multiple games."""

        LOGGER.info(
            "Running %d games with %d trees, %d fruits per tree and %d raven steps",
            num_games,
            self.num_trees,
            self.fruits_per_tree,
            self.raven_steps,
        )

        games = self._run_games(num_games)
        games_wrapped = tqdm(games, total=num_games) if progress_bar else games
        wins, rounds = zip(*games_wrapped)
        return pl.DataFrame(data={"win": wins, "round_length": rounds})

    def analyse_games(
        self,
        num_games: int,
        progress_bar: bool = True,
    ) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
        """Analyse multiple games."""

        results = self.run_games(num_games, progress_bar)

        full = results.cast(pl.Int64).describe()
        wins = results.filter(pl.col("win")).select(pl.col("round_length")).describe()
        losses = (
            results.filter(pl.col("win").not_())
            .select(pl.col("round_length"))
            .describe()
        )

        return full, wins, losses
