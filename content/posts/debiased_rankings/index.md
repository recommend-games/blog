---
title: Debiasing the BoardGameGeek ranking
# subtitle: "Applying the Gini coefficient to BoardGameGeek ratings"
slug: debiasing-boardgamegeek-ranking
author: Markus Shepherd
type: post
date: 2024-09-05T12:00:00+03:00
tags:
  - BoardGameGeek
  - Debiasing
  - ranking
  - rating
  - alternative rankings
---

*Bias* is a bit of an ugly word, isn't it? It certainly has become one of those battle phrases in the culture war, where both sides of the argument accuse the other of forcing their biases onto society. Board game reviews frequently need to justify themselves for their biases affecting their views. [Dan Thurot](https://spacebiff.com/2024/08/20/talking-about-games-18/) recently wrote a very eloquent piece on the matter, diving deeper into different kinds of biases.

But *bias* also has a well defined [meaning in statistics](https://en.wikipedia.org/wiki/Bias_(statistics)). Moving from emotions to cold hard numbers, the word *bias* loses its antagonistic nature and simply becomes a measurement one might want to minimise or remove entirely. Hence, *debiasing* the BoardGameGeek (BGG) ranking is about asking the question what it would look like if we removed the influence of a particular parameter. One such parameter is a game's age: we've seen in the [previous article]({{<ref "posts/highest_rated_year/index.md">}}) that ratings have gone up over time, so removing the age bias from the BGG ranking means correcting for this trend. (We shall come back later to this and see its effect.)

This is by no means a new idea: [Dinesh Vatvani](https://dvatvani.com/blog/bgg-analysis-part-2) published an often referenced article back in 2018 focussing on removing the complexity bias from the ratings. This article is an update to and an extension of his work.
