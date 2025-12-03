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

**How can we quantify luck and skill in games?** That was the question in the [first instalment]({{<ref "posts/elo_1/index.md">}}) of this series on Elo ratings.


## From Elo ratings to skill distributions

Our first approach was to go through the Elo rating system in some detail. Elo assigns each player a number that reflects their playing strength. The rating difference between two players can be fed into a simple formula to get their expected win probabilities. After each match, the ratings are updated based on the outcome, so over time they tend to track the players' underlying skill.

[Part 2]({{<ref "posts/elo_2/index.md">}}) applied this system to predict the 2025 World Snooker Champion. The model’s favourite, John Higgins, didn’t manage to win his fifth title, but it did give eventual winner Zhao Xintong a 10.6% chance when the bookies only gave him 5.9%. I’ll take that as a personal win — and as evidence that Elo isn’t just numerology, it really does capture something about players’ skills.


### Wider distributions, more skill

What we’re really after is a way to say *how much* skill is involved in a game, and to compare different games with each other. The individual Elo numbers are just a stepping stone. To get anywhere, we have to step back and look at the whole *distribution* of skills, as measured by all players’ Elo ratings.

The basic idea is simple: if a game is mostly luck and players’ decisions don’t matter much, nobody can reliably stay ahead for long. You’ll see some winning streaks, but they’ll wash out again, and everyone’s ratings will cluster around 0. In a game where skill really matters, the strongest players win more often than they lose and slowly drift away from the pack. The result is a much wider Elo distribution: a long tail of very strong players and a long tail of weaker ones.


### A first look: snooker vs tennis

Let’s make this more concrete. We’ve already calculated Elo ratings for snooker, so let’s compare it to another English upper-class sport played on a green surface: tennis. Which one *feels* more skill-based? Our idea is simple: look at the Elo distributions for both and see which one is wider:

{{< img src="elo_distribution_snooker_tennis_wta" alt="The Elo distributions for Snooker and Tennis (WTA)" >}}

According to this plot, the Elo ratings of snooker players are more tightly clustered around 0, which suggests that outcomes are more influenced by luck. Tennis — at least on the WTA, the women’s tour — seems to show a wider spread and therefore more room for skill. But how do we know these distributions are even comparable? And can we turn that vague “more luck, more skill” into an actual number?


## Turning spread into a skill measure

In order to answer these questions we need to properly dive into the science. 🧑‍🔬

I’m going to follow closely the methodology by Peter Duersch, Marco Lambrecht and Jörg Oechssler, described in their paper "[Measuring skill and chance in games](https://doi.org/10.1016/j.euroecorev.2020.103472)" (2020). They come from an economics background and look at games through the lens of gambling regulation: things like roulette or blackjack are usually treated as “games of chance”, while sports such as tennis or snooker are classified as “games of skill”, often on rather fuzzy or traditional grounds. Duersch et al use the *distribution* of Elo ratings in different games to pin down that fuzzy “skill vs chance” distinction with a single number — exactly what we’re trying to do here, just without the money on the line. 🤑

### From Elo ratings to Elo distributions

So what exactly did they do? Their starting point is the Elo rating as a measure of individual skill, as we’ve been discussing already ad nauseam. They then look at the distribution of ratings for all players of a given game and take the *spread* of that distribution as a measure of how much skill is involved: the wider the spread, the more skill. A game that is almost pure luck should have a distribution tightly clustered around 0.


### Standard deviation of Elo ratings

The mathematical measure for the spread of a distribution is its *standard deviation* \\(\sigma\\). The wider the distribution, the larger its standard deviation. Roughly speaking, it’s the root mean squared distance from the average. In our setting, that means \\(\sigma\\) tells us how far we should expect a random player’s skill to lie from the “average” player. You can think of it as the “height” of the skill mountain: a bigger \\(\sigma\\) means the top players sit much higher above the pack — exactly the sort of quantity we want to look at.

So from now on, whenever I talk about the “amount of skill” we see in a game, I’ll use the standard deviation of its Elo ratings, \\(\sigma\\), as the proxy.


### The problem with K

There's an important caveat though: Elo ratings and their distribution crucial depend on \\(K\\), the update factor. If you recall the metaphor from the first article: \\(K\\) is the number of "skill chips" the players put as an ante into the pot. Higher stakes will lead to a wider spread in the distribution. Conversely, if no or very few chips change hands, everybody will end up with roughly the same number, so the spread will be very small.

One possible response would be to fix a choice of \\(K\\) for all games. Unfortunately, that won't work either. Imagine two ladders for exactly the same game with the same population of players: in ladder *A* everyone plays a handful of games per year, in ladder *B* the same people grind hundreds of games a month. We now run Elo with the same \\(K\\) on both datasets. In ladder *A*, only a few "skill chips" ever change hands before the season is over; ratings barely have time to drift apart, so the final distribution stays fairly tight. In ladder *B*, chips slosh back and forth for thousands of rounds; random streaks get amplified, the system has time to separate the strong from the weak, and the rating spread ends up much wider. The underlying game and the underlying skills are identical, yet the dispersion of Elo ratings depends heavily on how often people play and how long we observe them. Fixing \\(K\\) globally doesn’t make the spread an intrinsic property of the game — it just bakes in arbitrary design decisions about volume and time.


### Calibrating K from the data

What Duersch et al suggested instead is to calibrate \\(K\\) such that the resulting Elo ratings will be as good as possible at the task they were designed for: predicting the outcome of the matches. Remember how Elo works: we take the pre-match ratings \\(r_A\\) and \\(r_B\\) of two players *A* and *B*. The sigmoid function then turns the ratings difference \\(r_A-r_B\\) into \\(p_A\\), the probability that *A* will win the match:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

