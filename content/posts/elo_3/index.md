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

**How can we quantify luck and skills in games?** This is the question I asked in the [first installment]({{<ref "posts/elo_1/index.md">}}) of this series on Elo ratings.


## From Elo ratings to skill distributions

Our first approach to this topic was to go through the Elo rating system in quite some details. This assigns a number to each player, reflecting their individual strength. The rating difference between two players can then be converted via a simple formula into the respective win probabilities for the players. Based on the outcome ratings will be updated after the match, thus converging over time to the players' true skills.

[Part 2]({{<ref "posts/elo_2/index.md">}}) applied this system to predict the 2025 World Snooker Champion. The model's favourite, John Higgins, didn't manage to win his fifth title, but it did give eventual winner Zhao Xintong a 10.6% chance, whilst the bookies only gave him 5.9%. I'll take that as a personal win — and a sign that Elo indeed manages to capture players' indivual skills, at least to some degree.


### Wider distributions, more skill

What we're trying to achieve though is to measure how much skill is involved in a game and compare games with one another. The individual skill that Elo is measuring is only a stepping stone towards the answer. What we need to do is to take a step back and consider the whole *distribution* of skills as measure by all players' Elo ratings.

The basic idea is this: if a game's outcome is largely determined by luck and players' decisions don't significantly influence who will win or lose, nobody should be able to consistently win in the long run and acquire very high Elo ratings. All players' ratings should cluster around 0. In a game of true skill, the best players will consistently win more often than they lose, and thus reach higher ratings in the long run. We'd expect the whole distribution of Elo ratings to be spread much more widely.


### A first look: snooker vs tennis

Let's make this more concrete. We've already calculated the Elo ratings for snooker, so let's compare it to another English upper class sport played on a green surface: tennis. Can you tell whether snooker or tennis is the more skillful game? The approach we're suggesting here is to look at the respective Elo distributions and check which one is wider:

{{< img src="elo_distribution_snooker_tennis_wta" alt="The Elo distributions for Snooker and Tennis (WTA)" >}}

