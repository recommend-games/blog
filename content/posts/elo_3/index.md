---
title: Elo as a Skill-O-Meter
subtitle: "Elo, part 3: What rating spreads in a toy universe tell us about luck and skill"
slug: elo-as-a-skill-o-meter
author: Markus Shepherd
type: post
date: 2025-12-03T12:00:00+02:00
tags:
  - Elo rating
  - board games
  - luck vs skill
  - game analytics
  - rating systems
  - probability
  - statistics
  - skill measurement
  - snooker
  - tennis
  - sports analytics
  - simulation
  - p-deterministic games
  - machine learning
---

Whether a game counts as “skill” or “chance” isn’t just a pub argument — in many countries it’s a legal distinction. Roulette and blackjack live on the “chance” side; tennis and chess are filed under “skill”. Different rules, different taxes, different ways for people to lose money.

The trouble is that this line is usually drawn by tradition and gut feeling. Is poker really “more skill” than backgammon? Is snooker closer to roulette or closer to chess? A group of economists tried to answer that question more systematically: instead of arguing, measure how “skill-heavy” a game is in practice by looking at the Elo ratings of all its players. We’ll meet their work properly in a bit.

In this article I want to steal that idea for board games. So far we’ve used Elo to track individual player strength; this time we’ll go one level up. Instead of asking *who* is strong, we’ll look at the whole *distribution* of Elo ratings in a game and see what its spread can tell us about luck and skill — turning Elo into a kind of “skill-o-meter”.


## From Elo ratings to skill distributions

By now the basics of Elo should be familiar: each player gets a rating that reflects their playing strength, rating differences go into a simple formula to give expected win probabilities, and after each match we update those ratings based on whether players beat expectations. If you want the full story (including all the maths and the logistic regression detour), [part 1]({{<ref "posts/elo_1/index.md">}}) has you covered; here we’ll treat Elo as a black box that turns match results into reasonable estimates of player skill.

In [part 2]({{<ref "posts/elo_2/index.md">}}) we applied this system to predict the 2025 World Snooker Champion. The model’s favourite, John Higgins, didn’t manage to win his fifth title, but it did give eventual winner Zhao Xintong a 10.6% chance when the bookies only gave him 5.9%. I’ll take that as a personal win — and as evidence that Elo isn’t just numerology, it really does capture something about players’ skills.


### Wider distributions, more skill

What we’re really after is a way to say *how much* skill is involved in a game, and to compare different games with each other. The individual Elo numbers are just a stepping stone. To get anywhere, we have to step back and look at the whole *distribution* of skills, as measured by all players’ Elo ratings.

The basic idea is simple: if a game is mostly luck and players’ decisions don’t matter much, nobody can reliably stay ahead for long. You’ll see some winning streaks, but they’ll wash out again, and everyone’s ratings will cluster around 0. In a game where skill really matters, the strongest players win more often than they lose and slowly drift away from the pack. The result is a much wider Elo distribution: a long tail of very strong players and a long tail of weaker ones.


### A first look: snooker vs tennis

Let’s make this more concrete. We’ve already calculated Elo ratings for snooker, so let’s compare it to another English upper-class sport played on a green surface: tennis. Can you tell which one is more skill-based? In order to find an objective answer we look at the Elo distributions for both and see which one is wider:

{{< img src="elo_distribution_snooker_tennis_wta" alt="The Elo distributions for Snooker and Tennis (WTA)" >}}

According to this plot, the Elo ratings of snooker players have a much higher peak and shorter tails, which suggests that outcomes are more influenced by luck. Tennis — at least on the WTA, the women’s tour[^tennis-atp] — seems to show a wider spread and therefore more room for skill. But how do we know these distributions are even comparable? And can we turn that vague “more luck, more skill” into an actual number?


## Turning spread into a skill measure

In order to answer these questions, we need to properly dive into the science. 🧑‍🔬


### From Elo ratings to Elo distributions

I’m going to lean on a neat idea by Peter Duersch, Marco Lambrecht and Jörg Oechssler, from their paper "[Measuring skill and chance in games](https://doi.org/10.1016/j.euroecorev.2020.103472)" (2020). They come from an economics background and originally cared about gambling regulation, but the trick itself is much more general: take the Elo ratings for all players in a game, look at their *distribution*, and from that pin down a single number that tells you where the game sits on the spectrum between “pure chance” and “pure skill”. That’s exactly what we’re trying to do here — just for board games instead of casinos. 🤑