After the match, we compare this prediction with \\(s_A\\), the actual outcome of the match (\\(s_A = 1\\) if *A* won, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a tie). This yields the update rule:

\\[ r_A \leftarrow r_A + K (s_A - p_A). \\]

The basic assumption in DLO's approach is that \\(K\\) is optimally calibrated if those prediction errors \\(s_A - p_A\\) are as small as possible. In other words, for a given \\(K\\) and a fixed set of matches \\(t \in \{1, …, T\}\\), we compute the errors induced by that update rule, and try to minimise the mean of their squares:

\\[ K^\* = \argmin_K \frac{1}{T} \sum_{t=1}^T (s^{(t)} - p^{(t)})^2. \\]

This kind of mean squared error is a standard target loss for training machine learning models, and in the case of probabilistic predictions, this is known as the *Brier loss*. This is a function depending on \\(K\\), and we can apply standard optimisation techniques to obtain \\(K^\*\\), i.e., the update factor which yields the most accurate predictions.[^snooker] Every game will have a different \\(K^\*\\) for the dataset we're looking at; once we have those, we can compute the Elo distributions we were looking for.


### Why K* is not our skill metric

But before we go there, let's pause and consider what information \\(K^\*\\) carries in and of itself. Remember how I compared \\(K\\) to the step size in (stochastic) gradient descent in machine learning? If \\(K^\*\\) is large, it means that we take big steps in each update and every match result provides a strong signal about a player's skills. Isn't that exactly what we're trying to measure? Can we just use \\(K^\*\\) as our coveted metric?

Not quite. First of all, as we've already discussed above, the optimal \\(K\\) will always crucially depend on the player population. Larger sets of matches will tend to have smaller \\(K^\*\\) even for players of exactly the same skill level. That's why we need to calibrate \\(K^\*\\) on the exact dataset we use for our evaluation.

Second, two games might require the same skills, but still have very different learning curves: some slow and steady, others in one single "epiphany". The shape of the learning curve will influence \\(K^\*\\), implying there's no meaningful comparison between the values for different games.

Luckily, the standard deviation of the Elo distribution is much more robust to those issues than \\(K^\*\\) itself.

We've now got the theoretical foundation to compute those Elo distributions (and their standard deviation). What we need is actual game data in order to compute those Elo ratings. I've already teased how this applies to snooker and tennis, and we'll look at a lot more concrete examples in the next article. But first, I'd like to take a closer look at a synthetic example. There are two good reasons to take this extra step: first, it's a simple sandbox example which will help us understand what's going on and santiy check that the method we've described actually works. Second, it'll yield an excellent benchmark which will help us interpret those fairly abstract standard deviations.


## A toy universe of luck and skill

### Extreme worlds: pure chance vs pure skill

Let's start with the two most extreme scenarios: one game of pure chance, i.e., where a coin toss determines the outcome, and one of pure skill, i.e., where the outcome is completely determined by some underlying skill ranking and the stronger player will always defeat the weaker one. What would the Elo distributions look like in those two cases?

In the totally random case no player would ever have any advantage over another, and hence the "skill chips" will just randomly be passed back and forth. Some winning streaks will occur, of course, but in the long run, those will give way to similar losing streaks. So in the limit every player's Elo rating will stay close to 0 and \\(\sigma\\) collapse into a very narrow band around 0.

In the converse case there is one player who will always dominate all other players. This best player will accumulate more and more rating points from other players and never converge to any value. The Elo update is constructed in such a way that large skill differences will result in a negligible point exchange, but in this particular game there's at least one player that will always provide "fresh points" when they face off each other: the second best player. They in turn accumulate an ever higher Elo rating by playing and winning the other players. By following this reasoning down the ranking one can prove that the Elo ratings for the top half of the ranking will grow without bounds, whilst the bottom half falls in a similar fashion, hence leading to an infinite spread in the limit.


### The p-deterministic game

With the extremes out of the way, we can consider an intermediate version of the two: the *\\(p\\)-deterministic game*. The idea is simple: with some probability \\(p\in\[0,1\]\\) the players will play a game of pure skill, and with \\(1-p\\) probability they will play a game of pure chance. In other words, before the match a weighted coin will decide if it's a deterministic game or a coin toss. In the former case, the skill ranking determines the outcome, in the latter case chance. This little *Gedankenspiel* is very easy to understand and reason about. It offers an idealised example of a game with "exactly \\(p\\) skill" involved and hence the benchmark I promised as something we'll be able to compare other games against. Moreover, it's so simple that we easily can run simulations of it and calculate their respective Elo distributions:

{{< img src="elo_distribution_p_deterministic" alt="Elo distribution plots for various p_deterministic games" >}}


### What simulations tell us

This illustrates nicely how games of skill have a much wider spread in their Elo ratings. We can calculate and plot the standard deviation in relation to \\(p\\):

{{< img src="p_deterministic_vs_sigma_two_players" alt="p_deterministic vs σ for two players" >}}

I hope you'll agree that this plot demonstrates a nice functional relationship between \\(p\\) and the Elo standard deviation. We'll be able to exploit this relationship to translate those fairly abstract spreads into the more tangible \\(p\\) as a measure of luck and skill when we apply this method to real games — in a later article.


## What's next

Before we get there, though, we still have to address one big limitation: everything so far assumed two-player games. In the next part of this series we'll extend Elo to proper multi-player tables, and only then move on to real-world data.


[^snooker]: Remember that \\(K=42\\) I've used in the [snooker article]({{<ref "posts/elo_2/index.md">}}#how-elo-predicts-the-winners)? I promised I'll explain in excruciating depth where it came from and I think I kept my promise.
