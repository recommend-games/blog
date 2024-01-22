"""Orchard game implementation."""

import concurrent.futures
import functools
import itertools
import logging
from dataclasses import dataclass
from typing import Generator

import numpy as np
import polars as pl
from tqdm import tqdm

LOGGER = logging.getLogger(__name__)


@dataclass
class OrchardGameConfig:
    """Orchard game configuration."""

    num_trees: int = 4
    fruits_per_tree: int = 4
    fruits_per_basket_roll: int = 1
    raven_steps: int = 6


class OrchardGame:
    """Orchard game implementation."""

    def __init__(
        self,
        config: OrchardGameConfig,
        *,
        random_seed: int | None = None,
    ) -> None:
        self.config = config
        self.die_faces = config.num_trees + 2
        self.gen = np.random.default_rng(random_seed)
        self.reset()

    def reset(self) -> None:
        """Reset the game."""
        self.fruits = (
            np.ones(self.config.num_trees, np.int8) * self.config.fruits_per_tree
        )
        self.raven = self.config.raven_steps

    def game_round(self) -> None:
        """Play one round of the game."""

        die = self.gen.integers(0, self.die_faces)
        LOGGER.debug("Rolled a %d", die)

        if die < self.config.num_trees:  # Regular fruit
            if self.fruits[die] > 0:
                LOGGER.debug("Picked a fruit from tree %d", die)
                self.fruits[die] -= 1

        elif die == self.config.num_trees:  # Basket
            assert np.max(self.fruits) > 0, "Game was already won!"
            for _ in range(self.config.fruits_per_basket_roll):
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

        raise RuntimeError("Unreachable code reached!")

    @classmethod
    def _run_game_wrapper(
        cls,
        _,  # Dummy argument
        *,
        config: OrchardGameConfig,
        random_seed: int | None,
    ) -> tuple[bool, int]:
        game = cls(config=config, random_seed=random_seed)
        return game.run_game()

    @classmethod
    def _run_games(
        cls,
        config: OrchardGameConfig,
        num_games: int,
        *,
        random_seed: int | None = None,
    ) -> Generator[tuple[bool, int], None, None]:
        """Run multiple games."""
        with concurrent.futures.ProcessPoolExecutor() as executor:
            game_results = executor.map(
                functools.partial(
                    cls._run_game_wrapper,
                    config=config,
                    random_seed=random_seed,
                ),
                range(num_games),
            )
            yield from game_results

    @classmethod
    def run_games(
        cls,
        config: OrchardGameConfig,
        num_games: int,
        *,
        random_seed: int | None = None,
        progress_bar: bool = True,
    ) -> pl.DataFrame:
        """Run multiple games."""

        LOGGER.info(
            "Running %d games with %d trees, %d fruits per tree, "
            + "%d fruits picked per basket roll and %d raven steps",
            num_games,
            config.num_trees,
            config.fruits_per_tree,
            config.fruits_per_basket_roll,
            config.raven_steps,
        )

        games = cls._run_games(
            config=config,
            num_games=num_games,
            random_seed=random_seed,
        )
        games_wrapped = tqdm(games, total=num_games) if progress_bar else games
        wins, rounds = zip(*games_wrapped)
        return pl.DataFrame(data={"win": wins, "round_length": rounds})

    @classmethod
    def analyse_games(
        cls,
        config: OrchardGameConfig,
        num_games: int,
        *,
        random_seed: int | None = None,
        progress_bar: bool = True,
    ) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
        """Analyse multiple games."""

        results = cls.run_games(
            config=config,
            num_games=num_games,
            random_seed=random_seed,
            progress_bar=progress_bar,
        )

        full = results.cast(pl.Int64).describe()
        wins = results.filter(pl.col("win")).select(pl.col("round_length")).describe()
        losses = (
            results.filter(pl.col("win").not_())
            .select(pl.col("round_length"))
            .describe()
        )

        return full, wins, losses
