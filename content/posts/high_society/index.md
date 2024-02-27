---
title: "How long is a game of High Society?"
slug: high-society
author: Markus Shepherd
type: post
date: 2024-02-27T22:33:00+02:00
tags:
  - High Society
  - Reiner Knizia
  - Osprey Games
  - Game length
  - Negative hypergeometric distribution
  - Python
  - Simulation
  - numpy
---

{{% game 220 %}}High Society{{% /game %}} is a classic bidding game by classic designer [Dr Reiner Knizia](https://recommend.games/#/?designer=2), most recently released by [Osprey Games](https://www.ospreypublishing.com/uk/osprey-games/) with a wonderfully classic look:

{{< img src="high_society_cover" alt="Cover of High Society" size="600x" >}}

The general concept is quite simple: the players are members of said "high society" and are trying to outdo each other in showing off their wealth. The game is played over a series of rounds, and in each round, a card is revealed from a deck of 16 cards. The players then take turns bidding on the card, and the player who wins the bid gets the card. The cards are worth points, and the player with the most points at the end of the game wins.

Here's the twist though: The player with the least money at the end of the game is disqualified (that poor bastard can no longer be accepted as a member of this exclusive club!), so the players are trying to get the most points while also keeping enough money to stay in the game. This provides agonising decisions every turn – as well as a biting satire of the upper class.

One interesting detail is the way the game ends. There's a total of 16 cards to be autioned off in the deck; 4 of these cards have a dark background. As soon as the 4th dark card is revealed, the game ends immediately. (That last card isn't sold anymore.) This looming end adds extra tension to the game as players need to take gambles towards the end of the game and try to guess how many more chances they'll get to bid.

This is where the maths comes in. While the strategy is way too deep to be easily analysed (and involves some interesting meta in pricing the cards), modelling the game length is pretty straightforward and we'll do so in a couple of different ways. We'll start with a simple simulation to understand what's going on. Then we'll develop exact formulae, which will culminate in meeting your new best friend: the negative hypergeometric distribution.

Let's settle one important convention first though: In everything that follows, I'll only count the cards that are actually auctioned off. The last card is never auctioned off, so it doesn't count towards the game length. This means that the shortest possible game is 3 rounds long: this happens if all 4 dark cards are on top of the deck (very unlikely). The longest possible game on the other hand is 15 rounds long: this happens if the card at the bottom of the deck is dark and hence the 15 cards above it will be autioned off (actually pretty likely, as we shall see).


## Simulation

It's really simple to simulate this situation. Just create a bunch of (virtual) decks of 16 cards each, colour 4 of them dark, then shuffle them. Now we just need to count where in each of the decks the 4th dark card is. If our sample was big enough, this gives us a really good approximation of the distribution of game lengths.

If you know a little bit of Python and the ubiquitous `numpy` library, you can do this in just a few lines of code, so I thought I'd walk you through it. If you don't care about coding, just skip ahead to the results. (Be warned that formulae are coming up next though, so the code might be the relaxing bit.)

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

# Count the game lengths: in each row,
# sum the number of dark cards revealed so far.
# Every column where this cumulative sum is
# less than the number of dark cards is a round of the game.
game_lengths = np.sum(np.cumsum(games, axis=1) < num_dark, axis=1)

# Mean and standard deviation of the game lengths
print(game_lengths.mean(), game_lengths.std())

