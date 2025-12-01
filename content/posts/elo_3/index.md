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

[Part 2]({{<ref "posts/elo_2/index.md">}}) applied this system to predict the 2025 World Snooker Champion. The model's favourite, John Higgins, didn't manage to win his fifth title, but it did give eventual winner Zhao Xintong a 10.6% chance, whilst the bookies only gave him 5.9%. I'll take that as a personal win — and a sign that Elo indeed manages to capture players' indivual skills, at least to some degree.

What we're trying to achieve though is to measure how much skill is involved in a game and compare games with one another. The individual skill that Elo is measuring is only a stepping stone towards the answer. What we need to do is to take a step back and consider the whole *distribution* of skills as measure by all players' Elo ratings.

The basic idea is this: if a game's outcome is largely determined by luck and players' decisions don't significantly influence who will win or lose, nobody should be able to consistently win in the long run and acquire very high Elo ratings. All players' ratings should cluster around 0. In a game of true skill, the best players will consistently win more often than they lose, and thus reach higher ratings in the long run. We'd expect the whole distribution of Elo ratings to be spread much more widely.

Let's make this more concrete. We've already calculated the Elo ratings for snooker, so let's compare it to another English upper class sport played on a green surface: tennis. Can you tell whether snooker or tennis is the more skillful game? The approach we're suggesting here is to look at the respective Elo distributions and check which one is wider:

{{< img src="elo_distribution_snooker_tennis_wta" alt="The Elo distributions for Snooker and Tennis (WTA)" >}}

