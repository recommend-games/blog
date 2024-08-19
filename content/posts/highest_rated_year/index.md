---
title: "What was the best year for board games?"
subtitle: The highest rated years on BoardGameGeek
slug: highest-rated-year
author: Markus Shepherd
type: post
date: 2024-08-19T12:00:00+03:00
tags:
  - BoardGameGeek
---

Corey Thompson (of [Above Board TV](https://www.youtube.com/@aboveboardTV) and [Dice Tower Dish](https://dicetowerdish.com/) fame) recently raised a [question](https://boardgamegeek.com/thread/3336646/playtesting-327) on the [Board Games Insider podcast](https://boardgamesinsider.com/): "In what year do you think the best titles (highest rated titles) were released?" He actually answered the question twice, first in episode [#328](https://boardgamegeek.com/blogpost/163710/board-games-insider-328-the-one-about-the-spiel-de) based on an analysis he ran a couple of years ago and then again in [#330](https://boardgamegeek.com/blogpost/164172/board-games-insider-330-the-one-about-the-biggest) with more up-to-date data. I'm not going to spoil his answer here – the podcast in general is worth a listen – so go and find those episodes on your favourite podcast platform. But of course I couldn't help but answer the question myself, in the most needlessly thorough way possible. 🤓

First of all, we need to make sure we understand what the question is asking. I'd say there's two general ways to interpret it: either average the ratings of the games released in a given year, or average all the ratings for all the games of that year. I think the difference between those approaches becomes much clearer with an example: Let's pick the year 1995. There's 224 ranked games from that year; all games (ranked and unranked) received a total of 276,158 ratings as of the time of writing. The former approach would be to average the individual ratings of those 224 games, whilst the latter would mean taking the average of those quarter of a million ratings. The reason why I picked 1995 as an example is of course because that year is dominated by {{% game 13 %}}CATAN{{% /game %}}: This giant amongst hobby games alone accounts for almost half all the ratings from 1995. So when averaging games' ratings, {{% game 13 %}}CATAN{{% /game %}} would have as much weight as some forgotten title with 30 ratings (the minimum required to be ranked). On the other hand, if we take the average over all ratings, we'd have less an average rating of that year and more of an average for {{% game 13 %}}CATAN{{% /game %}}. Neither approach would be right or wrong, they're just different choices, so let's try them both out.

Using the average of games actually presents two different options in its own right because BoardGameGeek (BGG) uses both plain averages for display purposes and Bayesian averages for [rankings]({{<ref "posts/reverse_engineer_bgg/index.md">}}). Let's start from the plain average:

{{< img src="avg_ratings_from_rankings_scatter" alt="TODO" >}}

Every dot is a year between 1970 and 2023, with its height on the *y*-axis indicating the average rating of all games released in that year (higher is better) and the size of the dot indicating the number of games. The acceleration in the past few years is striking, so looking at this plot the answer to Corey's question would definitely have to be: **2023** (and counting).

But we might want to refrain from using those plain averages in this context for the same reason they're not used for ranking: the averages for games with few ratings are just too swingy. So let's look at the Bayesian averages (aka geek scores) instead:

{{< img src="bayes_ratings_from_rankings_scatter" alt="TODO" >}}

There's a couple of interesting observations about this plot. First of, there's a much more uniform linear trend going on, though there's a notable drop in the last two years. That can easily be explained by the way the Bayesian averages are calculated: the dummies ratings that get added to the regular ones weigh much heavier on games with fewer ratings, which naturally is the case for newer games. So this plot tells us that **2019** should be considered the best year.

Is it though? Or is it simply the most recent year with complete data? Shouldn't the best year be the one that defeated the trend? To answer those questions, let's first make the trend explicit:

{{< img src="bayes_ratings_from_rankings_reg" alt="TODO" >}}