# Histogram the game lengths
unique_lengths, length_counts = np.unique(game_lengths, return_counts=True)
print(dict(zip(unique_lengths, length_counts / num_games)))
```

Don't worry if you can't follow the code immediately, I'll admit to playing a bit of code golf there. The important part are the results anyways, which should look something like this: the mean game length is **12.6 rounds** with a **standard deviation of 2.3**. This is the full distribution of game lengths:

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

As promised, very short games are extremely rare, whilst long games are in fact the most common. This isn't necessarily what I would have expected when starting to think about this problem. I think there's a pretty good intuition for why this is the case, but it's instructive to examine the distribution from a more theoretic point of view first.


## Hypergeometric distribution

If you've done your statistics 101, you've indubitably come across questions about poker hands. E.g., how likely is it to get a flush when drawing 5 cards out of a standard deck of 52? The answer to this question can be calculated using the hypergeometric distribution. If you find the name intimidating, wait till you see the formula:

\\[ p_\text{HG}(N, K, n; k) = \frac{{K \choose k} {N - K \choose n - k}}{{N \choose n}}. \\]

So let's take this step by step. Applied to our situation, we have a total of \\(N = 16\\) cards, \\(K = 4\\) of which are "successes", i.e., the dark ones. In the standard application of the hypergeometric distribution, we'd draw a fixed number of \\(n\\) cards and want to know the probability that exactly \\(k\\) of them are dark. Our problem however is a little different: we need to fix \\(k = 4\\) dark cards to be drawn and want to know the probability that this happens within the first \\(n\\) draws. This is *almost* what we want – it describes the probability that the game lasts *less* than \\(n\\) rounds. Let \\(X\\) be the random variable that describes the game length. Then what we just said can be expressed as

\\[ P(X \lt n) = p_\text{HG}(16, 4, n; 4) = \frac{{4 \choose 4} {16 - 4 \choose n - 4}}{{16 \choose n}} = \frac{{12 \choose n - 4}}{{16 \choose n}}. \\]

Now, it's easy to recover the probability is that the game lasts *exactly* \\(n\\) rounds:

\\[ P(X = n) = P(X \lt n + 1) - P(X \lt n) = \frac{{12 \choose n - 3}}{{16 \choose n + 1}} - \frac{{12 \choose n - 4}}{{16 \choose n}}, \\]

where \\(n \ge 4\\) to make sure the binomial coefficients are defined (I'll leave \\(P(X = 3)\\) as an exercise to the reader). If you're bored, you can flex your algebraic muscles and simplify this expression:

\\[ P(X = n) = \frac{12! \cdot n! \cdot 4}{(n - 3)! \cdot 16!}. \\]

This is a nice closed form, but it's *a)* tedious to calculate as those factorials really do blow up and *b)* not particularly insightful. Can we do better?


## Pedestrian, but insightful formula

Did you notice above how \\(P(X = 15) = 25\\%\\) is such a nice round number? Maybe it's worth calculating this value in yet another way. So, what does it mean for the game to go over the full length? It means that the very last card has to be a dark one. What's the probability of this happening? Well, 4 out of 16 cards are dark, so there's a 1 in 4 chance of the last card being dark.

Similarly, we can check why \\(P(X = 14) = 20\\%\\). This means the penultimate card will have to be the 4th dark card, i.e., the last card has to be light. In other words,

\\[ P(X = 14) = \frac{12}{16} \cdot \frac{4}{15} = \frac{1}{5} = 20\\%. \\]

Once I started to examine this pattern, a lightbulb went on in my head. We need to flip the deck over! 💡 Now, we're no longer asking where the 4th dark card is in the pile, but rather how many light cards are in a row at the bottom of it. This is pretty straightforward to write down, e.g., for the next probability in line:

\\[ P(X = 13) = \frac{12}{16} \cdot \frac{11}{15} \cdot \frac{4}{14} = \frac{11}{70} \approx 15.7\\%. \\]

And in general:

\\[ P(X = n) = \frac{4}{n+1} \cdot \prod_{k=n-2}^{12} \frac{k}{k+4}. \\]

Again, if you feel bored, you can express this product in terms of the same factorials as above. But the big advantage of this formulation is that it's pretty transparent what's going on.

<!-- TODO: Let's carry out those algebraic steps. -->

So, are we finally done? Not quite, there's still another way of arriving at the same result, which is a bit more elegant and general.


## Negative hypergeometric distribution

When playing with the hypergeometric distribution above, you might've stumbled across an important question we've ignored: is this even a proper distribution, i.e., do all those values sum up to 1? Those \\(p_\text{HG}(N, K, n; k)\\) assume you fix some parameters \\(N\\) (the number of cards), \\(K\\) (the number of dark cards), and \\(n\\) (the number of draws) and then run through all permissible values of \\(k\\) (the number of dark cards drawn). Summing \\(p_\text{HG}(N, K, n; k)\\) over all \\(k\\) for fixed parameters is guaranteed to give 1, but we've instead kept \\(k\\) fixed at 4 (i.e., draw all dark cards) and ranged \\(n\\) over all possible number of draws. Hasn't someone already figured out the details of this distribution?

Of course they have – this is called the [negative hypergeometric distribution](https://en.wikipedia.org/wiki/Negative_hypergeometric_distribution). Whilst the hypergeometric distribution counts the number of successes in a fixed number of draws, the negative hypergeometric distribution counts the number of successes until a fixed number of failures occur. Translated to our problem, it'll count how many light cards are drawn before the 4th dark card is drawn. Again, this is *almost* what we want – the game length will be the number of light cards drawn plus 3 for the first dark cards, which will be auctioned off as well.

The probability mass function of the negative hypergeometric distribution is given by

\\[ p_\text{NHG}(N, K, r; k) = \frac{{k + r - 1 \choose k} {N - r - k \choose K - k}}{N \choose K}, \\]

where \\(N = 16\\) is the total number of cards, \\(K = 12\\) is the number of *light* cards amongst them, \\(r = 4\\) is the number of dark cards (which will end the experiment / game), and \\(k\\) is the number of light cards drawn. Again, let \\(X\\) be the random variable that describes the game length. Then the probability that the game lasts \\(n\\) rounds is

\\[ P(X = n) = p_\text{NHG}(16, 12, 4; n - 3) = \frac{{n - 3 + 4 - 1 \choose n - 3} {16 - 4 - n + 3 \choose 12 - n + 3}}{16 \choose 12} = \frac{{n \choose n - 3}}{16 \choose 12}, \\]

which we can further simplify to

\\[ P(X = n) = \frac{n!}{(n-3)! \cdot 3!} \cdot \frac{12! \cdot 4!}{16!} = \frac{12! \cdot n! \cdot 4}{(n - 3)! \cdot 16!}, \\]

so thankfully, this checks out. 😌

Now, you might think it's quite redundant to derive the same result over and over, but I find it immensely satisfying to obtain the same formula in 3 different ways – and have them verified by simulation. Probability theory can be very tricky and plausible calculations can go wrong in unexpected ways. This article could've just been a single paragraph if we had immediately given away the answer with the negative hypergeometric distribution, but I honestly wouldn't have trusted the results just like that.

<!-- TODO: What's the intuition behind long games? -->

One final question remains: Did Reiner Knizia crunch the numbers when he designed the game? I can't tell for sure, but he does hold a PhD in mathematics, so he would certainly have carefully considered the impact of the game length on the balance and gaming experience. When it comes to the "fun" in games, theory doesn't matter and play testing is king, but calculations like these will provide a shortcut in the design process. Simulations are usually the fastest and most robust way to model a game, but calculations can lead you down really fun rabbit holes – I speak from experience… 🐇
