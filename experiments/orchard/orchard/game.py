import itertools
import logging

import numpy as np

LOGGER = logging.getLogger(__name__)


class OrchardGame:
    def __init__(self) -> None:
        self.gen = np.random.default_rng()
        self.num_trees = 4
        self.fruits_per_tree = 4
        self.die_faces = self.num_trees + 2
        self.raven_steps = 6
        self.reset()

    def reset(self) -> None:
        self.fruits = np.ones(self.num_trees, np.int8) * self.fruits_per_tree
        self.raven = self.raven_steps

    def game_round(self) -> None:
        die = self.gen.integers(0, self.die_faces)
        if die < self.num_trees:  # Regular fruit
            if self.fruits[die] > 0:
                self.fruits[die] -= 1
        elif die == self.num_trees:  # Basket
            max_fruits = np.argmax(self.fruits)
            assert self.fruits[max_fruits] > 0, "Game was already won!"
            self.fruits[max_fruits] -= 1
        else:  # Raven
            assert self.raven > 0, "Game was already lost!"
            self.raven -= 1

    def run_game(self) -> tuple[bool, int]:
        for game_round in itertools.count():
            if np.min(self.fruits) <= 0:
                LOGGER.debug("Game won after %d rounds", game_round)
                return True, game_round  # Game won
            if self.raven <= 0:
                LOGGER.debug("Game lost after %d rounds", game_round)
                return False, game_round  # Game lost
            self.game_round()
        return False, 0  # Never reached
