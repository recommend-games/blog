---
title: Recommend.Games ranking explained
slug: recommend-games-ranking
author: Markus Shepherd
type: post
date: 2022-02-22T22:02:22+02:00
tags:
  - news
  - ranking
  - highest rated games
  - alternative rankings
---

We have some pretty exciting news! 🤩 Since 2022-02-22, we've been using a new and improved ranking as the default sorting for our front page at [Recommend.Games](https://recommend.games/).

… What do you mean, you haven't noticed there's a R.G ranking? You know, that thing that's referenced in the [statistics](https://recommend.games/#/stats)? … You haven't ever opened that view?!? 😱

OK, let's back up for a second. R.G's primary purpose is a recommendation engine, that is, finding personalised game recommendations based on a user's preferences (in this case as expressed through their [BoardGameGeek](https://boardgamegeek.com/) ratings). But we want to show some games to the users immediately when they load the start page, before entering their user name. Think of these games as recommendations for… anyone. What games would you recommend to a person if you didn't know anything about their taste? This is the implicit purpose of any "Top X entities" list. Since this is a recommendation site, we'd like to make this claim explicit, so the R.G ranking has always been those "recommendations for everyone". What's changed is the way those recommendations are calculated.

Recommendations are based on a technique known as collaborative filtering. Basically, the algorithm tries to learn the users' preferences based on their ratings, find users with similar tastes, and then recommend new games that user might like. R.G uses Apple's implementation [Turi Create](https://github.com/apple/turicreate) for its recommendations, which does a lot of magic 🪄 under the hood. One of those magic tricks is that it offers recommendations for users it doesn't know anything about. The algorithm treats those users as new and offers some default recommendations that should be a good starting point for anybody, without any particular context. It's exactly those recommendations that R.G has been using for years as our ranking and default sorting.

So, why change this and create a new ranking? There's a number of problems with the old ranking. For one, it's really swingy.[^stochastic] Seriously, just take a look at the [history](https://recommend.games/#/history/fac):[^smoothed]

[{{< img src="history_crop" size="x300" alt="Ancient history" >}}](history_full.png)

Maybe more importantly, the exact algorithm to determine those recommendations for new users is extremely obscure. There's been a [long-standing ticket](https://gitlab.com/recommend.games/board-game-recommender/-/issues/38) to find out what's going on. The answer isn't documented anywhere, but you can find it somewhere in [these lines of code](https://github.com/apple/turicreate/blob/30eced4508bf86c4c59a1fef96bd0b23363db283/src/toolkits/recsys/models/itemcf.cpp#L194). Let me know if you can make sense of them, I've simply given up at some point.

[^stochastic]: In case you're curious: The reason why the recommendations are so swingy is because they aren't precisely calculated, but merely approximated by an algorithm called [stochastic gradient descent](https://recommend.games/#/faq#the-1-game-keeps-changing-cant-you-make-up-your-mind), which is inherently non-deterministic.
[^smoothed]: And this is even a smoothed version of the rankings: It uses the average score of one week to determine the ranking in that plot.
