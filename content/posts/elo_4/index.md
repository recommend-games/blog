---
title: "TODO: Multi-player Elo"
subtitle: "Elo, part 4: TODO"
slug: elo-part-4-todo
author: Markus Shepherd
type: post
date: 2025-12-12T12:00:00+02:00
draft: true
tags:
  - Elo rating
---

TODO: Proper introduction

> - Hook
> - Motivate this article, outline its scope
> - Summarise the story so far (very briefly)
> - Apologise for this being *even more* technical than part 3.
> - Remind readers: part 3 gave us a 2-player skill-o-meter (σ and p-deterministic).
> - Point out the missing piece: modern board games usually have 3–5 players.
> - Pitch this article as:
> > “teach Elo to handle real multiplayer tables and sanity-check that our skill-o-meter still works there.”

Before we can apply this method to real games, we need a few more technicalities out of the way.


## Why two-player Elo isn’t enough for modern games

> Scope: short, scene-setting.
>
> - Reuse your first two paragraphs (chess → 2p → need multiplayer).
> - Explicitly connect to board games: “if we want to talk about Catan / Gaia Project / Brass etc, two-player Elo isn’t enough.”
> - Keep it brief; this is just motivation.

Elo's original paper was targeted at chess, so naturally it was only concerned with two-player games. Likewise, everything I've talked about assumed a pair around the table (or court). But if we want to examine a wider variety of games, including some of the most beloved modern board games, we need to generalise this concept to the multi-player setting.


## How people fake multiplayer Elo (and why it’s not quite right)

> This is where your BGA bit belongs.
> 
> - Explain BGA’s trick: treat an n-player game as all pairwise matchups.
> - Mention the quadratic growth in pairings (n(n−1)/2).
> - Briefly hint at conceptual issues (transitivity, everyone “plays everyone” even though they don’t, etc) – you don’t need a full critique, just “this is a hack”.
> 
> Goal: make the reader feel “ok, this is clever, but we can do better”.

If you're like me and waste a lot of your time on [Board Game Arena](https://boardgamearena.com/), you might have noticed their Elo implementation. They simply treat multi-player games as a collection of 1-vs-1 battles. So, if Alice, Bob and Carol play a game, their Elo calculations treat this as *three* matches: Alice vs Bob, Alice vs Carol and Bob vs Carol. If Alice indeed won the game, Bob came in second and Carol last, Alice would win both her matches and Bob his against Carol. Elo ratings would then be updated according to the regular formula, with \\(K\\) "adjusted for player count" (I didn't find an up-to-date source as to the details).

Note that for an \\(n\\) player game there are \\({n\choose2}=\frac{n(n+1)}{2}\\) pairings, so the number of updates grows quadratically. This kind of growing complexity can really come to bite one in the behind when it comes to compute, but (a) luckily we don't need to worry about matches with hundreds of players in tabletop gaming and (b) it could be *much* worse, as we shall see in a minute…


## A more principled multiplayer Elo: ranking probabilities

> This is the “big maths” section. I’d split it into subheadings so people can skim.


### From table results to expected payoffs

> - Introduce DLO’s idea: n×n probability matrix p_{ij} = P(\text{player } i \text{ finishes in position } j).
> - Introduce the rank-payoff vector (n-1, …, 0) and the expected payoff
> e_i = \sum_j p_{ij} (n - 1 - j).
> - Show the Elo update rule
> r_i \leftarrow r_i + \frac{K}{n-1}(a_i - e_i).
> - Emphasise intuition: “same logic as 2-player Elo, just scaled for n−1 possible ‘wins’ per game.”
> 
> This is the “what the model is doing” subsection.


Duersch et al chose a different multi-player Elo generalisation. Let \\(n\\) be the number of players in the match we're considering. Their basic premise is to compute an \\(n\times n\\) probability matrix that tells us for each of the players what's the predicted probability that they will end up in each of the positions:

\\[ p_{ij} = P(\text{player $i$ in pos $j$}) \\]

Much like we assigned 1 as the outcome for the winner and 0 for the loser of a two-player game, we associate payoffs[^flexible-payoff] of \\(n-1, …, 0\\) for the players from winner to loser in a multi-player game, where tied players receive the average payoff for the respective ranks. Then the expected outcome for player \\(i\\) is simply the weighted sum of the different rank payoffs:

\\[ e_i = E\[\text{payoff for player $i$}\] = \sum_{j=0}^{n-1} p_{ij} \cdot (n - j - 1). \\]

At this point the Elo update is exactly the same as for the two player case: we compare actual outcome \\(a_i\\) (from the ranking payoff) to the expected outcome (divided by the maximal payoff) and adjust the player's Elo according to whether they over or under performed:

\\[ r_i \leftarrow r_i + \frac{K}{n-1} (a_i - e_i). \\]


### From Elo ratings to ranking probabilities

