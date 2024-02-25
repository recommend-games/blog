---
title: "How long is a game of High Society?"
slug: high-society
author: Markus Shepherd
type: post
date: 2024-02-25T15:00:00+02:00
tags:
  - High Society
  - Reiner Knizia
  - Osprey Games
  - Game length
  - Negative hypergeometric distribution
---

{{% game 220 %}}High Society{{% /game %}} is a classic bidding game by classic designer [Dr Reiner Knizia](https://recommend.games/#/?designer=2), most recently released by [Osprey Games](https://www.ospreypublishing.com/uk/osprey-games/) with a wonderfully classic look:

{{< img src="high_society_cover" alt="Cover of Orchard" size="600x" >}}

The general concept is quite simple: the players are members of said "high society" and are trying to outdo each other in showing off their wealth. The game is played over a series of rounds, and in each round, a card is revealed from a deck of 16 cards. The players then take turns bidding on the card, and the player who wins the bid gets the card. The cards are worth points, and the player with the most points at the end of the game wins.

Here's the twist though: The player with the least money at the end of the game is disqualified (that poor bastard can no longer be accepted as a member of this exclusive club!), so the players are trying to get the most points while also keeping enough money to stay in the game. This provides agonising decisions every turn – as well as a biting satire of the upper class.

One interesting detail is the way the game ends. There's a total of 16 cards to be autioned off in the deck. Four of these cards have a dark background. As soon as the fourth dark card is revealed, the game ends immediately. (That last card isn't sold anymore.) This looming end adds extra tension to the game as players need to take gambles towards the end of the game and try to guess how many more chances they'll get to bid.

This is where the maths comes in. While the strategy is way too deep to be easily analysed, modelling the game length is pretty straightforward and we'll do so in a couple of different ways. We'll start with a simple simulation to understand what's going on. Then we'll develop exact formulae, which will culminate in meeting your new best friend: the negative hypergeometric distribution.

Let's settle one important convention first though: In everything that follows, I'll only count the cards that are actually auctioned off. The last card is never auctioned off, so it doesn't count towards the game length. So the shortest possible game is three rounds long: this happens if all four dark cards are on top of the deck (very unlikely). The longest possible game on the other hand is 15 rounds long: this happens if the card at the bottom of the deck is dark and hence the 15 cards above it will be autioned off (actually pretty likely, as we shall see).


## Simulation

It's really simple to simulate this situation. Just create a bunch of (virtual) decks of 16 cards each, colour four of them dark, then shuffle them. Now we just need to count where in each of the decks the fourth dark card is. If our sample was big enough, this gives us a really good approximation of the distribution of game lengths.

If you know a little bit of Python and the ubiquitous `numpy` library, you can do this in just a few lines of code, so I thought, I'd walk you through it. If you don't care about coding, just skip ahead to the results. (Be warned that formulae are coming up next though, so the code might be the relaxing bit.)

```python
import numpy as np

# Set up the parameters
num_cards = 16
num_dark = 4
num_games = 1_000_000
rng = np.random.default_rng(seed=13)

# Create the decks: num_games rows, num_cards columns
games = np.zeros((num_games, num_cards), dtype=bool)
# Colour the last four columns in each row dark
games[:, :num_dark] = True
# Shuffle each row individually
games = rng.permuted(games, axis=1, out=games)

# Count the game lengths: in each row, sum the number of dark cards revealed so far.
# Every column where this cumulative sum is less than the number of dark cards is a round of the game.
game_lengths = np.sum(np.cumsum(games, axis=1) < num_dark, axis=1)
# Mean and standard deviation of the game lengths
print(game_lengths.mean(), game_lengths.std())
# Histogram the game lengths
unique_lengths, length_counts = np.unique(game_lengths, return_counts=True)
print(dict(zip(unique_lengths, length_counts / num_games)))
```

Don't worry if you can't follow the code immediately, I'll admit to playing a bit of code golf there. The important part are the result anyways, which should look something like this: the mean game length is **12.6 rounds** with a **standard deviation of 2.3**. This is the full distribution of game lengths:

|Length|Probability||Length|Probability|
|---:|---:|-|---:|---:|
|3|0.1%||10|6.6%|
|4|0.2%||11|9.1%|
|5|0.5%||12|12.1%|
|6|1.1%||13|15.8%|
|7|1.9%||14|20.0%|
|8|3.1%||15|25.0%|
|9|4.6%||||

If you prefer the visual representation, here's a histogram of the game lengths:

{{< img src="game_lengths" alt="Histogram of game lengths" >}}

As promised, very short games are extremely rare, but long games are in fact the most common. This isn't necessarily what I would have expected when starting to think about this problem. I think there's a pretty good intuition for why this is the case, but it's instructive to examine the distribution from a more theoretic point of view first.


## Hypergeometric distribution

If you've done your statistics 101, you've indubitably come across questions about poker hands, e.g., how likely is it to get a flush when drawing five cards out of a standard deck of 52? The answer to this question is given by the hypergeometric distribution, which is the distribution of the number of successes in a sequence of $n$ draws without replacement from a finite population of size $N$ containing exactly $K$ successes. The probability mass function of the hypergeometric distribution is given by

$$
P(X = k) = \frac{{K \choose k} {N - K \choose n - k}}{{N \choose n}}.
$$

Now we can frame the game length question in terms of the hypergeometric distribution. With its help, we can easily calculate the probability that the four dark cards are drawn among the first $n$ cards. This is *almost* what we want – it really describes the cumulative probability, i.e., the probability of a game lasting at most $n$ rounds.

## Exact formula, the pedestrian way

TODO


## Negative hypergeometric distribution

TODO


## Outline

* Explain the game
* Relate to Orchard, but explain difference (actual strategy and very meaningful decisions)
* How long is a game? (Why should we care?)
* Simulation
* Work backwards, probability of full length, then one card left, etc.
* Exact formula, pedestrian
* Hypergeometric distribution
* Negative hypergeometric distribution
* Are the probabilities always monotonic? Why? Intuition?
* Did Dr Knizia do this calculation? Why did he make the choices he did?
* What if there were different number of cards?
* Conclusion
