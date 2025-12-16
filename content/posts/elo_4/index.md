---
title: Teaching Elo to Play with Friends
subtitle: "Elo, part 4: How to rate everyone round the table — and keep our skill-o-meter honest"
slug: teaching-elo-to-play-with-friends
author: Markus Shepherd
type: post
date: 2025-12-12T12:00:00+02:00
tags:
  - Elo rating
  - board games
  - luck vs skill
  - game analytics
  - rating systems
  - probability
  - statistics
  - skill measurement
  - simulation
  - p-deterministic games
  - machine learning
  - multiplayer games
---

At some point this year, I let my laptop run flat-out for almost two weeks just to answer one question: *how much of a four-player board game is "skill" and how much is "luck"?* That sounds excessive, but there was a catch: before I could even start those simulations, I had to fix a basic problem. Elo – the rating system we've been happily using so far – only really knows how to handle one-on-one duels.

This article is the missing technical chapter in the series. In [part 1]({{<ref "posts/elo_1/index.md">}}) we met Elo and learned how it turns match results into skill ratings. In [part 2]({{<ref "posts/elo_2/index.md">}}) we sent those ratings to the Crucible to predict the next World Snooker Champion. And in [part 3]({{<ref "posts/elo_3/index.md">}}) we stole a clever idea from Dürsch, Lambrecht and Oechssler to turn the spread of Elo ratings in a two-player "toy universe" into a kind of skill-o-meter: a way to say whether a game behaves more like a 30%-skill world or an 80%-skill world.

There's one obvious gap left: most modern board games aren't tidy head-to-head affairs. Around a real table you'll usually find three, four, sometimes five players battling it out in CATAN, Brass, Gaia Project or whatever your current obsession is. If we want to use our shiny skill-o-meter on those games, we first have to teach Elo how to cope with real multiplayer tables instead of just faking them as a stack of two-player matches.

Fair warning: this part is even more technical than part 3. We'll talk about probability matrices, permutations and a scary-looking formula or two. If that's not your thing, you're still very welcome to skim the maths-heavy bits – I'll keep pointing out the important intuitions along the way. The payoff is worth it: by the end of this article, we'll have a principled multiplayer Elo system and a checked-and-calibrated skill-o-meter that still works when three, four or five people sit down to play.


## Why two-player Elo isn't enough for modern games

Elo's original paper was targeted at chess, so naturally it was only concerned with two-player games. Likewise, everything I've talked about in this series so far has assumed a simple head-to-head match: one player vs another, winner takes the Elo chips.

If we want to apply our shiny "skill-o-meter" from part 3 to the games we actually play, we need to teach Elo how to handle true multiplayer tables instead of just faking them as a bunch of two-player matches.


## How people fake multiplayer Elo (and why it's not quite right)

If you're like me and spend a slightly embarrassing amount of your free time on [Board Game Arena](https://boardgamearena.com/), you might have noticed their Elo implementation. They simply treat multiplayer games as a collection of 1‑vs‑1 battles. So if Alice, Bob and Carol play a game, their Elo calculations treat this as *three* matches: Alice vs Bob, Alice vs Carol and Bob vs Carol. If Alice indeed won the game, Bob came in second and Carol last, Alice would win both her "virtual" matches and Bob his against Carol. Elo ratings would then be updated according to the regular formula, with \\(K\\) "adjusted for player count" (I didn't find an up-to-date source as to the details).

Conceptually, this is a neat hack but not quite right: it pretends Alice actually played two independent duels against Bob and Carol, even though in reality all three interacted in the same shared game state and their decisions affected each other at the same time.

Note that for an \\(n\\)-player game there are \\({n \choose 2} = \frac{n(n-1)}{2}\\) pairings, so the number of updates grows quadratically with player count. This kind of growing complexity can really come back to bite you in the behind when it comes to compute, but (a) luckily we don't need to worry about matches with hundreds of players in tabletop gaming and (b) it could be *much* worse, as we shall see in a minute…


## A more principled multiplayer Elo: ranking probabilities

In [part 3]({{<ref "posts/elo_3/index.md">}}), we already leaned on a neat idea by Peter Dürsch, Marco Lambrecht and Jörg Oechssler from their paper "[Measuring skill and chance in games](https://doi.org/10.1016/j.euroecorev.2020.103472)" (2020). There we used their framework to turn the spread of Elo ratings into a "skill-o-meter" for two-player games. In this article, we're going back to the same well: DLO also propose a way to run Elo on proper multiplayer tables, and that's exactly the tool we need for modern board games.