At least according to this plot the Elo ratings of snooker players are more tightly clustered around 0 and hence the outcome is more determined by luck, whilst tennis seems to require more skill (at least on the WTA, the women's tour). But how can we be sure that those distributions are even comparable? And can we quantify exactly how much luck and how much skill is involved?

In order to answer these questions we need to properly dive into the science. 🧑‍🔬

I'm going to follow closely the methodology by Peter Duersch, Marco Lambrecht and Jörg Oechssler, described and applied in their paper "[Measuring skill and chance in games](https://doi.org/10.1016/j.euroecorev.2020.103472)" (2020). They have an economics background, so obviously their motivation is money. When it comes to games, that means gambling. Most jurisdictions tightly regulate any form of gambling, but are more permissive when it comes to winning money, e.g., from sports tournaments. The legal argument usually goes that roulette, blackjack & co are predominantly "games of chance", whilst tennis and snooker would be considered "games of skill". The line between "chance" and "skill" is usually drawn arbitrarily — maybe as a matter of tradition, or whoever has the better lobby. Duersch et al use the Elo distribution of players in various games to obtain an objective measure of luck and skills in games. Exactly what we set out to achieve as well. As mentioned before, I'm not a fan of gambling, but luckily their method works even without the monetary motivation. 🤑

So, what exactly did they do? Their starting point are the Elo ratings as measures of individual skills, as we've been discussing already ad nauseam. They then looked at the distribution of ratings for all players of a given game, and considered the spread of this distribution as a measure of skill. The wider the spread, the more skill is involved in a game. Entirely luck based games will have a distribution tightly clustered around 0.

The mathematical measure for the spread of a distribution is its *standard deviation*. The wider the distribution, the larger its standard deviation. It measures the expected (quadratic) difference from the mean. For our use case this means it measures how far we'd expect the skills to deviate from that of an average player — exactly the kind of thing we want to examine.

There's an important caveat though: Elo ratings and their distribution crucial depend on \\(K\\), the update factor. If you recall the metaphor from the first article: \\(K\\) is the number of "skill chips" the players put as an ante into the pot. Higher stakes will lead to a wider spread in the distribution. Conversely, if no or very few chips change hands, everybody will end up with roughly the same number, so the spread will be very small.

One possible response would be to fix a choice of \\(K\\) for all games. Unfortunately, that won't work either. Imagine two ladders for exactly the same game with the same population of players: in ladder *A* everyone plays a handful of games per year, in ladder *B* the same people grind hundreds of games a month. We now run Elo with the same \\(K\\) on both datasets. In ladder *A*, only a few "skill chips" ever change hands before the season is over; ratings barely have time to drift apart, so the final distribution stays fairly tight. In ladder *B*, chips slosh back and forth for thousands of rounds; random streaks get amplified, the system has time to separate the strong from the weak, and the rating spread ends up much wider. The underlying game and the underlying skills are identical, yet the dispersion of Elo ratings depends heavily on how often people play and how long we observe them. Fixing \\(K\\) globally doesn’t make the spread an intrinsic property of the game — it just bakes in arbitrary design decisions about volume and time.

What Duersch et al suggested instead is to calibrate \\(K\\) such that the resulting Elo ratings will be as good as possible at the task they were designed for: predicting the outcome of the matches. Remember how Elo works: we take the pre-match ratings \\(r_A\\) and \\(r_B\\) of two players *A* and *B*. The sigmoid function then turns the ratings difference \\(r_A-r_B\\) into \\(p_A\\), the probability that *A* will win the match:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

After the match, we compare this prediction with \\(s_A\\), the actual outcome of the match (\\(s_A = 1\\) if *A* won, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a tie). This yields the update rule:

\\[ r_A \leftarrow r_A + K (s_A - p_A). \\]

The basic assumption in DLO's approach is that \\(K\\) is optimally calibrated if those prediction errors \\(s_A - r_A\\) are as small as possible. In other words, for a given \\(K\\) and a fixed set of matches \\(t \in \{1, …, T\}\\), we compute the errors induced by that update rule, and try to minimise the mean of their squares:

\\[ K^\* = \argmin_K \frac{1}{T} \sum_{t=1}^T (s^{(t)} - p^{(t)})^2. \\]

This kind of mean squared error is a standard target loss for training machine learning models, and in the case of probabilistic predictions, this is known as the *Brier loss*. This is a function depending on \\(K\\), and we can apply standard optimisation techniques to obtain \\(K^\*\\), i.e., the update factor which yields the most accurate predictions.[^snooker] Every game will have a different \\(K^\*\\); once we have those, we can compute the Elo distributions we were looking for.

But before we go there, let's pause and consider what information \\(K^\*\\) carries in and of itself. Remember how I compared \\(K\\) to the step size in (stochastic) gradient descent in machine learning? If \\(K^\*\\) is large, it means that we take big steps in each update and every match result provides a strong signal about a player's skills. Isn't that exactly what we're trying to measure? Can we just use \\(K^\*\\) as our coveted metric?

Not quite. First of all, as we've already discussed above, the optimal \\(K\\) will always crucially depend on the player population. Larger sets of matches will tend to have smaller \\(K^\*\\) even for players of exactly the same skill level. That's why we need to calibrate \\(K^\*\\) on the exact dataset we use for our evaluation.

Second, two games might require the same skills, but still have very different learning curves: some slow and steady, others in one single "epiphany". The shape of the learning curve will influence \\(K^\*\\), implying there's no meaningful comparison between the values for different games.

Luckily, the standard deviation of the Elo distribution is robust against all those concerns.

We've now got the theoretical foundation to compute those Elo distributions (and their standard deviation). What we need is actual game data in order to compute those Elo ratings. I've already teased how this applies to snooker and tennis, and we'll look at a lot more concrete examples in the next article. But first, I'd like to take a closer look at a synthetic example. There are two good reasons to take this extra step: first, it's a simple sandbox example which will help us understand what's going on and santiy check that the method we've described actually works. Second, it'll yield an excellent benchmark which will help us interpret those fairly abstract standard deviations.

Let's start with the two most extreme scenarios: one game of pure chance, i.e., where a coin toss determines the outcome, and one of pure skill, i.e., where the outcome is completely determined by some underlying skill ranking and the stronger player will always defeat the weaker one. What would the Elo distributions look like in those two cases?

In the totally random case no player would ever have any advantage over another, and hence the "skill chips" will just randomly be passed back and forth. Some winning streaks will occur, of course, but in the long run, those will give way to similar losing streaks. So in the limit every player's Elo rating will stay close to 0 and the overall standard deviation will converge to 0.

In the converse case there is one player who will always dominate all other players. This best player will accumulate more and more rating points from other players and never converge to any value. The Elo update is constructed in such a way that large skill differences will result in a negligible point exchange, but in this particular game there's at least one player that will always provide "fresh points" when they face off each other: the second best player. They in turn accumulate an ever higher Elo rating by playing and winning the other players. By following this reasoning down the ranking one can prove that the Elo ratings for the top half of the ranking will grow without bounds, whilst the bottom half falls in a similar fashion, hence leading to an infinite spread in the limit.

With the extremes out of the way, we can consider an intermediate version of the two: the *\\(p\\)-deterministic game*. The idea is simple: with some probability \\(p\in\[0,1\]\\) the players will play a game of pure skill, and with \\(1-p\\) probability they will play a game of pure chance. In other words, before the match a weighted coin will decide if it's a deterministic game or a coin toss. In the former case, the skill ranking determines the outcome, in the latter case chance. This little *Gedankenspiel* is very easy to understand and reason about. It offers an idealised example of a game with "exactly \\(p\\) skill" involved and hence the benchmark I promised as something we'll be able to compare other games against. Moreover, it's so simple that we easily can run simulations of it and calculate their respective Elo distributions:

TODO: Elo distribution plot with p=0% (?), 10%, …, 90%

This illustrates nicely how games of skill have a much wider spread in their Elo ratings. We can calculate and plot the standard deviation in relation to \\(p\\):

TODO: p vs sigma, two players only, for p=0%, 1%, …, 99% (?)

I hope you'll agree that this plot demonstrates a nice functional relationship between \\(p\\) and the Elo standard deviation. We'll be able to exploit this relationship to translate those fairly abstract spreads into the more tangible \\(p\\) as a measure of luck and skill when we apply this method to real games — in the next article.

Unfortunately, before we get to the fun part, we need a few more technicalities out of the way.

Elo's original paper was targeted at chess, so naturally it was only concerned with two-player games. Likewise, everything I've talked about assumed a pair around the table (or court). But if we want to examine a wider variety of games, including some of the most beloved modern board games, we need to generalise this concept to the multi-player setting.

If you're like me and waste a lot of your time on [Board Game Arena](https://boardgamearena.com/), you might have noticed their Elo implementation. They simply treat multi-player games as a collection of 1-vs-1 battles. So, if Alice, Bob and Carol play a game, their Elo calculations treat this as *three* matches: Alice vs Bob, Alice vs Carol and Bob vs Carol. If Alice indeed won the game, Bob came in second and Carol last, Alice would win both her matches and Bob his against Carol. Elo ratings would then be updated according to the regular formula, with \\(K\\) "adjusted for player count" (I didn't find an up-to-date source as to the details).

