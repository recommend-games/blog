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

But *bias* also has a well defined [meaning in statistics](https://en.wikipedia.org/wiki/Bias_(statistics)). Moving from emotions to cold hard numbers, the word *bias* loses its antagonistic nature and simply becomes a measurement one might want to minimise or remove entirely. Hence, *debiasing* the BoardGameGeek (BGG) ranking is about asking the question what it would look like if we removed the influence of a particular parameter. One such parameter is a game's age: we've seen in the [previous article]({{<ref "posts/highest_rated_year/index.md">}}) that ratings have gone up over time, so removing the age bias from the BGG ranking means correcting for this trend.

This is by no means a new idea: [Dinesh Vatvani](https://dvatvani.com/blog/bgg-analysis-part-2) published an often referenced article back in 2018 focussing on removing the complexity bias from the ratings. This article is an update to and an extension of his work.


# Removing the age bias

So, let's start with the bias readers of this blog will already be familar with: age bias, which really is just a slightly more neutral term for *cult of the new*. The first step is plotting the games' ages vs their average ratings:

{{< img src="plot_reg_age" alt="Scatter plot: a game's age vs its rating" >}}

The points on the very left are the oldest games in our dataset, those published in 1970, whilst the ones on the right are those published in 2024. I've plotted games with few ratings more faintly in order to declutter the image. The bold red line is the line of best fit, i.e., the trend line that best describes the yearly increase in average ratings. This picture should look pretty familiar if you've read the previous article, though we didn't aggregate by year but plotted every single game as an individual dot.

That trend line has a slope of 0.03, which means that overall, a game's average rating decrease by 0.03 with every year that has passed since its release. Now, removing the age bias means reducing that slope to 0. It's as if we consider each year on its own and only care how much better or worse a game was compared to its peers released at the same time. I hope this little animation will make things much clearer:

{{< img src="plot_reg_age_animated" alt="Animation: removing the age biased from games' ratings" >}}

(Again, credit to Dinesh Vatvani for introducing this kind of visualisation in his article.)

{{< img src="plot_reg_complexity" alt="Scatter plot: a game's complexity vs its rating" >}}

{{< img src="plot_reg_min_time" alt="Scatter plot: a game's minimum playing time vs its rating" >}}

{{< img src="plot_cat_cooperative" alt="Violin plot: competitive/cooperative games vs their ratings" >}}

{{< img src="plot_cat_game_type" alt="Violin plot: game types vs their ratings" >}}
