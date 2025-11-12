---
title: Measuring Skill and Luck with Elo
subtitle: "Elo, part 3: TODO"
slug: measuring-skill-and-luck-with-elo
author: Markus Shepherd
type: post
date: 2025-11-12T12:00:00+02:00
tags:
  - Elo rating
---

**How can we quantify luck and skills in games?** This is the question I asked in the first installment of this series on Elo ratings.

- Methodology: summarising paper
  - Recap 2-player Elo
  - Elo: individual skill -> Elo distribution: measure of skill in the game (within the playing community)
  - Crucial ingredient: Choosing the right update factor k*
    - Explain optimisation
    - Computationally really expensive!
    - Is this a good measure of skill in and of itself?
  - Use std dev of normalised Elo rating distribution as measure of skill!
    - Where does it fall short?
- Example and benchmark: p-deterministic games
  - This should allow us to exactly quantify for a given game what % of its outcome is determined by skill and what % by luck
  - Plot for 2-players
- Generalise Elo to multi-player games
  - Explain their choice
  - Compare to classic 2-player
  - Compare to BGA
  - Super duper expensive
    - Mention DP and MC alternatives to factorial explosion
  - Compare results for multi-player p-deterministic games to 2-player