At least according to this plot the Elo ratings of snooker players are more tightly clustered around 0 and hence the outcome is more determined by luck, whilst tennis seems to require more skill (at least on the WTA, the women's tour). But how can we be sure that those distributions are even comparable? And can we quantify exactly how much luck and how much skill is involved?


## Turning spread into a skill measure

In order to answer these questions we need to properly dive into the science. 🧑‍🔬

I'm going to follow closely the methodology by Peter Duersch, Marco Lambrecht and Jörg Oechssler, described and applied in their paper "[Measuring skill and chance in games](https://doi.org/10.1016/j.euroecorev.2020.103472)" (2020). They have an economics background, so obviously their motivation is money. When it comes to games, that means gambling. Most jurisdictions tightly regulate any form of gambling, but are more permissive when it comes to winning money, e.g., from sports tournaments. The legal argument usually goes that roulette, blackjack & co are predominantly "games of chance", whilst tennis and snooker would be considered "games of skill". The line between "chance" and "skill" is usually drawn arbitrarily — maybe as a matter of tradition, or whoever has the better lobby. Duersch et al use the Elo distribution of players in various games to obtain an objective measure of luck and skills in games. Exactly what we set out to achieve as well. As mentioned before, I'm not a fan of gambling, but luckily their method works even without the monetary motivation. 🤑


### From Elo ratings to Elo distributions

So, what exactly did they do? Their starting point are the Elo ratings as measures of individual skills, as we've been discussing already ad nauseam. They then looked at the distribution of ratings for all players of a given game, and considered the spread of this distribution as a measure of skill. The wider the spread, the more skill is involved in a game. Entirely luck based games will have a distribution tightly clustered around 0.


### Standard deviation of Elo ratings

The mathematical measure for the spread of a distribution is its *standard deviation*. The wider the distribution, the larger its standard deviation. It measures the expected (quadratic) difference from the mean. For our use case this means it measures how far we'd expect the skills to deviate from that of an average player — exactly the kind of thing we want to examine.


### The problem with K

There's an important caveat though: Elo ratings and their distribution crucial depend on \\(K\\), the update factor. If you recall the metaphor from the first article: \\(K\\) is the number of "skill chips" the players put as an ante into the pot. Higher stakes will lead to a wider spread in the distribution. Conversely, if no or very few chips change hands, everybody will end up with roughly the same number, so the spread will be very small.

One possible response would be to fix a choice of \\(K\\) for all games. Unfortunately, that won't work either. Imagine two ladders for exactly the same game with the same population of players: in ladder *A* everyone plays a handful of games per year, in ladder *B* the same people grind hundreds of games a month. We now run Elo with the same \\(K\\) on both datasets. In ladder *A*, only a few "skill chips" ever change hands before the season is over; ratings barely have time to drift apart, so the final distribution stays fairly tight. In ladder *B*, chips slosh back and forth for thousands of rounds; random streaks get amplified, the system has time to separate the strong from the weak, and the rating spread ends up much wider. The underlying game and the underlying skills are identical, yet the dispersion of Elo ratings depends heavily on how often people play and how long we observe them. Fixing \\(K\\) globally doesn’t make the spread an intrinsic property of the game — it just bakes in arbitrary design decisions about volume and time.


### Calibrating K from the data

What Duersch et al suggested instead is to calibrate \\(K\\) such that the resulting Elo ratings will be as good as possible at the task they were designed for: predicting the outcome of the matches. Remember how Elo works: we take the pre-match ratings \\(r_A\\) and \\(r_B\\) of two players *A* and *B*. The sigmoid function then turns the ratings difference \\(r_A-r_B\\) into \\(p_A\\), the probability that *A* will win the match:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

After the match, we compare this prediction with \\(s_A\\), the actual outcome of the match (\\(s_A = 1\\) if *A* won, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a tie). This yields the update rule:

\\[ r_A \leftarrow r_A + K (s_A - p_A). \\]

The basic assumption in DLO's approach is that \\(K\\) is optimally calibrated if those prediction errors \\(s_A - r_A\\) are as small as possible. In other words, for a given \\(K\\) and a fixed set of matches \\(t \in \{1, …, T\}\\), we compute the errors induced by that update rule, and try to minimise the mean of their squares:

\\[ K^\* = \argmin_K \frac{1}{T} \sum_{t=1}^T (s^{(t)} - p^{(t)})^2. \\]

This kind of mean squared error is a standard target loss for training machine learning models, and in the case of probabilistic predictions, this is known as the *Brier loss*. This is a function depending on \\(K\\), and we can apply standard optimisation techniques to obtain \\(K^\*\\), i.e., the update factor which yields the most accurate predictions.[^snooker] Every game will have a different \\(K^\*\\); once we have those, we can compute the Elo distributions we were looking for.


### Why K* is not our skill metric

But before we go there, let's pause and consider what information \\(K^\*\\) carries in and of itself. Remember how I compared \\(K\\) to the step size in (stochastic) gradient descent in machine learning? If \\(K^\*\\) is large, it means that we take big steps in each update and every match result provides a strong signal about a player's skills. Isn't that exactly what we're trying to measure? Can we just use \\(K^\*\\) as our coveted metric?

Not quite. First of all, as we've already discussed above, the optimal \\(K\\) will always crucially depend on the player population. Larger sets of matches will tend to have smaller \\(K^\*\\) even for players of exactly the same skill level. That's why we need to calibrate \\(K^\*\\) on the exact dataset we use for our evaluation.

Second, two games might require the same skills, but still have very different learning curves: some slow and steady, others in one single "epiphany". The shape of the learning curve will influence \\(K^\*\\), implying there's no meaningful comparison between the values for different games.

Luckily, the standard deviation of the Elo distribution is robust against all those concerns.

We've now got the theoretical foundation to compute those Elo distributions (and their standard deviation). What we need is actual game data in order to compute those Elo ratings. I've already teased how this applies to snooker and tennis, and we'll look at a lot more concrete examples in the next article. But first, I'd like to take a closer look at a synthetic example. There are two good reasons to take this extra step: first, it's a simple sandbox example which will help us understand what's going on and santiy check that the method we've described actually works. Second, it'll yield an excellent benchmark which will help us interpret those fairly abstract standard deviations.


## A toy universe of luck and skill

### Extreme worlds: pure chance vs pure skill

Let's start with the two most extreme scenarios: one game of pure chance, i.e., where a coin toss determines the outcome, and one of pure skill, i.e., where the outcome is completely determined by some underlying skill ranking and the stronger player will always defeat the weaker one. What would the Elo distributions look like in those two cases?

In the totally random case no player would ever have any advantage over another, and hence the "skill chips" will just randomly be passed back and forth. Some winning streaks will occur, of course, but in the long run, those will give way to similar losing streaks. So in the limit every player's Elo rating will stay close to 0 and the overall standard deviation will converge to 0.

In the converse case there is one player who will always dominate all other players. This best player will accumulate more and more rating points from other players and never converge to any value. The Elo update is constructed in such a way that large skill differences will result in a negligible point exchange, but in this particular game there's at least one player that will always provide "fresh points" when they face off each other: the second best player. They in turn accumulate an ever higher Elo rating by playing and winning the other players. By following this reasoning down the ranking one can prove that the Elo ratings for the top half of the ranking will grow without bounds, whilst the bottom half falls in a similar fashion, hence leading to an infinite spread in the limit.


### The p-deterministic game

With the extremes out of the way, we can consider an intermediate version of the two: the *\\(p\\)-deterministic game*. The idea is simple: with some probability \\(p\in\[0,1\]\\) the players will play a game of pure skill, and with \\(1-p\\) probability they will play a game of pure chance. In other words, before the match a weighted coin will decide if it's a deterministic game or a coin toss. In the former case, the skill ranking determines the outcome, in the latter case chance. This little *Gedankenspiel* is very easy to understand and reason about. It offers an idealised example of a game with "exactly \\(p\\) skill" involved and hence the benchmark I promised as something we'll be able to compare other games against. Moreover, it's so simple that we easily can run simulations of it and calculate their respective Elo distributions:

TODO: Elo distribution plot with p=0% (?), 10%, …, 90%


### What simulations tell us

This illustrates nicely how games of skill have a much wider spread in their Elo ratings. We can calculate and plot the standard deviation in relation to \\(p\\):

TODO: p vs sigma, two players only, for p=0%, 1%, …, 99% (?)

I hope you'll agree that this plot demonstrates a nice functional relationship between \\(p\\) and the Elo standard deviation. We'll be able to exploit this relationship to translate those fairly abstract spreads into the more tangible \\(p\\) as a measure of luck and skill when we apply this method to real games — in a later article.


## What's next

Before we get there, though, we still have to address one big limitation: everything so far assumed two-player games. In the next part of this series we'll extend Elo to proper multi-player tables, and only then move on to real-world data.


[^snooker]: Remember that \\(K=42\\) I've used in the [snooker article]({{<ref "posts/elo_2/index.md">}}#how-elo-predicts-the-winners)? I promised I'll explain in excruciating depth where it came from and I think I kept my promise.