So we’ll follow their lead and focus on the *spread* of the Elo distribution as our measure of how much skill shows up in a game.


### Standard deviation of Elo ratings

The mathematical measure for the spread of a distribution is its *standard deviation* \\(\sigma\\). The wider the distribution, the larger its standard deviation. Roughly speaking, it’s the expected (squared) difference from the mean. In our setting, that means \\(\sigma\\) tells us how far, on average, players’ skills lie from the “average” player: a bigger \\(\sigma\\) means the field is more spread out, with larger typical gaps between players — exactly the sort of quantity we want to look at.

So from now on, whenever I talk about the “amount of skill” we see in a game, I’ll use the standard deviation of its Elo ratings, \\(\sigma\\), as the proxy.


### The problem with K

There’s an important caveat: Elo ratings and their distribution crucially depend on \\(K\\), the update factor. If you remember the metaphor from the first article, \\(K\\) is the number of “skill chips” the players put into the pot each game. Higher stakes lead to a wider spread; if almost no chips change hands, everyone ends up with roughly the same number and the spread stays tiny.

A natural idea would be to just fix one \\(K\\) for all games. Unfortunately, that doesn’t work either. Imagine two ladders for exactly the same game with the same population of players. In ladder *A* everyone plays a handful of games per year; in ladder *B* the same people grind hundreds of games a month. We now run Elo with the same \\(K\\) on both datasets. In ladder *A* only a few “skill chips” ever change hands before the season is over, ratings barely have time to drift apart, and the final distribution stays fairly tight. In ladder *B*, chips slosh back and forth for thousands of rounds; random streaks get amplified, the system has time to separate the strong from the weak, and the rating spread ends up much wider. The underlying game and the underlying skills are identical, yet the dispersion of Elo ratings depends heavily on how often people play and how long we observe them. Fixing \\(K\\) globally doesn’t make the spread an intrinsic property of the game — it just bakes in arbitrary design decisions about volume and time.


### Calibrating K from the data

What Duersch et al suggest instead is to calibrate \\(K\\) from the data, so that the Elo ratings are as good as possible at the job they were designed for: predicting who wins. Remember how Elo works: we take the pre-match ratings \\(r_A\\) and \\(r_B\\) of two players *A* and *B*, and feed the difference into a logistic formula to get the predicted win probability for *A*:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

After the match, we compare this prediction with \\(s_A\\), the actual outcome of the match (\\(s_A = 1\\) if *A* won, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a tie), and update:

\\[ r_A \leftarrow r_A + K (s_A - p_A). \\]

The basic assumption in DLO’s approach is that \\(K\\) is “optimal” if these prediction errors \\(s_A - p_A\\) are, on average, as small as possible. For a given \\(K\\) and a fixed set of matches \\(t \in \{1, …, T\}\\), we look at the squared errors and minimise their mean:

\\[ K^\* = \argmin_K \frac{1}{T} \sum_{t=1}^T (s^{(t)} - p^{(t)})^2. \\]

This mean squared error is a standard loss for training machine learning models; when we apply it to probabilistic predictions like this, it’s known as the *Brier loss*. We can search over \\(K\\) to find \\(K^\*\\), the update factor that makes Elo’s predictions as accurate as possible on a given dataset.[^snooker] Different games (and different datasets) will generally end up with different \\(K^\*\\). Once we’ve found \\(K^\*\\), we can run Elo with that value and then look at the resulting rating distributions.


### Why K* is not our skill metric

Before we happily run Elo with \\(K^\*\\) and stare at the resulting distributions, let’s pause and ask what \\(K^\*\\) itself is telling us. Earlier I compared \\(K\\) to a step size in an iterative learning process: a larger \\(K\\) means we take bigger steps on each update and let a single match pull the ratings around more. If the “optimal” \\(K^\*\\) is large, doesn’t that mean each game is very informative about the players’ skills? That sounds suspiciously close to what we’re trying to measure. Can we just use \\(K^\*\\) as our coveted luck–skill number?

Not quite. First of all, as we’ve already discussed above, the optimal \\(K\\) depends strongly on the player population. Larger sets of matches will tend to have smaller \\(K^\*\\), even if the underlying skill levels are exactly the same, simply because with more data you don’t need to react as violently to each individual result. That’s why we have to calibrate \\(K^\*\\) on the exact dataset we’re using.

