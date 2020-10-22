---
title: Reverse engineering the BoardGameGeek ranking – Part 2!
slug: reverse-engineering-boardgamegeek-ranking-part-2
author: Markus Shepherd
type: post
date: 2020-10-20T00:00:00+03:00
tags:
  - BoardGameGeek
  - BGG
  - ranking
  - rating
  - statistics
  - Bayesian
  - geek score
  - top 100
  - dummy ratings
  - highest rated games
  - alternative rankings
---

*This is the second part of a series explaining and analysing the BoardGameGeek rankings. Read the [first part here]({{<ref "posts/reverse_engineer_bgg/index.md">}}).*

[Last time]({{<ref "posts/reverse_engineer_bgg/index.md">}}) I left you with the nice result that [BoardGameGeek (BGG)](https://boardgamegeek.com/) calculates its ranking by taking users' ratings for a particular game and then add around **1500-1600 dummy ratings of 5.5**. This so-called *geek score* is used to sort the games from best ({{% game 174430 %}}Gloomhaven{{% /game %}}) to worst ({{% game 11901 %}}Tic-Tac-Toe{{% /game %}}).

One detail however we touched on in passing, but did not resolve, is how that number of dummy ratings develop over time. When the current calculation method was introduced, BGG founder [Scott Alden mentioned](https://www.boardgamegeek.com/thread/103639/new-game-ranking-system) that this number would be pegged to the number of total ratings, but did not reveal any details. Challenge accepted!

{{< img src="games" alt="Number of games and ratings on BGG over time" >}}

{{< img src="ratings" alt="Number of total ratings vs dummy ratings" >}}
