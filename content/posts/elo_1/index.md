---
title: Elo ratings explained
subtitle: How to measure players' skills in games
slug: elo
author: Markus Shepherd
type: post
date: 2025-04-19T12:00:00+03:00
tags:
  - Elo rating
  - Snooker
---

## Introduction

- How to measure skills in games?
- Why does it matter to measure this? Applications?
  - Find opponents to match your (current) skills well
    - E.g., it wouldn't be much fun for either of us if I played chess against Magnus Carlsen, nor would I even learn anything from such a match, so we need a way to find a player of similar strength for us to have fun and/or learn anything.
  - People love a good ranking!
- Discuss possible other ways (if any)
- Elo used in chess, BGA, football etc
- First in a series of (four?) articles on Elo


## Key idea

- Elo ≠ absolute skill, but relative skill.
- Winning against stronger players gains more points, losing against weaker ones loses more.
- Simple mental model: shifting ratings based on expected vs actual outcomes.
- Imagine putting an ante into the pot according to your expected outcome, then the winner gets the pot (or split in case of a tie)


## Formula

- Explain formula, how to convert to probability and rating update
- Pot metaphor: players put $$p \cdot K$$ chits into the pot
- Discuss diffent choices of $$K$$


## Logistic regression

- Interpret Elo rating as logistic regression
- Derive update from stochastic gradient descent


## Strengths & weaknesses

- Positive:
  - It's pretty simple and fairly interpretable
  - It has a descent performance at predicting outcomes of, e.g., chess matches
- Caveats to using Elo:
  - Only meaningful in relative terms
  - Group needs to be sufficiently connected
  - Very sensitive to $$K$$ (tie back to logistic regression and the difficulty of picking a good learning rate)


## Example / application: Snooker

**Best factor this out into a separate article. Publish the general Elo article on 2025-04-13, and the Snooker article on 2025-04-19, in time for the opening of the World Snooker Championship.**

- World Championship opening today
- How does it apply to Snooker
- Sample calculations
- Winner prediction / simulation?
  - Use Elo ratings we just calculated to predict matches
  - Simulate tournaments where each match is decided according to Elo probability predictions
  - Who is going to be the next champion?


## Conclusion / outlook

- Summary
- What's next?
- Tease / outline the other articles