Second, two games might demand the same underlying skills, but still have very different learning curves: some are slow and steady, others click after a single “epiphany”. Those learning dynamics also feed into \\(K^\*\\): in a game where people improve in big jumps, you’ll see a different “optimal” step size than in a game where everyone creeps up gradually. So even if two games are equally skill-based in the end, their \\(K^\*\\) values can be quite different, and comparing them would be misleading.

Luckily, the standard deviation of the Elo distribution is much more robust to those issues than \\(K^\*\\) itself: it mostly cares about *where everyone ends up*, not about how fast they got there.

We now have the theoretical foundation to compute Elo distributions and their standard deviation. What we still need is actual game data. I’ve already teased how this applies to snooker and tennis, and in the next article we’ll look at many more concrete examples.


## A toy universe of luck and skill

Before we get there, though, I want to take a closer look at a synthetic example. There are two good reasons for this extra step. First, it gives us a simple little sandbox where we can see what’s going on and sanity-check that the method behaves as we expect. Second, it lets us build an excellent benchmark that will help us interpret those fairly abstract standard deviations later on.


### Extreme worlds: pure chance vs pure skill

Let’s start with two extreme scenarios. First, a game of pure chance, where the winner is literally decided by a coin toss. Second, a game of pure skill, where there is some fixed underlying skill ranking and the stronger player always beats the weaker one. What would the Elo distributions look like in those two imagined worlds?

In the totally random case, no player ever has any real advantage over another, so the “skill chips” just get tossed back and forth. Some winning streaks will occur, of course, but in the long run they’re balanced by losing streaks. Elo will keep nudging ratings back towards the middle, and everyone’s rating will hover near 0. The overall spread \\(\sigma\\) settles into a very narrow band around 0.

In the opposite extreme there is a fixed skill ranking, and the strongest player always beats everyone else. This top player will keep siphoning rating points from their opponents and never really settle at a final value. Elo is designed so that very large skill differences lead to only tiny rating changes, but in a world of perfect skill, there is always at least one opponent – the second-best player – who still gives them a little positive update every time they meet. The second-best player in turn keeps gaining points from everyone below them, and so on down the ladder. As a result, the strongest players drift further and further away from the pack, while the weakest ones sink lower and lower. In principle, the spread of ratings can grow without bound.


### The p-deterministic game

With the extremes out of the way, we can now blend them into an intermediate case: the *\\(p\\)-deterministic game*. The idea is simple. We fix an underlying skill ranking for all players. Before each match, we flip a weighted coin: with probability \\(p \in \[0,1\]\\) we play a game of pure skill, where that ranking decides the winner; with probability \\(1-p\\) we play a game of pure chance, where the winner is chosen at random. This little *Gedankenspiel* is easy to understand and to reason about. It gives us an idealised example of a game with “roughly \\(p\\) parts skill and \\(1-p\\) parts luck”, and it serves as the benchmark I promised — something we can later compare real games against. And because the rules are so simple, we can easily run simulations and calculate the resulting Elo distributions:

{{< img src="elo_distribution_p_deterministic" alt="Elo distribution plots for various p_deterministic games" >}}


### What simulations tell us

The first plot already shows the basic pattern: as we turn up \\(p\\) and let skill matter more often, the Elo distribution gets wider and wider. To make this easier to see, we can just take the standard deviation \\(\sigma\\) of each distribution and plot it against \\(p\\):

{{< img src="p_deterministic_vs_sigma_two_players" alt="p_deterministic vs σ for two players" >}}

The result is a smooth, monotone curve: higher \\(p\\) consistently leads to a larger Elo spread \\(\sigma\\). That gives us exactly what we wanted — a way to translate those abstract standard deviations into a more tangible “skill fraction” \\(p\\). Later on, when we look at real games, we’ll be able to say “this game behaves roughly like a 70%-skill world” by matching its Elo spread to this benchmark curve.


## What's next

Before we get there, though, we still have to address one big limitation: everything so far has assumed two-player games. In the next part of this series we’ll teach Elo to handle real multiplayer tables — the kind we actually have in modern board games — and only then move on to real-world data.


[^tennis-atp]: Interestingly, the Elo distribution for men's tennis (ATP) looks more similar to the one for snooker than women's tennis.
[^snooker]: Remember that \\(K=42\\) I used in the [snooker article]({{<ref "posts/elo_2/index.md">}}#how-elo-predicts-the-winners)? I promised I'll explain in excruciating depth where it came from and I think I kept my promise.