Note that for an \\(n\\) player game there are \\({n\choose2}=\frac{n(n+1)}{2}\\) pairings, so the number of updates grows quadratically. This kind of growing complexity can really come to bite one in the behind when it comes to compute, but (a) luckily we don't need to worry about matches with hundreds of players in tabletop gaming and (b) it could be *much* worse, as we shall see in a minute…

Duersch et al chose a different multi-player Elo generalisation. Let \\(n\\) be the number of players in the match we're considering. Their basic premise is to compute an \\(n\times n\\) probability matrix that tells us for each of the players what's the predicted probability that they will end up in each of the positions:

\\[ p_{ij} = P(\text{player $i$ in pos $j$}) \\]

Much like we assigned 1 as the outcome for the winner and 0 for the loser of a two-player game, we associate payoffs[^flexible-payoff] of \\(n-1, …, 0\\) for the players from winner to loser in a multi-player game, where tied players receive the average payoff for the respective ranks. Then the expected outcome for player \\(i\\) is simply the weighted sum of the different rank payoffs:

\\[ e_i = E\[\text{payoff for player $i$}\] = \sum_{j=0}^{n-1} p_{ij} \cdot (n - j - 1). \\]

At this point the Elo update is exactly the same as for the two player case: we compare actual outcome \\(a_i\\) (from the ranking payoff) to the expected outcome (divided by the maximal payoff) and adjust the player's Elo according to whether they over or under performed:

