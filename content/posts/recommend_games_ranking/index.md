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

Instead, I wanted to create a new ranking which I can at least explain. So here goes:

**The basic idea is to calculate the recommended games for all users, and then average those rankings. Those averages would become the Recommend.Games rankings.**

That sounds simple and intuitive, but, as the saying goes, the devil is in the details. For starters, there are over 100,000 games in the BoardGameGeek database, and [over 400,000 users](https://twitter.com/recommend_games/status/1498184269402980355) with at least one rated game. Calculating *all recommendations* for *all users* would therefore mean over 40 billion user–game pairs. That's a lot. 😅 But really, we don't care if a game is the 1,000th, 10,000th or 100,000th highest rated game. Instead, we only recommend the top 100 games for each user. The highest game on that list receives 100 points, the next 99, and so on, until the 100th game receives a single point from that user. All other games will be awarded 0 points. The we can simply average those points across all users, and voilà, those scores become the R.G rankings. 🤩

… Except that's still not the whole story. I wasn't happy about the idea of a user who 15 years ago left a single rating being equally important as someone who played and rated hundreds of board games over two decades of BGG history. That's why I tried to model the "trust" we should put in different users' ratings. The idea here would be that we should trust a user's rating more if two things are true:

* They are a regular contributor to BGG, i.e., rate, log plays etc at least once a month over a long period of time.
* They should rate games with a reasonable distribution, i.e., on a nice bell curve.

For the first point we count each calendar month that the user was active on BGG (e.g., rated a game, logged a play, updated their collection). Then we take the logarithm (base 2) of that number – this means the score will rise quite rapidly in the first year of BGG activity, but then flatten out quite quickly. The goal is not to treat newcomers too harshly. Note that \\(\log_2 1 = 0\\), so new users with only one month of activity will start with zero trust and consequently not be considered in the rankings calculations.

The second point is a little trickier. Mathematically speaking, we want to assess how closely a user's ratings follow a normal distribution. There are a couple of neat statistical tests that do that, the one that's considered best is the [Shapiro–Wilk test](https://en.wikipedia.org/wiki/Shapiro%E2%80%93Wilk_test). What we care about is a number between 0 and 1 that somehow measures how much a user's rating distribution resembles a bell. Take, for instance, Tom Vasel's ratings. He clearly users a nice spread for his ratings:

{{< img src="tomvasel" size="x300" alt="Tom Vasel's ratings" >}}

If on the other hand a user only ever rates games with a 10, never any other score, their factor would be 0, and again, they wouldn't take part in the R.G rankings calculations.

So, long story short, we have those two factors that are supposed to describe how much we can trust a user's ratings. We can now multiply them with each other, and the higher the score, the higher will be our trust in their ratings, and consequently, the more weight their "vote" will have when calculating the R.G ranking. But before we got there, what users *do* we trust the most? Many of the highest scores actually belong to pretty random users, so I'm not comfortable exposing them here, but it's interesting to compare some of the "celebrities" in the hobby (and yours truly):

|    bgg_user_name    |       trust        |  rank  |
|:-------------------:|-------------------:|-------:|
|    w eric martin    | 7.3757623059412065 |   21   |
|      engelstein     | 7.227097020759851  |   77   |
|       tomvasel      | 7.009196280501789  |  311   |
|        aldie        | 6.544203898142164  |  1885  |
|    jameystegmaier   | 6.343327925731987  |  3211  |
|      jonpurkis      | 6.295583835577709  |  3628  |
|      bohnanzar      | 5.8475915773208955 |  8798  |
|   markus shepherd   | 5.452849953473498  | 16181  |
|        quinns       |  5.42065509053484  | 16925  |
|     matthiasmai     | 4.489247857378577  | 46287  |
|     phelddagrif     | 3.981026376056779  | 67790  |
|     cephalofair     | 3.833117202933614  | 74801  |
|       elizharg      | 3.155649456087472  | 107995 |

[^stochastic]: In case you're curious: The reason why the recommendations are so swingy is because they aren't precisely calculated, but merely approximated by an algorithm called [stochastic gradient descent](https://recommend.games/#/faq#the-1-game-keeps-changing-cant-you-make-up-your-mind), which is inherently non-deterministic.
[^smoothed]: And this is even a smoothed version of the rankings: It uses the average score of one week to determine the ranking in that plot.

<!--
from board_game_recommender.trust import user_trust
trust = user_trust(ratings='../board-game-data/scraped/bgg_RatingItem.jl', min_ratings=10)
trust = trust.sort('trust', ascending=False)
trust['rank'] = range(len(trust))
trust['rank'] += 1
trust.print_rows(1000)
trust[s.is_in(['w eric martin', 'tomvasel', 'jonpurkis', 'quinns', 'markus shepherd', 'bohnanzar', 'aldie', 'bruno des montagnes', 'cephalofair', 'donaldx', 'elizharg', 'engelstein', 'eric lang', 'faidutti', 'frog1', 'jameystegmaier', 'matthiasmai', 'mleacock', 'nopunincluded', 'phelddagrif', 'robdaviau', 'toinito', 'vlaada'])].print_rows(100)
 -->
