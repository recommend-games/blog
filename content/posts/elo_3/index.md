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

I'm going to follow closely the methodology by TODO, described and applied in their paper TODO. They have an economics background, so obviously their motivation is money. When it comes to games, that means gambling. Most jurisdictions tightly regulate any form of gambling, but are more permissive when it comes to winning money, e.g., from sports tournaments. The legal argument usually goes that roulette, blackjack & co are predominantly “games of chance”, whilst tennis and snooker would be considered “games of skill”. The line between “chance” and “skill” is usually drawn arbitrarily - maybe as a matter of tradition, or whoever has the better lobby. TODO et al use the Elo distribution of players in various games to obtain an objective measure of luck and skills in games. Exactly what we set out to achieve as well. As mentioned before, I'm not a fan of gambling, but luckily their method works even without the monetary motivation. 🤑

So, what exactly did they do? Their starting point are the Elo ratings as measures of individual skills, as we've been discussing already ad nauseam. They then looked at the distribution of ratings for all players of a given game, and considered the spread of this distribution as a measure of skill. The wider the spread, the more skill is involved in a game. Entirely luck based games will have a distribution tightly clustered around 0.

The mathematical measure for the spread of a distribution is its standard deviation. The wider the distribution, the larger its standard deviation. It measures the expected difference from the mean. For our use case this means it measures how far we'd expect the skills to deviate from that of an average player - exactly the kind of thing we want to examine.

There's an important caveat though: Elo ratings and their distribution crucial depend on K, the update factor. If you recall the metaphor from the first article: K is the number of “skill chips” the players put as an ante into the pot. Higher stakes will lead to a wider spread in the distribution. Conversely, if no or very few chips change hands, everybody will end up with roughly the same number, so the spread will be very small.

One possible response would be to fix a choice of K for all games. Unfortunately, that won't work either. Imagine two ladders for exactly the same game with the same population of players: in ladder A everyone plays a handful of games per year, in ladder B the same people grind hundreds of games a month. We now run Elo with the same K on both datasets. In ladder A, only a few “skill chips” ever change hands before the season is over; ratings barely have time to drift apart, so the final distribution stays fairly tight. In ladder B, chips slosh back and forth for thousands of rounds; random streaks get amplified, the system has time to separate the strong from the weak, and the rating spread ends up much wider. The underlying game and the underlying skills are identical, yet the dispersion of Elo ratings depends heavily on how often people play and how long we observe them. Fixing K globally doesn’t make the spread an intrinsic property of the game — it just bakes in arbitrary design decisions about volume and time.

What TODO et al suggested instead is to calibrate K such that the resulting Elo ratings will be as good as possible at the task they were designed for: predicting the outcome of the matches. Remember how Elo works: we take the pre-match ratings r_A and r_B of two players A and B. The sigmoid function then turns the ratings difference r_A - r_B into p_A, the probability that A will win the match:

TODO: p_A formula

After the match, we compare this prediction with s_A, the actual outcome of the match (s_A = 1 if A won, 0 if they lost and 0.5 in case of a tie). This yields the update rule:

TODO: Elo update

The basic assumption in TODO’s approach is that K is optimally calibrated if those prediction errors s_A - r_A are as small as possible. In other words, for a given K and a fixed set of matches TODO, we compute the errors induced by that update rule, and try to minimise the mean of their squares. This (rooted) mean squared error is a standard target loss for training machine learning models, and in the case of probabilistic predictions, this is known as the Brier loss. This is a function depending on K, and we can apply standard optimisation techniques to obtain K*, the argument that minimises the Brier loss, i.e., the update factor which yields the most accurate predictions. The authors calculate those optimal K* for each game and use those to calculate the Elo distributions.

TODO: Is this a good measure of skill in and of itself? Why does it fall short?

TODO: Mention the compute that goes into this?


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
