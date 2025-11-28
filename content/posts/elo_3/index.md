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

**How can we quantify luck and skills in games?** This is the question I asked in the [first installment]({{<ref "posts/elo_1/index.md">}}) of this series on Elo ratings. Our first approach to this topic was to go through the Elo rating system in quite some details. This assigns a number to each player, reflecting their individual strength. The rating difference between two players can then be converted via a simple formula into the respective win probabilities for the players. Based on the outcome ratings will be updated after the match, thus converging over time to the players' true skills.

[Part 2]({{<ref "posts/elo_2/index.md">}}) applied this system to predict the 2025 World Snooker Champion. The model's favourite, John Higgins, didn't manage to win his fifth title, but it did give eventual winner Zhao Xintong a 10.6% chance, whilst the bookies only gave him 5.9%. I'll take that as a personal win – and a sign that Elo indeed manages to capture players' indivual skills, at least to some degree.

What we're trying to achieve though is to measure how much skill is involved in a game and compare games with one another. The individual skill that Elo is measuring is only a stepping stone towards the answer. What we need to do is to take a step back and consider the whole *distribution* of skills as measure by all players' Elo ratings.

The basic idea is this: if a game's outcome is largely determined by luck and players' decisions don't significantly influence who will win or lose, nobody should be able to consistently win in the long run and acquire very high Elo ratings. All players' ratings should cluster around 0. In a game of true skill, the best players will consistently win more often than they lose, and thus reach higher ratings in the long run. We'd expect the whole distribution of Elo ratings to be spread much more widely.

Let's make this more concrete. We've already calculated the Elo ratings for snooker, so let's compare it to another English upper class sport played on a green surface: tennis. Can you tell whether snooker or tennis is the more skillful game? The approach we're suggesting here is to look at the respective Elo distributions and check which one is wider:

{{< img src="elo_distribution_snooker_tennis_wta" alt="The Elo distributions for Snooker and Tennis (WTA)" >}}

At least according to this plot the Elo ratings of snooker players are more tightly clustered around 0 and hence the outcome is more determined by luck, whilst tennis seems to require more skill (at least on the WTA, the women's tour). But how can we be sure that those distributions are even comparable? And can we quantify exactly how much luck and how much skill is involved?

In order to answer these questions we need to properly dive into the science. 🧑‍🔬

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
