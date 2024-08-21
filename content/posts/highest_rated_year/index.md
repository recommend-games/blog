---
title: "What was the best year for board games?"
subtitle: The highest rated years on BoardGameGeek
slug: highest-rated-year
author: Markus Shepherd
type: post
date: 2024-08-19T12:00:00+03:00
tags:
  - BoardGameGeek
  - Ratings
  - highest rated games
  - Corey Thompson
  - Board Games Insider
---

Corey Thompson (of [Above Board TV](https://www.youtube.com/@aboveboardTV) and [Dice Tower Dish](https://dicetowerdish.com/) fame) recently raised an interesting [question](https://boardgamegeek.com/thread/3336646/playtesting-327) on the [Board Games Insider podcast](https://boardgamesinsider.com/):

> In what year do you think the best titles (highest rated titles) were released?

He actually answered the question twice, first in episode [#328](https://boardgamegeek.com/blogpost/163710/board-games-insider-328-the-one-about-the-spiel-de) based on an analysis he ran a couple of years ago and then again in [#330](https://boardgamegeek.com/blogpost/164172/board-games-insider-330-the-one-about-the-biggest) with more up-to-date data. I'm not going to spoil his answer here – the podcast in general is worth a listen – so go and find those episodes on your favourite podcast platform. But of course I couldn't help but answer the question myself, in the most needlessly thorough way possible. 🤓


# Boring technicalities

First of all, we need to make sure we understand what the question is asking. I'd say there's two general ways to interpret it: either average the ratings of the games released in a given year, or average all the ratings for all the games of that year. I think the difference between those approaches becomes much clearer with an example: Let's pick the year 1995. There's 224 ranked games from that year; all games (ranked and unranked) received a total of 276,158 ratings as of the time of writing. The former approach would be to average the individual ratings of those 224 games, whilst the latter would mean taking the average of those quarter of a million ratings. The reason why I picked 1995 as an example is of course because that year is dominated by {{% game 13 %}}CATAN{{% /game %}}: This giant amongst hobby games alone accounts for almost half all the ratings from 1995. So when averaging games' ratings, {{% game 13 %}}CATAN{{% /game %}} would have as much weight as some forgotten title with 30 ratings (the minimum required to be ranked). On the other hand, if we take the average over all ratings, we'd have less an average rating of that year and more of an average for {{% game 13 %}}CATAN{{% /game %}}. Neither approach would be right or wrong, they're just different choices, so let's try them both out.


# Data from rankings

## Average ratings

Using the average of games actually presents two different options in its own right because BoardGameGeek (BGG) uses both plain averages for display purposes and Bayesian averages for [rankings]({{<ref "posts/reverse_engineer_bgg/index.md">}}). Let's start from the plain average:

{{< img src="avg_ratings_from_rankings_scatter" alt="Yearly average ratings from ranked games" >}}

Every dot is a year between 1970 and 2023, with its height on the *y*-axis indicating the average rating of all games released in that year (higher is better) and the size of the dot indicating the number of games. The acceleration in the past few years is striking, so looking at this plot the answer to Corey's question would definitely have to be: **2023** (and counting).


## Geek scores

But we might want to refrain from using those plain averages in this context for the same reason they're not used for ranking: the averages for games with few ratings are just too swingy. So let's look at the Bayesian averages (aka geek scores) instead:

{{< img src="bayes_ratings_from_rankings_scatter" alt="Yearly average geek score from ranked games" >}}

There's a couple of interesting observations about this plot. First of, there's a much more uniform linear trend going on, though there's a notable drop in the last two years. That can easily be explained by the way the Bayesian averages are calculated: the dummies ratings that get added to the regular ones weigh much heavier on games with fewer ratings, which naturally is the case for newer games. So this plot tells us that **2019** should be considered the best year.


## Linear regression

Is it though? Or is it simply the most recent year with complete data? Shouldn't the best year be the one that defeated the trend? To answer those questions, let's first make the trend explicit:

{{< img src="bayes_ratings_from_rankings_reg" alt="Yearly average geek score from ranked games (including trend line)" >}}

I've added the "line of best fit", i.e., the one that follows the trend most closely, via standard linear regression. The shaded band indicates the 95% confidence interval, i.e., we can be 95% confident that the true trend line lies within that band.

Very simply put, the trends tells us that the average game from 1970 has a geek score of around 5.516. This makes sense, since it is strongly pulled towards the value 5.5 of the dummy ratings added to calculate this Bayesian average. According to the trend, that geek score then increases year on year by about 0.004. This might not sound like much, but 53 years later, in 2023, the average game should have a geek score of 5.722. In increase of over 0.2 is huge for a score that is so strongly drawn to its mean.

Of course, I was now talking of the hypothetical scores if they were indeed lining up perfectly on that trend line. The reality is slightly more messy, and we can now calculate the difference between the actual average values for a year and the trend line. Years that beat the expecation from the trend lie above that line, underperforming years under the line. So now we can find the year that is the best in relation to the trend of its time, which is … 🥁 … **1977**. This might not be the most obvious year at first glance, but when looking more closely, it did bring forth iconic titles such as {{% game 1035 %}}Squad Leader{{% /game %}}, {{% game 15 %}}Cosmic Encounter{{% /game %}} and {{% game 811 %}}Rummikub{{% /game %}}. In light of those games, I'd say it's a well earned title.

Now, one can also look at the underperforming years. Generally, it appears that the 70s are still held in high regards, whilst from the mid 80s to the mid 00s most years are underperforming, with the worst year being **1996**. This makes 1995 with {{% game 13 %}}CATAN{{% /game %}}, as well as {{% game 93 %}}El Grande{{% /game %}} and {{% game 220 %}}High Society{{% /game %}}, stand out even more.


# Data from ratings

I've promised a different way to calculate the average ratings for each year, so now we look at all the individual ratings for all the games released in that year and average those. Here's the result plot:

{{< img src="avg_ratings_from_ratings_scatter" alt="Yearly average ratings" >}}

We see a similar increasing trend, but one that does continue to the present, so again, we'd have to say that the best year for games is **2023**. Another interesting observation is that the slope is much steeper. Let's make this concrete:

{{< img src="avg_ratings_from_ratings_reg" alt="Yearly average ratings (including trend line)" >}}

Again, the trend tells us that the average rating for 1970 is 5.926, but here the yearly increase is almost 0.03, an order of magnitude higher than when we looked at the geek scores, so we end up with a trend of 7.471 for 2023.

So, what years are the biggest winners and losers compared to the trend? The biggest overperformer, by quite a margin, is **1980** according to this measure. It got classics such as {{% game 71 %}}Civilization{{% /game %}} and {{% game 41 %}}Can't Stop{{% /game %}} going for itself, which hit really hard in this metric since there's so few ratings for those old games, as you can tell by those vanishingly small dots. Other strong positive outliers are 1982 (with {{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} and {{% game 2653 %}}Survive: Escape from Atlantis!{{% /game %}}), as well as the aforementioned 1995 and 1977.

The most disappointing year in this category is **2001**, which is curiously nested between the strong 2000 ({{% game 822 %}}Carcassonne{{% /game %}}) and 2002 ({{% game 3076 %}}Puerto Rico{{% /game %}}).


## Testing for significance

I promised excrutiating details, didn't I? So I've gotta answer one more question: Are those outliers significant, or are they just randomly spread around the trend line? Statistical testing is a vast field – so vast in fact that I always feel completely lost whenever I enter it.

So let's not make things overly complicated. In their most basic form, most of those tests boil down to checking if values we're looking at don't stray too far from the mean. In our case, we look at the distances between actual values and the trend line and check how they are distributed. Those values that lie more than two standard deviations from the mean could be considered significant outliers.

If you're not interested in any of those statistical details, you can just call your favourite software package to calculate the *p*-value, which – roughly speaking – tells you the probability that the effect you observed is due to random chance. The smaller the *p*-value, the more likely you've observed the actual effect you were interested in. Usually, an arbitrary threshold is chosen, often 5%. Observations with a *p*-value below that threshold are considered significant.

In our case, we have two years significantly outperforming the trend (1980 and 1982) and two significantly underperforming (1996 and 2001). So, I guess we can conclude by calling those years the confirmed best and worst years, respectively.

Except, it's not that simple. (I wasn't lying when I said I'd be going into unnecessary depths. 🤓) One possible interpretation of that 5% threshold is that you'll get positive results just by random chance in 1 in 20 experiments. But when we just calculated *p*-values for 53 years, we effectively performed 53 experiments, so a couple of years sticking out randomly would actually be expected. Again, there's a vast body of research to deal with those multiple tests. For good measure, I've checked the outcome for the procedures according to Bonferroni, Holm and Benjamini–Hochberg, but the result is the same for all of them: None of the years differ significantly from the trend. So I guess I've just wrote over 1500 words just to conclude that the best years in board gaming are yet to come. There's some comfort in that.


# Golden age or cult of the new?

Let me finish with a more philosophical thought: We've collected a lot of evidence to confidently conclude that the average ratings have been increasing over the years and continue to do so, but what is the reason for this? Is it because we are, as many people claim, in a "golden age of board gaming"? Or is it a by-product of the "cult of the new" which willingly drops hundreds of dollars on games that don't even exist yet, but which receive perfect ratings from their backers as if to reassure themselves that this was a sound investment?

I don't think there's a definitive answer. [Grade inflation](https://en.wikipedia.org/wiki/Grade_inflation) is a real thing, and if it affects professional teachers who (hopefully) put a lot of thought and attention into the way they rate students, I'd say it's safe to assume the same will be true for some random people judging games on a website.

But it's also true that designer games are still a very young art form and their creators have made a tremendous amount of progress in their craft over the past decades. In that respect, it's understandable that gamers want to express their appreciation for those advances. Let's just hope we won't run out of rating space before this century is over: At the current pace, every game will be a perfect 10 by the year 2110.

*You can find the full results from the ranking data [here](years_from_rankings.csv) and the test results [here](years_from_rankings_stats.csv), results from the rating data [here](years_from_ratings.csv) and corresponding test results [here](years_from_ratings_stats.csv). As always, you can find the full analysis code and notebooks on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/highest_rated_year).*
