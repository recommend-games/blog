---
title: "Child's play: How hard is Orchard?"
slug: orchard
author: Markus Shepherd
type: post
date: 2024-01-23T21:00:00+02:00
tags:
  - Orchard
  - First Orchard
  - Haba
  - Child's play
  - Children's games
  - Win rates
---

{{% game 5770 %}}Orchard{{% /game %}} is a beloved children's game classic which is so old – it's as old as myself. 👴 As one might expect from a children's game, it's really simple: roll a die, pick a fruit of the corresponding color, and put it in the basket. If you roll the raven, the raven moves one step closer to the orchard. If you manage to pick all the fruit before the raven reaches the orchard, you win together. If the raven reaches the orchard first, you lose.

<!-- TODO cover image -->

It's really quite charming and the fruits make great toys. Kids learn to wait for their turns, to recognise colours and maybe even to accept when they lose. But one thing the game does not teach is making smart decisions: on most turns, the die roll completely determines your action. One die face shows a basket which allows you to pick any fruit you want, but you probably already figured out what's the dominant strategy: select the fruit we have the most left of. So really, the game offers no meaningful decisions at all.

<!-- TODO game image -->

What makes for a pretty dull game (by adult standards, of course) actually makes for an excellent playground for simulations! The lack of choices means that the probability of winning is completely determined by die rolls, not skills, and hence can be objectively measured. So if you ever wondered how hard it is to beat the raven in that game from your childhood, you're in for a treat! 🤓

<!-- TODO another image -->

In order to determine the win rate, we can just simulate a series of die rolls and check if their outcome means we win or lose the game. Repeat this process thousands of times and we get a pretty good estimate of the win rate. So without further ado, here's the win rate for Orchard:

It's **68.282%**. You're going to win just over two thirds of your games of {{% game 5770 %}}Orchard{{% /game %}}.

Is this particularly high or low? It's actually a really tough challenge in game design to calibrate the win rate of a co-operative game. If you ask people how often they should win a co-operative game for it to be interesting and challenging, they might say something like 50–50, but in reality people simply don't like losing and would probably be frustrated to play a game where they lose half the time. With that in mind, a game the children will lose 32% of the time seems like a desaster in the making. 😅

A by-product of the simulation is that we can also look at the distribution of game lengths. Here's a histogram of the lengths of games of Orchard:

{{< img src="game_length_original" alt="Histogram over the lengths of games of Orchard" >}}

So the average game last for about 40 rounds, with a standard deviation of about 5.4, i.e., quite a lot of spread. The shortest possible game would be losing after rolling 9 ravens in a row – the probability of that is \\( 6^{-9} \approx 0.00001\\% \\) or 1 in 10 million games. The shortest possible win would mean rolling the basket 20 times in a row (basket rolls allow you to pick two fruits at once) – which happens in 1 in 3,656,158,440,062,976 games. In theory, the game could go on forever if you keep rolling fruits you've already emptied, but honestly, already 40 die rolls without any decisions feels long enough for my taste – in particular when you have to watch a toddler at the same time. 👶

{{< img src="game_length_first" alt="Histogram over the lengths of games of First Orchard" >}}

TODO

{{< img src="win_rates_first" alt="Win rates for First Orchard with different lengths of the raven path" >}}