\\[ r_i \leftarrow r_i + \frac{K}{n-1} (a_i - e_i). \\]

The crucial question is thus where said probability matrix comes from. For this we need to calculate the probability for each possible ranking, which we express by the permutation \\(\tau\\):

\\[
  P(\tau) = P(\text{players $\tau(0), …, \tau(n - 1)$ on pos $0, …, n - 1$}) \\\\ 
  = \prod_{i=0}^{n-1} P(\text{player $\tau(i)$ on pos $i$} | \text{players $\tau(0), …, \tau(i - 1)$ on pos $0, …, i - 1$}),
\\]

which is simply the [chain rule of probability](https://en.wikipedia.org/wiki/Chain_rule_(probability)) applied. We obtain an estimate for those factors by applying the [softmax](https://en.wikipedia.org/wiki/Softmax_function) to the ratings of the relevant players:

\\[
  P(\text{$\tau(i)$ on $i$} | \text{$\tau(0), …, \tau(i - 1)$ on $0, …, i - 1$}) = \frac{10^{r_i / 400}}{\sum_{j=i}^{n-1} 10^{r_j / 400}}.
\\]

If you're not familiar with the softmax, you can just think of it as a generalisation of the logistic (or sigmoid) function for multiple dimensions. This is quite a lot, so if I've lost you along the way, just remember we have this formula to calculate the pre-match probability that a particular ranking / permutation \\(\tau\\) will be the result:

\\[ P(\tau) = \prod_{i=0}^{n-1} \frac{10^{r_i / 400}}{\sum_{j=i}^{n-1} 10^{r_j / 400}}. \\]

Now, in order to compute \\(p_{ij}\\), the probability that player \\(i\\) will end up in position \\(j\\), we "simply" need to sum up the probability of all such rankings:

\\[ p_{ij} = \sum_\text{$\tau$ s.t. $\tau(i)=j$} P(\tau). \\]

Uff. That really was a lot. A couple of more notes. First note something I've glossed over: in order to execute that sum over all permutations, i.e., possible rankings, we need to go through all of them — if you remember your combinatorics basics, you'll know that there are \\(n!\\) of them, a function which grows even faster than exponential. Or in other words: this whole calculation is computationally super expensive.

So, does this mean the whole approach is doomed? Luckily, not quite. Most matches will have 6 or fewer players. Since \\(6!=720\\), this explosive growth doesn't really concern us in the majority of cases. Further, there are alternatives to those calculations (namely dynamic programming and Monte Carlo simulations) which make those calculations for higher player counts a little more managable. I'm not going to go into the details here; if you're curious, check out the implementation.

Second, you might wonder if it's really justified to call this a generalisation of two-player Elo since it looks somewhat esoteric at first glance. The best way to convince yourself that this is indeed doing "the right thing" is checking that the multi-player formulae collapse to Elo's original formulation when setting \\(n=2\\). I'll leave this as an exercise to you, dear reader. 🤓


[^snooker]: Remember that \\(K=42\\) I've used in the [snooker article]({{<ref "posts/elo_2/index.md">}}#how-elo-predicts-the-winners)? I promised I'll explain in excruciating depth where it came from and I think I kept my promise.
[^flexible-payoff]: Duersch et al use a flexible payoff structure, but I think it's more confusing than anything else (and looking at their code, they might have confused themselves).
