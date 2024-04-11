---
title: "Has board game rating inequality increased over the years?"
subtitle: "Applying the Gini coefficient to BoardGameGeek ratings"
# slug: gini
author: Markus Shepherd
type: post
date: 2024-04-11T20:00:00+03:00
tags:
  - BoardGameGeek
  - Ratings
  - Gini coefficient
  - Inequality
---


## The number of ratings per game

Perhaps one of the more controversial choices of the [Shut Up & Sit Down Effect]({{<ref "posts/susd_effect/index.md">}}) article was using the number of ratings on BoardGameGeek (BGG) as proxy for "attention" to a game. So let's double down on that! 😈

If lots of ratings mean a lots of eyes on a game, we can ask questions like: What games get all the attention? Do few games steal the spotlight? Or is the attention spread out evenly?

The answer is pretty clear if we sort the games by their number of ratings and plot them from fewest to most:

{{< img src="num_ratings" alt="The distribution of the number of ratings on BoardGameGeek, from fewest to most ratings per game" >}}

Note that in this plot and everything that follows, I only include ranked games, i.e., games with at least 30 ratings. This is partially for convenience (we have excellent [historical ranking data](https://github.com/beefsack/bgg-ranking-historicals) going back to 2016), but also because the BGG database is full of obscure games with very limited distribution and audience.

With that out of the way, what do we see in the plot? It's clear that the vast majority of games have very few ratings, while a handful of games have a ton of ratings. This is a classic example of a [long-tailed distribution](https://en.wikipedia.org/wiki/Long_tail), where most of the data is concentrated in the "tail" of the distribution.

Fun fact: there are three absolute classic games that have been competing for the distinction of most-rated game on BGG for years now. As of the time of writing, the current standings are:

1. {{% game 13 %}}CATAN{{% /game %}}: 126,425 ratings
2. {{% game 822 %}}Carcassonne{{% /game %}}: 125,831 ratings
3. {{% game 30549 %}}Pandemic{{% /game %}}: 124,575 ratings

It is clear that the attention of the board game world is concentrated on *very* few games. Can we quantify this inequality in attention? Why, I'm glad you asked! 🧐


## The Gini coefficient

Enter the [Gini coefficient](https://en.wikipedia.org/wiki/Gini_coefficient). This measure is commonly used to quantify income inequality, but it can be applied to any distribution of values. In our case, we can use it to measure the inequality in the distribution of ratings on BGG.

For this, we change the point of view slightly. Instead of looking at the absolute number of ratings, we ask the question: What share of all ratings do the top X% of games have? This is the cumulative distribution of ratings, and it looks like this:

{{< img src="gini_coefficient" alt="The share of the total ratings and the Gini coefficient of BoardGameGeek ratings" >}}

The thin 45° line is the (hypothetical) perfectly equal distribution, where every game has exactly the same number of ratings; the thick curve is the actual cumulative distribution of ratings. The area between the two lines is (essentially) the Gini coefficient, which – as you can see – is **0.836** in our case. A perfectly equal distribution of ratings (every game has the same number of ratings) would have a Gini coefficient of 0, while a perfectly unequal distribution (one game would have *all* the ratings, whilst all others have none) would have a Gini coefficient of 1. So 0.836 is really high, meaning a *very* unequal distribution of ratings. This shouldn't come as a surprise to anyone following the glut of new games coming out every year, with only a few of them getting the lion's share of attention, whilst most of the rest languish in obscurity. Has this phenomenon changed over the years though? 🤔


### Outline

- Introduction:
    - Link back to SU&SD article: using number of ratings as proxy for attention (note about the actual data?)
    - How are the number of ratings distributed?
    - Plot of the distribution (not cumulative)
- Gini coefficient:
    - Change PoV to cumulative distribution, i.e., share of all ratings / "attention"
    - Compare perfect equality and perfect inequality
    - Define Gini coefficient
    - What's the value today?
    - Compare to Gini coefficient in actual income inequality?
- Historical perspective:
    - How has the Gini coefficient changed over the years?
    - Plot of the Gini coefficient over time
- Conclusion:
    - Where could this increased inequality come from?
    - What does this mean for the board game industry?
    - What does this mean for the board game community?
    - PS: mention inspiration for this article


### Plots

{{< img src="gini_coefficient_over_time" alt="The Gini coefficient of BoardGameGeek ratings over time" >}}