> This is where all the heavy probability machinery goes.
> 
> - Introduce permutations τ as possible finish orders.
> - Give the chain-rule expression for P(\tau).
> - Explain the softmax step in words first: “given the remaining players, assign probabilities proportional to 10^{rating/400}”.
> - Then show the formal softmax formula.
> - Then the compact product formula for P(\tau).
> - Then define p_{ij} as the sum of P(\tau) over all τ with player i in position j.
> 
> Crucial: keep a “just remember” sentence above or below the maths:
> 
> > “If the formulas lose you at some point, the story is simple: we assign a probability to each possible ranking based on Elo, then sum those probabilities to get how likely each player is to finish in each position.”


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

Uff. That really was a lot.


### Does this really generalise two-player Elo?

> Short reassurance subsection.
> 
> - Pose the doubt: “this looks nothing like classic Elo, is it really the same thing?”
> - Say what you mean by “generalise”: “for n=2, you get back the normal win/loss model.”
> - Either:
> - hand-wave with one sentence (“if you set n=2 the matrix collapses to the 2×2 win/loss case and the update reduces to the usual formula”)
> or
> - give a very short algebra hint.
> - Drop the “exercise to the reader” line or soften it; you’ve already made them eat a lot of equations.

Second, you might wonder if it's really justified to call this a generalisation of two-player Elo since it looks somewhat esoteric at first glance. The best way to convince yourself that this is indeed doing "the right thing" is checking that the multi-player formulae collapse to Elo's original formulation when setting \\(n=2\\). I'll leave this as an exercise to you, dear reader. 🤓


### The price of doing it properly: combinatorics and compute

> This is your n! section.
> 
> - Explain that summing over all permutations is O(n!) and explodes fast.
> - Calm the reader:
> - most board games have ≤ 6 players,
> - 6! = 720 is big but manageable,
> - for higher n you can use dynamic programming / Monte Carlo approximations (point to the code instead of explaining in detail).
> - Optionally mention that this is why your implementation is the bottleneck for the simulations.
> 
> This section is where you’re honest about cost, but don’t lose the plot.

A couple of more notes. First note something I've glossed over: in order to execute that sum over all permutations, i.e., possible rankings, we need to go through all of them — if you remember your combinatorics basics, you'll know that there are \\(n!\\) of them, a function which grows even faster than exponential. Or in other words: this whole calculation is computationally super expensive.

So, does this mean the whole approach is doomed? Luckily, not quite. Most matches will have 6 or fewer players. Since \\(6!=720\\), this explosive growth doesn't really concern us in the majority of cases. Further, there are alternatives to those calculations (namely dynamic programming and Monte Carlo simulations) which make those calculations for higher player counts a little more managable. I'm not going to go into the details here; if you're curious, check out the implementation.


## Extending the toy universe: p-deterministic games with more players

> Now you connect back to Part 3. This is the narrative payoff.

## Multiplayer p-deterministic games

> - Restate the p-deterministic idea, but in the ranking language:
> - fixed underlying skill ranking,
> - with probability p → deterministic ranking by skill,
> - with probability 1−p → random permutation.
> - Emphasise that this is the same toy universe as last time, just with more than two players around the table.

Right, after so much theory you deserve some real world applications … which will follow in the next article. For now, there's still one more thing to check: do the multi-player versions of the \\(p\\)-deterministic game yield the same distribution as the two-player game we've discussed before? The setup remains much the same, just that the outcome in the deterministic case is a ranking of the players based on that underlying ranking of strength, and in the chance case it is a random permutation of the players.


### The σ vs p benchmark still holds for 2–6 players

> - Show / reference the p_deterministic_vs_sigma image.
> - Explain the result in words:
> - all the curves (2–6 players) are smooth and monotone;
> - they lie very close together;
> - the 2-player curve from part 3 is basically sitting on top of the others.
> - Draw the conclusion explicitly:
> - the σ vs p relationship is robust to player count;
> - we can still interpret a measured σ in a real 3–5 player game as “about p ≈ … skill” using this benchmark.
> - This is a good place for the “almost two weeks of CPU” anecdote.

With this, we can run similar simulations to the ones before for various player counts and obtain the same plot:

{{< img src="p_deterministic_vs_sigma" alt="p_deterministic vs σ for various player counts" >}}

I really hope that this plot convinces you that the multi-player system we've discussed above is indeed a useful generalisation of two-player Elo, and also that the spread of the Elo distribution is a really robust measure for skill and luck in games. Talking of the computational effort: the calculations for this last plot took almost two weeks on my laptop, so please don't let those have been in vain. 😅


## Where this leaves us (and what’s next)

> Short wrap-up.
> 
> - Recap the two main wins of this article:
> - we now have a principled multiplayer Elo that reduces to the 2-player version;
> - our σ-as-skill metric behaves nicely for 2–6 players in the p-deterministic universe.
> - One sentence on “what this buys us”:
> “Given real multiplayer game logs, we can now (a) fit Elo, (b) calibrate K, (c) read off σ and map it to a ‘skill fraction’ p.”
> - Tease part 5: “Now we finally get to throw real board game data at this and see which games behave like 30% skill vs 80% skill etc.”

OK, finally I'll shut up about the theory and get to work on the really fun part: applying this whole aparatus to actual board games. I'll promise I won't keep you waiting for long. 🤓


[^flexible-payoff]: Duersch et al use a flexible payoff structure, but I think it's more confusing than anything else (and looking at their code, they might have confused themselves).
