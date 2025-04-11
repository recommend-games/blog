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
  - People love a good ranking!
- Discuss possible other ways (if any)
- Elo used in chess, BGA, football etc


## Key idea

- Elo ≠ absolute skill, but relative skill.
- Winning against stronger players gains more points, losing against weaker ones loses more.
- Simple mental model: shifting ratings based on expected vs actual outcomes.


## Formula

- Explain formula, how to convert to probability and rating update
- Winning against stronger players gains more points, losing against weaker ones loses more.
- Imagine putting an ante into the pot according to your expected outcome (p * K), then the winner gets the pot (or split in case of a tie)
- Discuss diffent choices of $$K$$


## Strengths & weaknesses

- Caveats to using Elo:
  - Only meaningful in relative terms
  - Group needs to be sufficiently connected
  - Very sensitive to $$K$$


## Logistic regression

- Interpret Elo rating as logistic regression
- Derive update from stochastic gradient descent


## Example / application: Snooker

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
