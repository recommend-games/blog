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

Elo's original paper was targeted at chess, so naturally it was only concerned with two-player games. Likewise, everything I've talked about in this series so far has assumed a simple head-to-head match: one player vs another, winner takes the Elo chips.

But most modern board games don't work like that. Around a real table you'll usually find three, four, sometimes five players battling it out in CATAN, Brass, Gaia Project or whatever your current obsession is. If we want to apply our shiny “skill-o-meter” from part 3 to those games, we need to teach Elo how to handle true multiplayer tables instead of just faking them as a bunch of two-player matches.


## How people fake multiplayer Elo (and why it’s not quite right)

If you're like me and spend an unhealthy amount of your precious time on [Board Game Arena](https://boardgamearena.com/), you might have noticed their Elo implementation. They simply treat multi-player games as a collection of 1‑vs‑1 battles. So if Alice, Bob and Carol play a game, their Elo calculations treat this as *three* matches: Alice vs Bob, Alice vs Carol and Bob vs Carol. If Alice indeed won the game, Bob came in second and Carol last, Alice would win both her “virtual” matches and Bob his against Carol. Elo ratings would then be updated according to the regular formula, with \\(K\\) "adjusted for player count" (I didn't find an up-to-date source as to the details).

Conceptually, this is a neat hack but not quite right: it pretends Alice actually played two independent duels against Bob and Carol, even though in reality all three interacted in the same shared game state and their decisions affected each other at the same time.

Note that for an \\(n\\)-player game there are \\({n \choose 2} = \frac{n(n-1)}{2}\\) pairings, so the number of updates grows quadratically with player count. This kind of growing complexity can really come back to bite you in the behind when it comes to compute, but (a) luckily we don't need to worry about matches with hundreds of players in tabletop gaming and (b) it could be *much* worse, as we shall see in a minute…


## A more principled multiplayer Elo: ranking probabilities


### From table results to expected payoffs

<!-- TODO: Introduce the paper and its authors before. -->

Duersch et al suggest a more principled way to deal with multiplayer tables. Let \\(n\\) be the number of players in the match. Instead of pretending everyone played everyone else in separate duels, they directly model the whole finishing order at once.

The first ingredient is an \\(n\\times n\\) matrix of probabilities:

\\[
  p_{ij} = P(\text{player $i$ finishes in position $j$}).
\\]

You can read row \\(i\\) as "what's the chance player \\(i\\) finishes 1st, 2nd, …, last?" and column \\(j\\) as "who is most likely to end up in position \\(j\\)?".

Just like in the two-player case, we need a numerical payoff to compare expectations with reality. For an \\(n\\)-player game we give the winner \\(n-1\\) points, the runner-up \\(n-2\\), all the way down to 0 for last place.[^flexible-payoff] If there are ties, we give each tied player the average of the payoffs they straddle. That gives us the expected payoff for player \\(i\\):

\\[
  e_i = E[\text{payoff for player $i$}] = \sum_{j=0}^{n-1} p_{ij} (n - 1 - j).
\\]

Once we have that, the Elo update looks exactly like before. Let \\(a_i\\) be the actual payoff (from the final ranking, scaled in the same way). We compare \\(a_i\\) to \\(e_i\\), and shift the rating in the direction of the surprise:

\\[
  r_i \leftarrow r_i + \frac{K}{n-1} (a_i - e_i).
\\]

The factor \\(1/(n-1)\\) just normalises things so that one whole game still corresponds to about \\(K\\) "chips" moving around, as in the two-player version.


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
