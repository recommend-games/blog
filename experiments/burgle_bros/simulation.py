# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from collections import defaultdict
from itertools import count
from random import randrange

import jupyter_black
import numpy as np

jupyter_black.load()


# %%
def one_run(
    *,
    dice_pool: int,
    number_of_targets: int,
    die_faces: int = 6,
) -> dict[int, int]:
    assert 0 < number_of_targets <= die_faces

    remaining_targets = set(range(number_of_targets))
    curr_number_of_targets = number_of_targets
    data = {number_of_targets: 0}

    for n in count(1):
        rolled_dice = frozenset(randrange(die_faces) for _ in range(dice_pool))
        remaining_targets -= rolled_dice
        next_number_of_targets = len(remaining_targets)

        if next_number_of_targets < curr_number_of_targets:
            data[next_number_of_targets] = n

        if next_number_of_targets == 0:
            break

        curr_number_of_targets = next_number_of_targets

    results = {
        length: data[0] - data[length]
        for length in range(1, number_of_targets + 1)
        if length in data
    }

    return results


# %%
def many_runs(
    *,
    dice_pool: int,
    min_runs: int,
    die_faces: int = 6,
) -> dict[int, list[int]]:
    results = defaultdict(list)
    for number_of_targets in range(die_faces, 0, -1):
        while len(results[number_of_targets]) < min_runs:
            run = one_run(
                dice_pool=dice_pool,
                number_of_targets=number_of_targets,
                die_faces=die_faces,
            )
            for number, length in run.items():
                results[number].append(length)
    return results


# %%
def simulation(
    *,
    max_pool: int,
    min_runs: int,
    die_faces: int = 6,
) -> tuple[np.ndarray, np.ndarray]:
    results_rolls = np.zeros((die_faces, max_pool))
    results_actions = np.zeros((die_faces, max_pool))
    for dice_pool in range(1, max_pool + 1):
        runs = many_runs(dice_pool=dice_pool, min_runs=min_runs, die_faces=die_faces)
        for number_of_targets, values in sorted(runs.items()):
            values = np.array(values)
            mean_rolls = values.mean()
            mean_actions = mean_rolls + 2 * dice_pool
            print(
                f"{dice_pool=:2d} {number_of_targets=:2d} {mean_rolls=:6.3f} {mean_actions=:6.3f}"
            )
            results_rolls[number_of_targets - 1, dice_pool - 1] = mean_rolls
            results_actions[number_of_targets - 1, dice_pool - 1] = mean_actions
    return results_rolls, results_actions


# %%
results_rolls, results_actions = simulation(max_pool=10, min_runs=100_000)

# %%
print(results_rolls)

# %%
print(results_actions)

# %%
results_actions.argmin(axis=1) + 1
