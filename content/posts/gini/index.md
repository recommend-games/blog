---
title: "Has board game rating inequality increased over the years?"
subtitle: "Applying the Gini coefficient to BoardGameGeek ratings"
slug: rating-inequality-gini-coefficient
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

1. {{% game 13 %}}CATAN{{% /game %}}: 126,448 ratings
2. {{% game 822 %}}Carcassonne{{% /game %}}: 125,850 ratings
3. {{% game 30549 %}}Pandemic{{% /game %}}: 124,584 ratings

So, obviously the attention of the board game world is concentrated on *very* few games. The 26,168 ranked games share a total of 24,353,222 ratings[^dummy-votes] between them. The top 1%, the 262 games with the most ratings, account for 35.5% of those ratings. Conversely, the bottom 23.2%, the 6,071 games with the fewest ratings, account for only 1% of the ratings.

Can we somehow quantify this inequality more precisely? Why, I'm glad you asked! 🧐


## The Gini coefficient

Enter the [Gini coefficient](https://en.wikipedia.org/wiki/Gini_coefficient). This measure is commonly used to quantify income inequality, but it can be applied to any distribution of values. In our case, we can use it to measure the inequality in the distribution of ratings on BGG.

For this, we dive deeper into the question: What share of all ratings do the top X% of games have? This is the cumulative distribution of ratings, and it looks like this:

{{< img src="gini_coefficient" alt="The share of the total ratings and the Gini coefficient of BoardGameGeek ratings" >}}

The thin 45° line is the (hypothetical) perfectly equal distribution, where every game has exactly the same number of ratings; the thick curve is the actual cumulative distribution of ratings. The area between the two lines is (essentially[^gini-coefficient]) the Gini coefficient, which – as you can see – is **0.836** in our case. A perfectly equal distribution of ratings (every game has the same number of ratings) would have a Gini coefficient of 0, while a perfectly unequal distribution (one game would have *all* the ratings, whilst all others have none) would have a Gini coefficient of 1. So 0.836 is really high, meaning a *very* unequal distribution of ratings. This shouldn't come as a surprise to anyone following the glut of new games coming out every year, with only a few of them getting the lion's share of attention, whilst most of the rest languish in obscurity. Has this phenomenon changed over the years though? 🤔


## Historical perspective

To answer that question, we can look at how the Gini coefficient has changed over time. Here's how it has evolved since late 2016:

{{< img src="gini_coefficient_over_time" alt="The Gini coefficient of BoardGameGeek ratings over time" >}}

So, we started out this period with a little over 0.8 and have been steadily creeping up to over 0.835 today. This increase of inequality on a very high level is an interesting observation – and somewhat worrying. For comparison: The most unequal country in the world is considered to be South Africa 🇿🇦, with a Gini coefficient of 0.63. The US 🇺🇸 has a Gini coefficient of 0.40, Finland 🇫🇮 0.27 and Slowakia 🇸🇰 0.23, the lowest value in the world.[^wikipedia]

Obviously, those values don't compare directly, but they serve as a reminder of just how unequal the baseline in 2016 was, and the situation has intensified since then. So, why is that? One obvious factor is the number of new games being released each year. Let's take a look at this plot:

{{< img src="games_per_year" alt="The number of games released each year between 1990 and 2022" >}}

So, there's a lot to unpack here. Start from the bars in the background: they count the number of games released each year from 1990 to 2022. Just look at the explosive growth from 2013 through 2019 in particular – that's probably the influence of crowdfunding. The abrupt drop in 2020 is, of course, due to COVID–19. Interestingly, the number of releases haven't picked up since and 2019 remains the record year.

The dots are the Gini coefficient just for that cohort, i.e., those dots measure how unequal the ratings are distributed among the games released in that year. The higher up a dot is, the more a year is dominated by a few games – or just a single one. {{% game 13 %}}CATAN{{% /game %}}, the most rated game on BGG (see above), single-handedly makes the 1995 cohort the most unequal year in the dataset. The sizes of the dots represent the most popular game of that year, so 1995, 2000 and 2008 get the biggest dots. Unsurprisingly, games with an uber-popular game (big dot) tend to have a higher Gini coefficient (high up on the y-axis).

But there something else going on: whilst the number of releases have been skyrocketing since 2013, the Gini coefficients of the years since 2016 have been falling noticibly, indicating less concentration of the ratings on just a few games. Games released in 2022 form the first cohort with a Gini coefficient below 0.75 since the 90s.

So how come that rating inequality is still rising? This might have to do with publishers' increased focus on evergreens – flagship titles and lines that have proven to be consistently popular. Most publishers will rather release new expansions for and versions of a successful game than take a risk on a new one. So while new releases get slightly more evenly distributed attention, much of the overall attention (and marketing budget) is still drawn to select few games. Publishers and designers certainly complain that it's increasingly harder for new games to get noticed and even get a second printrun, and the data seems to support those complaints.

Maybe it's worth pausing for a moment to consider if this inequality is actually bad – or if it could even be a good thing. One should remember that the easiest way (arguably the only one) to achieve perfect equality is by assigning everyone the exact same value: zero. Put another way: while the *share* of attention captured by the top games of the hobby has increased, this doesn't necessarily mean this attention has been taken away from the rest of the games.️ Overall, interest in modern games has been growing, so even the long tail of games should receive more attention overall when measured in absolute terms. A rising tide lifts all boats, at least that's what those on the steering wheels tell those toiling in the engine rooms. 🚢

You might deduce that I don't fully buy into this narrative. The continuing increase of the Gini coefficient, the focus on blockbuster title, the ongoing consolidation of the hobby board game publishers (although Asmodee has noticably slowed down as their parent company did some [stupid capitalist things](https://www.dicebreaker.com/companies/asmodee/news/asmodee-embracer-earnings-2023-saudi-arabia-deal)) – all of these are signs of a Marvelisation of the board game industry. ️Have we reached the end of this industry being run by boutique publishers? Will it all be nature kitsch, anthropomorphic animals or billion dollar licenses from here on out? I have no doubt that quirky and sometimes downright weird games will continue to be made, some of which will tackle difficult topics or push the boundaries of what a game can be. But I'm afraid those will be more and more pushed to the fringes of the hobby, while the mainstream will be dominated by the same old, same old.


### Outline

- How many games are released each year? Does the increase correlate to the increase in the Gini coefficient?
- Do we see the same phenomenon if we look at different slices of data? E.g., by year.
- Conclusion:
    - Where could this increased inequality come from?
    - What does this mean for the board game industry?
    - What does this mean for the board game community?
    - PS: mention inspiration for this article


[^dummy-votes]: Remember that the number dummy ratings added to [calculate the geek score]({{<ref "posts/reverse_engineer_bgg/index.md">}}), which is used for the BGG rankings, is pegged to the total number of ratings. Since there's one dummy rating for every 10,000 ratings, the current number of dummy ratings is somewhere around 2435. When we [last checked in]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}) around three years ago, that number was around 1729 dummies. Quite the growth indeed.
[^gini-coefficient]: The Gini coefficient is actually twice the area between the two lines. The line of equality cuts the unit square in half, so the area of perfect inequality would be 0.5. For the coefficient to be between 0 and 1, we double that area to get the final value.
[^wikipedia]: [List of countries by income equality](https://en.wikipedia.org/wiki/List_of_countries_by_income_equality)