### From table results to expected payoffs

Dürsch et al suggest a more principled way to deal with multiplayer tables. Let \\(n\\) be the number of players in the match. Instead of pretending everyone played everyone else in separate duels, they directly model the whole finishing order at once.

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

This is where things get a bit heavy. If you're mostly here for the big picture, feel free to skim or even skip the formulae in this section — I'll summarise the important part again at the end.

Conceptually, what we want is simple: for a given set of Elo ratings, we assign a probability to each possible finishing order of the players. Stronger players should be more likely to end up near the top, weaker ones near the bottom. Once we have those probabilities, we can add them up to get the chance that a particular player finishes in a particular position.

Formally, we write a possible ranking as a permutation \\(\tau\\) of \\(\{0, \dots, n-1\}\\), where \\(\tau(j)\\) tells us *which player* ends up in position \\(j\\) (with \\(j=0\\) for the winner, \\(j=1\\) for second place, and so on). The probability of seeing a particular ranking \\(\tau\\) can be written using the [chain rule of probability](https://en.wikipedia.org/wiki/Chain_rule_(probability)):

\\[
  P(\tau) = P(\text{players $\tau(0), \dots, \tau(n - 1)$ on positions $0, \dots, n - 1$}) \\\\
  = \prod_{j=0}^{n-1} P(\text{player $\tau(j)$ on position $j$} \mid \text{players $\tau(0), \dots, \tau(j - 1)$ fixed above}).
\\]

To estimate those conditional probabilities, Dürsch et al use the [softmax](https://en.wikipedia.org/wiki/Softmax_function) over Elo ratings. Softmax is just the multiplayer cousin of the Elo win-probability formula: you take a "strength score" for each player, exponentiate it, and then divide by the sum so that everything adds up to 1. At each step \\(j\\), we look at the players who haven't been placed yet and assign probabilities proportional to \\(10^{r / 400}\\), just like in the two-player Elo formula. If we write \\(r_i\\) for the current rating of player \\(i\\), this gives:

\\[
  P(\text{player $\tau(j)$ on position $j$} \mid \text{players $\tau(0), \dots, \tau(j - 1)$ fixed above}) \\\\
  = \frac{10^{r_{\tau(j)} / 400}}{\sum_{k=j}^{n-1} 10^{r_{\tau(k)} / 400}}.
\\]

Plugging this into the chain rule expression yields a compact formula for the probability of a full ranking \\(\tau\\):

\\[
  P(\tau) = \prod_{j=0}^{n-1} \frac{10^{r_{\tau(j)} / 400}}{\sum_{k=j}^{n-1} 10^{r_{\tau(k)} / 400}}.
\\]

Now, to get the entries of our probability matrix, we just have to sum over all rankings that put a given player in a given position. Remember that \\(p_{ij}\\) is the probability that player \\(i\\) finishes in position \\(j\\). With the convention \\(\tau(j) = i\\) meaning "player \\(i\\) sits in position \\(j\\)", we have:

\\[
  p_{ij} = \sum_{\tau \text{ with } \tau(j) = i} P(\tau).
\\]

If the formulae lost you at some point, that's OK — the story is simple: we assign a probability to each possible finishing order based on the Elo ratings, and then sum those probabilities to find out how likely each player is to end up in each position. That's all you really need to remember from this section.


### Does this really generalise two-player Elo?

You might still wonder if it's really justified to call this a generalisation of two-player Elo, since it looks rather different at first glance. The crucial sanity check is that when we only have \\(n = 2\\) players at the table, all of this machinery collapses back to the usual head-to-head model: there are only two possible rankings, the probability matrix reduces to the familiar win–loss probabilities, the payoff vector \\((1, 0)\\) just scores win vs loss, and the update rule becomes exactly the original Elo formula again.[^exercise] You don't need to wade through the algebra – the important point is that for ordinary two-player encounters, this system behaves just like classic Elo.


### The price of doing it properly: combinatorics and compute

There is one big catch we've glossed over so far. To calculate the entries of the probability matrix \\(p_{ij}\\), we have to sum \\(P(\\tau)\\) over all possible rankings \\(\\tau\\). If you remember your combinatorics basics, you'll know that there are \\(n!\\) permutations of \\(n\\) players – a function that grows even faster than exponential. In other words: a straightforward implementation of this model is computationally very expensive.

Does this mean the whole approach is doomed? Luckily, not quite. Most board games have at most five or six players, and \\(6! = 720\\) is big but still perfectly manageable on a modern computer. That covers the vast majority of situations we care about in tabletop gaming.

For higher player counts there are more efficient tricks (for example dynamic programming and Monte Carlo approximations) that avoid looping over all permutations explicitly. I'm not going to go into the details here; if you're curious, you can have a look at the implementation in the code for this article – but for our purposes it's enough to know that the full model is tractable for realistic games.


### Multiplayer p-deterministic games

Right, after so much theory you deserve something a bit more concrete. Real-world applications will come in the next article; for now, there's still one more thing to check: do the multiplayer versions of the \\(p\\)-deterministic game behave in the same way as the two-player toy world we built in part 3?

The setup remains almost the same. We fix an underlying skill ranking for all players. For each game, we flip a weighted coin: with probability \\(p\\) we play a game of pure skill, where players finish in order of their underlying strength; with probability \\(1-p\\) we play a game of pure chance, where the finishing order is just a random permutation of the players. It's the same toy universe as before, just with more than two players sitting at the table each time.


### The σ vs p benchmark still holds for up to 15 players

With this multiplayer version of the \\(p\\)-deterministic game in hand, we can run the same kind of simulations as before. For each choice of \\(p\\) and for player counts between 2 and 15, we let lots of games play out, calibrate \\(K\\) on the simulated match data, compute the resulting Elo ratings and record their standard deviation \\(\\sigma\\). Plotting \\(\\sigma\\) against \\(p\\) for each player count gives us this family of curves:

{{< img src="p_deterministic_vs_sigma" alt="p_deterministic vs σ for various player counts" >}}

All of these curves are smooth and strictly increasing: as we turn up \\(p\\) and let skill matter more often, the Elo spread \\(\\sigma\\) grows, just like in the two-player case. More interestingly, when we plot these player counts from 2 up to 15, the points for different player counts are essentially indistinguishable: for each value of \\(p\\), all the coloured dots sit almost exactly on top of each other. Any tiny visible wobble at very high \\(p\\) is well within the limits of simulation noise and numerical quirks.

That's precisely the behaviour we were hoping to see. Empirically, in this toy universe \\(\\sigma\\) is effectively a function of \\(p\\) alone and — within our numerical precision — invariant to how many players sit at the table, even up to 15. In practical terms, this means that if we measure a standard deviation \\(\\sigma\\) in a real three-, four- or five-player game, we can safely read off a corresponding "\\(p\\)-skill world" from this benchmark without worrying about the exact player count.

Talking of the computational effort: getting this last plot alone down to *only* about two weeks of wall-clock time on my poor laptop took a fair bit of optimisation. The result might look a little underwhelming after all that build-up, but that's exactly the point: after grinding through all those simulations, the curves stubbornly agree that player count basically doesn't matter. 🔥😅🤓


## Where this leaves us (and what's next)

We've covered a lot of ground in this article, but the payoff is twofold.

First, we now have a principled way to run Elo on real multiplayer tables. Instead of faking CATAN or Brass as a pile of head-to-head duels, we can model the whole finishing order at once, get sensible expected payoffs for each seat, and update ratings in a way that reduces to classic two-player Elo when there are only two people at the table.

Second, we've stress-tested our "Elo-as-a-skill-o-meter" from part 3 in a richer toy universe. In those \\(p\\)-deterministic worlds, the standard deviation \\(\\sigma\\) of Elo ratings turns out to depend almost entirely on \\(p\\) and, within numerical accuracy, not on how many players sit down to play. That means \\(\\sigma\\) really does behave like a calibrated skill dial we can use for 2–6 player games.

Put together, this gives us the toolset we wanted: given real multiplayer game logs, we can (a) fit Elo using the multiplayer update, (b) calibrate \\(K\\) on predictive accuracy, (c) read off the resulting \\(\\sigma\\) and map it to a "skill fraction" \\(p\\) using our benchmark curve.

Next time, we'll finally unleash this machinery on actual board games. We'll look at real play logs, see which games behave more like 30%-skill worlds and which ones look closer to 80% skill, and maybe settle a few pub arguments along the way. 🤓


[^flexible-payoff]: Dürsch et al use a flexible payoff structure which makes the formulae and implementation more confusing. For our purposes, the fixed payoff based on ranks is enough, so I tried to keep things simple.
[^exercise]: If you're itching to do the algebra yourself, be my guest — that's the unofficial "exercise to the reader" for this section. I decided you didn't need to watch me juggle minus signs for a page.
