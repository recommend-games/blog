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

In order to determine the win rate, we can just simulate a series of die rolls and check if their outcome means we win or lose the game. Repeat this process thousands of time and we get a pretty good estimate of the win rate.

{{< img src="game_length_original" alt="Histogram over the lengths of games of Orchard" >}}

TODO

{{< img src="game_length_first" alt="Histogram over the lengths of games of First Orchard" >}}

TODO

{{< img src="win_rates_first" alt="Win rates for First Orchard with different lengths of the raven path" >}}
