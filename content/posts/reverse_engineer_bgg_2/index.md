---
title: Reverse engineering the BoardGameGeek ranking – Part 2!
slug: reverse-engineering-boardgamegeek-ranking-part-2
author: Markus Shepherd
type: post
date: 2021-01-26T22:24:00+02:00
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
  - circle of hype
---

*This is the second part of a series explaining and analysing the BoardGameGeek rankings. Read the [first part here]({{<ref "posts/reverse_engineer_bgg/index.md">}}).*

[Last time]({{<ref "posts/reverse_engineer_bgg/index.md">}}) I left you with the nice result that [BoardGameGeek (BGG)](https://boardgamegeek.com/) calculates its ranking by taking users' ratings for a particular game and then add around **1500-1600 dummy ratings of 5.5**. This so-called *geek score* is used to sort the games from best ({{% game 174430 %}}Gloomhaven{{% /game %}}) to worst ({{% game 11901 %}}Tic-Tac-Toe{{% /game %}}).

One detail however we touched on in passing, but did not resolve, is how that number of dummy ratings develop over time. When the current calculation method was introduced, BGG founder [Scott Alden mentioned](https://www.boardgamegeek.com/thread/103639/new-game-ranking-system) that this number would be pegged to the number of total ratings, but did not reveal any details. Challenge accepted!

In order to tackle this question, we need to compare that dummy number to the total number of ratings over time. Fortunately, thanks to the scraping done for [Recommend.Games](https://recommend.games/), we have access to the [BGG games data](https://boardgamegeek.com/thread/2287371/boardgamegeek-games-and-ratings-datasets) over the past year or so. Using these snapshots, we observe how the number of games and ratings in the database has grown:

{{< img src="games" alt="Number of games and ratings on BGG over time" >}}

We can now repeat the exact same calculation we did in the [previous post]({{<ref "posts/reverse_engineer_bgg/index.md#optimisation">}}): For each point in time, the algorithm searches for the number of dummy ratings that yields an estimated geek score closest to the actual score. Now, we have a bunch of data points that correlate the total number of ratings with the number of dummies used at that time. Here's what it looks like:

{{< img src="ratings" alt="Number of total ratings vs dummy ratings" >}}

We get a pretty nice straight line – the dashed line in the plot is fitted with linear regression, i.e., the straight line that most closely fits our data. Its formula is:

\\[ \\textrm{number of dummies} \approx 0.0000997 \cdot \\textrm{total number of ratings}. \\]

This means that for every rating entered into the BGG database, the number of dummy ratings is increased by \\(0.0000997\\). That number might look a bit opaque, but it's actually very easy to interpret once you put the question to its head: How many ratings have to be entered for the number of dummies to increase by \\(1\\)? You get the answer to that by taking the inverse of that factor, which happens to be about \\(10\\,032\\). This number is way to close to \\(10\\,000\\) to be a coincidence! We can conclude the exact formula for the number of dummy ratings:

\\[ \\textrm{number of dummies} = \\frac{\\textrm{total number of ratings}}{10\\,000}. \\]

As of the time of writing, there are \\(17\\,287\\,904\\) ratings (give or take) in the BGG database, so there will be around 1729 dummy ratings of \\(5.5\\) added to the regular ratings.

As the number of BGG users [rises steadily](https://boardgamegeek.com/thread/2585742/happy-21st-birthday-geek), this number of dummy ratings also keeps increasing. This is part of the reason why older games (particularly those with a newer edition) tend to drop in the rankings. When users stop adding new ratings, a game's average rating more or less freezes. But because more and more dummy votes are added, the geek score decreases every time it gets recalculated, and so the older games drop in the rankings, while the latest hotness gets all the fresh votes, and shoots up to the top.

The circle of hype.
