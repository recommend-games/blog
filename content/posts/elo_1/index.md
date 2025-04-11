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
- Discuss possible ways (if any)
- Key idea for Elo rating: find a way to predict a game's outcome from players' relative strengths


## Formula

- Explain formula, how to convert to probability and rating update
- Caveats to using Elo:
  - Only meaningful in relative terms
  - Group needs to be sufficiently connected
  - Very sensitive to $$k$$


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
