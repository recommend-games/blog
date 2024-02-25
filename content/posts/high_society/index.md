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
