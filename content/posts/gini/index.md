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


## Historical perspective

To answer that question, we can look at how the Gini coefficient has changed over time. Here's how it has evolved since late 2016:

{{< img src="gini_coefficient_over_time" alt="The Gini coefficient of BoardGameGeek ratings over time" >}}

So, we started out this period with a little over 0.8 and have been steadily creeping up to over 0.835 today. This increase of inequality on a very high level is an interesting observation – and somewhat worrying. For comparison: The most unequal country in the world is considered to be South Africa 🇿🇦, with a Gini coefficient of 0.62. The US 🇺🇸 has a Gini coefficient of 0.39, Finland 🇫🇮 0.27 and Slowakia 🇸🇰 0.21, the lowest value in the world.

Obviously, those values don't compare directly, but they serve as a reminder of just how unequal the baseline in 2016 was, and the situation has intensified since then. So, why is that?

Maybe it's worth pausing for a moment to consider if this inequality is actually bad – or if it could even be a good thing. One should remember that the easiest way (arguably the only one) to achieve perfect equality is by assigning everyone the exact same value: zero. Put another way: while the *share* of attention captured by the top games of the hobby has increased, this doesn't necessarily mean this attention has been taken away from the rest of the games.️ Overall, interest in modern games has been growing, so even the long tail of games should receive more attention overall when measured in absolute terms. A rising tide lifts all boats, at least that's what those on the steering wheels tell those toiling in the engine rooms. 🚢


### Outline

- Conclusion:
    - Where could this increased inequality come from?
    - What does this mean for the board game industry?
    - What does this mean for the board game community?
    - PS: mention inspiration for this article
    - Note about the overall number of ratings, which – as you recall – is pegged to the number of dummy ratings for the geek score
