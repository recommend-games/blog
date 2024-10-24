---
title: Debiasing the BoardGameGeek ranking
# subtitle: "Applying the Gini coefficient to BoardGameGeek ratings"
slug: debiasing-boardgamegeek-ranking
author: Markus Shepherd
type: post
date: 2024-09-20T22:34:11+03:00
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

The points on the very left are the oldest games in our dataset, those published in 1970, whilst the ones on the right are those published in 2024. I've plotted games with few ratings more faintly in order to declutter the image. The bold red line is the line of best fit, i.e., the trend line that best describes the yearly increase in average ratings. This picture should look pretty familiar if you've read the [previous article]({{<ref "posts/highest_rated_year/index.md">}}), though here we plotted every single game as an individual dot instead of aggregating by year.

That trend line has a slope of 0.03, which means that overall, a game's average rating decrease by 0.03 with every year that has passed since its release. Now, removing the age bias means reducing that slope to 0. It's as if we consider each year on its own and only care how much better or worse a game was compared to its peers released at the same time. I hope this little animation will make things much clearer:

{{< img src="plot_reg_age_animated" alt="Animation: removing the age bias from games' ratings" >}}

(Again, credit to Dinesh Vatvani for introducing this kind of visualisation in [his article](https://dvatvani.com/blog/bgg-analysis-part-2).)

Next, we can use those adjusted average ratings to calculate a new, debiased ranking. In order to do this, we recreate the [BGG ranking]({{<ref "posts/reverse_engineer_bgg/index.md">}}) by taking the Bayesian average, i.e., adding 2311 dummy ratings ([one for every 10,000 ratings]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}) in total) of 5.5.

Without further ado, those are the new top 10 rated games after removing the age bias:

|Rank|Game|Rating|
|:--:|:---|:----:|
|**#1** <small>(🔺 2)</small>|{{% game 174430 %}}Gloomhaven{{% /game %}} <small>(2017)</small>|8.4 <small>(🔻 0.2)</small>|
|**#2** <small>(🔺 11)</small>|{{% game 12333 %}}Twilight Struggle{{% /game %}} <small>(2005)</small>|8.4 <small>(🔺 0.2)</small>|
|**#3** <small>(🔻 1)</small>|{{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}} <small>(2015)</small>|8.4 <small>(🔻 0.1)</small>|
|**#4** <small>(🔺 4)</small>|{{% game 115746 %}}War of the Ring: Second Edition{{% /game %}} <small>(2011)</small>|8.5 <small>(🔸 0.0)</small>|
|**#5** <small>(🔻 4)</small>|{{% game 224517 %}}Brass: Birmingham{{% /game %}} <small>(2018)</small>|8.4 <small>(🔻 0.2)</small>|
|**#6** <small>(🔺 145)</small>|{{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} <small>(1982)</small>|8.5 <small>(🔺 0.8)</small>|
|**#7** <small>(🔸 0)</small>|{{% game 167791 %}}Terraforming Mars{{% /game %}} <small>(2016)</small>|8.2 <small>(🔻 0.2)</small>|
|**#8** <small>(🔻 4)</small>|{{% game 342942 %}}Ark Nova{{% /game %}} <small>(2021)</small>|8.2 <small>(🔻 0.3)</small>|
|**#9** <small>(🔺 36)</small>|{{% game 3076 %}}Puerto Rico{{% /game %}} <small>(2002)</small>|8.2 <small>(🔺 0.2)</small>|
|**#10** <small>(🔻 1)</small>|{{% game 187645 %}}Star Wars: Rebellion{{% /game %}} <small>(2016)</small>|8.2 <small>(🔻 0.2)</small>|

As designed, older games are the big winners of this adjustment, with former BGG #1s {{% game 12333 %}}Twilight Struggle{{% /game %}} and {{% game 3076 %}}Puerto Rico{{% /game %}} making a comeback. Classic murder mystery game {{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} makes a huge leap into the top 10 as one of the few games from the 80s that stood the test of time. You can download the full new ranking [here](ranking_debiased_age.csv).


# Removing the complexity bias

Obviously, we can apply the exact same idea to other features, e.g., a game's complexity (or weight) as Dinesh Vatvani did in his [original article](https://dvatvani.com/blog/bgg-analysis-part-2). Again, we start by looking at the spread of the data points, from the lightest games on the left to the heaviest on the right:

{{< img src="plot_reg_complexity" alt="Scatter plot: a game's complexity vs its rating" >}}

The trend line has a slope of 0.63, i.e., the heaviest games on BGG have on average a full 2.5 point higher average score than the lighest ones. Somehow it feels particularly pleasing to see the light but clever games being lifted up when we remove this complexity bias:

{{< img src="plot_reg_complexity_animated" alt="Animation: removing the complexity bias from games' ratings" >}}

This is the new top 10 after adjusting for the complexity bias:

|Rank|Game|Rating|
|:--:|:---|:----:|
|**#1** <small>(🔺 141)</small>|{{% game 254640 %}}Just One{{% /game %}} <small>(2018)</small>|8.2 <small>(🔺 0.6)</small>|
|**#2** <small>(🔺 127)</small>|{{% game 178900 %}}Codenames{{% /game %}} <small>(2015)</small>|8.0 <small>(🔺 0.4)</small>|
|**#3** <small>(🔺 45)</small>|{{% game 295947 %}}Cascadia{{% /game %}} <small>(2021)</small>|8.0 <small>(🔺 0.1)</small>|
|**#4** <small>(🔺 101)</small>|{{% game 291453 %}}SCOUT{{% /game %}} <small>(2019)</small>|8.2 <small>(🔺 0.4)</small>|
|**#5** <small>(🔻 3)</small>|{{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}} <small>(2015)</small>|8.0 <small>(🔻 0.6)</small>|
|**#6** <small>(🔺 13)</small>|{{% game 173346 %}}7 Wonders Duel{{% /game %}} <small>(2015)</small>|7.9 <small>(🔻 0.2)</small>|
|**#7** <small>(🔺 30)</small>|{{% game 324856 %}}The Crew: Mission Deep Sea{{% /game %}} <small>(2021)</small>|8.1 <small>(🔻 0.1)</small>|
|**#8** <small>(🔺 71)</small>|{{% game 230802 %}}Azul{{% /game %}} <small>(2017)</small>|7.8 <small>(🔺 0.1)</small>|
|**#9** <small>(🔺 117)</small>|{{% game 163412 %}}Patchwork{{% /game %}} <small>(2014)</small>|7.8 <small>(🔺 0.2)</small>|
|**#10** <small>(🔺 57)</small>|{{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}} <small>(2018)</small>|7.8 <small>(🔸 0.0)</small>|

I'm not going to lie: As a lover of small and interactive games, this top 10 looks much more apealing to me than the actual BGG top 10. One striking observation: six out of these ten games won {{% sdj %}}Spiel{{% /sdj %}} or {{% kdj / %}} (if we generously count the other {{% game 284083 %}}Crew{{% /game %}}'s title), with two more nominated and the other two recommended. The grognards on the internet can complain all they want about how the awards have become too shallow, but the jury really knows how to pick out the games that put the maximum amount of game play into minimal rules. You can download the full new ranking [here](ranking_debiased_complexity.csv).


# Removing the playing time bias

Next, we'll take a look at how a game's playing time (as measured by the minimum playing time printed on the box) affects its rating:

{{< img src="plot_reg_min_time" alt="Scatter plot: a game's minimum playing time vs its rating" >}}

We see a similar trend line as with the complexity bias, which shouldn't come as a surprise since a game's length and complexity are highly correlated. The slope here is 0.0045, i.e., every minute it takes longer to play a game makes it 0.0045 points "better", which does sound a bit weird when one puts it like that.

Because publishers love to lie about playing time and claim most games can be played in about an hour, the adjusted ranking doesn't look all that different from the usual one, so I'll skip it for this article, but you can download it [here](ranking_debiased_min_time.csv) if you'd like to take a look anyways.


# Removing the game type bias

So far, we've been looking at continuous values (also known as numerical features), but we can apply the same principal to categories. One particularly interesting feature in this context is a game's type: BGG maintains separate rankings for eight different game types, and users can vote which of those types a game belongs to (depending on the share of votes, a game might be classified as more than one type). Given everything we've seen so far, you can probably already guess that the lighter categories like children's and party games aren't as highly praised as war and strategy games. Here's all eight types sorted from lowest to highest average rating:

{{< img src="plot_cat_game_type" alt="Violin plot: game types vs their ratings" >}}

Each of those little violins represent the distribution of ratings amongst that type, with the white line indicating the median. Removing the game type bias now means bringing those distributions in line:

{{< img src="plot_cat_game_type_animated" alt="Animation: removing the game type bias from games' ratings" >}}

Just like before, we can calculate a new, debiased ranking:

|Rank|Game|Rating|
|:--:|:---|:----:|
|**#1** <small>(🔸 0)</small>|{{% game 224517 %}}Brass: Birmingham{{% /game %}} <small>(2018)</small>|8.2 <small>(🔻 0.4)</small>|
|**#2** <small>(🔺 7)</small>|{{% game 187645 %}}Star Wars: Rebellion{{% /game %}} <small>(2016)</small>|8.2 <small>(🔻 0.2)</small>|
|**#3** <small>(🔺 1)</small>|{{% game 342942 %}}Ark Nova{{% /game %}} <small>(2021)</small>|8.1 <small>(🔻 0.4)</small>|
|**#4** <small>(🔺 36)</small>|{{% game 285774 %}}Marvel Champions: The Card Game{{% /game %}} <small>(2019)</small>|8.2 <small>(🔺 0.1)</small>|
|**#5** <small>(🔺 43)</small>|{{% game 295947 %}}Cascadia{{% /game %}} <small>(2021)</small>|8.1 <small>(🔺 0.1)</small>|
|**#6** <small>(🔺 31)</small>|{{% game 324856 %}}The Crew: Mission Deep Sea{{% /game %}} <small>(2021)</small>|8.2 <small>(🔺 0.1)</small>|
|**#7** <small>(🔺 34)</small>|{{% game 366013 %}}Heat: Pedal to the Metal{{% /game %}} <small>(2022)</small>|8.1 <small>(🔺 0.1)</small>|
|**#8** <small>(🔻 2)</small>|{{% game 316554 %}}Dune: Imperium{{% /game %}} <small>(2020)</small>|8.0 <small>(🔻 0.4)</small>|
|**#9** <small>(🔻 2)</small>|{{% game 167791 %}}Terraforming Mars{{% /game %}} <small>(2016)</small>|7.9 <small>(🔻 0.4)</small>|
|**#10** <small>(🔺 11)</small>|{{% game 167355 %}}Nemesis{{% /game %}} <small>(2018)</small>|8.0 <small>(🔻 0.2)</small>|

At first glance, it might seem curious that some games from the current BGG top 10 stay (more or less) put whilst others fall off. The reason for this is that both {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}} and {{% game 174430 %}}Gloomhaven{{% /game %}} are considered to be both strategy and thematic games, two of the most popular categories, and so the model weighs them down twice. Instead, we see some of the top rated customisable, abstract and family games in this adjusted top 10. Again, you can download the full new ranking [here](ranking_debiased_game_type.csv).


# Removing the bias towards cooperative games

Let's take a look at one final categorical feature to debias: competitive vs cooperative games. Cooperative games have been on the rise for a number of years now, winning six out of ten {{% sdj %}}Spiel{{% /sdj %}} and {{% kdj / %}} awards since I started my predictions in [2020]({{<ref "posts/sdj_2020_4/index.md">}}). While less than 9% of all games in our dataset are cooperative, on average they have a significantly higher (by almost 0.48 points) rating compared to competitive games:

{{< img src="plot_cat_cooperative" alt="Violin plot: competitive/cooperative games vs their ratings" >}}

We can go through the exercise of debiasing the ratings and calculating a new ranking here too, but the outcome would pretty much be just the standard BGG ranking with the cooperative games filter out (or rather weighed down). If you really want to take a look, you can download the new ranking [here](ranking_debiased_cooperative.csv).


# Removing *all* the biases

OK, so you might be wondering by now why I went through all that trouble, in particular since complexity, playing time and game types are all so strongly correlated. You've probably also been thinking *association isn't causation*. You'd be right: viewing those different features *individually*, this approach yields nothing but correlations. But take them all *together* and we get a shot at a bit of [causal inference](https://matheusfacure.github.io/python-causality-handbook/05-The-Unreasonable-Effectiveness-of-Linear-Regression.html).

How does it work? So far, I've calculated those trend lines using simple linear regression (also known as the ordinary least squares method) in a single explanatory variable. But the maths works just the same in higher dimensions and we can throw *all* the features discussed above at once into a single model, predicting again the game's rating, but now with much more information. The outcome is this:

> **Estimated rating** =  
> -0.031 * age in years  
> +0.567 * complexity score  
> -0.001 * minimum playing time in minutes  
> +0.167 if an abstract game  
> -0.029 if a children's game  
> -0.030 if a customizable game  
> +0.225 if a family game  
> +0.274 if a party game  
> +0.125 if a strategy game  
> +0.125 if a thematic game  
> +0.485 if a war game  
> +0.199 if cooperative  
> +5.700

It's worth taking a look at and comparing some of those coefficients. First of: Age and complexity have about the same influence in this combined model as they had individually. This means that age and complexity biases are real. Even when taking other factors into account, gamers clearly strongly prefer newer over older and heavier over lighter games.

Interestingly, something different is happening with playing time: If you recall, the original model estimated that every minute of additional playing time *increased* the rating by around 0.005, but this model tells us that every minute extra actually *decreases* a game's rating by 0.001. This number is very small, but the direction is still statistically significant. This is a sign that the model correctly decoupled what we discussed before intuitively: the positive correlation between a game's length and rating can be explained by the game's complexity. Once we take that into account, any additional playing time actually harms the game's rating. In other words: Our model finds that – all other features being equal – players do prefer shorter over longer games.

We observe some similar effects with the game types. In the single feature model, children's games were rated over 0.6 points lower. But in this multi feature model, the coefficient is very close to zero, in fact not statistically significantly different. This is evidence that the 'geeks don't actually have a systematic bias against children's games – they dislike all light games equally, no matter whether they are for children or adults.

Finally, the bias in favour of cooperative games is still pretty clear, but at around 0.2 it's less than have what the single feature model predicted. They clearly are very fashionable, but much of their higher average ratings can be explained by other variables.

Enough looking at coefficients, let's finally move on to the moment you didn't even know you were looking forward to: the ultimate debiased ranking. Just like with all the other models, we can use this multivariate model to debias the games' ratings by simply setting all those coefficients to zero. We lose the ability to animate this process for easy visualisation, but we gain average ratings and a ranking freed of all the biases we've been talking about:

|Rank|Game|Rating|
|:--:|:---|:----:|
|**#1** <small>(🔺 323)</small>|{{% game 2653 %}}Survive: Escape from Atlantis!{{% /game %}} <small>(1982)</small>|8.2 <small>(🔺 0.9)</small>|
|**#2** <small>(🔺 772)</small>|{{% game 41 %}}Can't Stop{{% /game %}} <small>(1980)</small>|8.2 <small>(🔺 1.3)</small>|
|**#3** <small>(🔺 326)</small>|{{% game 172 %}}For Sale{{% /game %}} <small>(1997)</small>|7.9 <small>(🔺 0.7)</small>|
|**#4** <small>(🔺 15)</small>|{{% game 173346 %}}7 Wonders Duel{{% /game %}} <small>(2015)</small>|7.8 <small>(🔻 0.3)</small>|
|**#5** <small>(🔺 146)</small>|{{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} <small>(1982)</small>|7.9 <small>(🔺 0.3)</small>|
|**#6** <small>(🔺 209)</small>|{{% game 215 %}}Tichu{{% /game %}} <small>(1991)</small>|8.0 <small>(🔺 0.4)</small>|
|**#7** <small>(🔺 205)</small>|{{% game 118 %}}Modern Art{{% /game %}} <small>(1992)</small>|7.9 <small>(🔺 0.4)</small>|
|**#8** <small>(🔺 637)</small>|{{% game 432 %}}Take 5{{% /game %}} <small>(1994)</small>|7.8 <small>(🔺 0.8)</small>|
|**#9** <small>(🔺 316)</small>|{{% game 50 %}}Lost Cities{{% /game %}} <small>(1999)</small>|7.7 <small>(🔺 0.5)</small>|
|**#10** <small>(🔺 204)</small>|{{% game 822 %}}Carcassonne{{% /game %}} <small>(2000)</small>|7.6 <small>(🔺 0.2)</small>|
|**#11** <small>(🔺 177)</small>|{{% game 54043 %}}Jaipur{{% /game %}} <small>(2009)</small>|7.7 <small>(🔺 0.2)</small>|
|**#12** <small>(🔺 117)</small>|{{% game 178900 %}}Codenames{{% /game %}} <small>(2015)</small>|7.6 <small>(🔺 0.1)</small>|
|**#13** <small>(🔺 125)</small>|{{% game 12 %}}Ra{{% /game %}} <small>(1999)</small>|7.7 <small>(🔺 0.1)</small>|
|**#14** <small>(🔺 141)</small>|{{% game 14996 %}}Ticket to Ride: Europe{{% /game %}} <small>(2005)</small>|7.6 <small>(🔺 0.1)</small>|
|**#15** <small>(🔺 76)</small>|{{% game 93 %}}El Grande{{% /game %}} <small>(1995)</small>|7.7 <small>(🔻 0.1)</small>|
|**#16** <small>(🔻 9)</small>|{{% game 167791 %}}Terraforming Mars{{% /game %}} <small>(2016)</small>|7.6 <small>(🔻 0.8)</small>|
|**#17** <small>(🔻 15)</small>|{{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}} <small>(2015)</small>|7.6 <small>(🔻 0.9)</small>|
|**#18** <small>(🔺 289)</small>|{{% game 46213 %}}Telestrations{{% /game %}} <small>(2009)</small>|7.8 <small>(🔺 0.4)</small>|
|**#19** <small>(🔺 211)</small>|{{% game 9209 %}}Ticket to Ride{{% /game %}} <small>(2004)</small>|7.5 <small>(🔺 0.1)</small>|
|**#20** <small>(🔺 85)</small>|{{% game 291453 %}}SCOUT{{% /game %}} <small>(2019)</small>|7.8 <small>(🔻 0.1)</small>|
|**#21** <small>(🔺 273)</small>|{{% game 760 %}}Battle Line{{% /game %}} <small>(2000)</small>|7.8 <small>(🔺 0.3)</small>|
|**#22** <small>(🔺 634)</small>|{{% game 699 %}}HeroQuest{{% /game %}} <small>(1989)</small>|7.8 <small>(🔺 0.6)</small>|
|**#23** <small>(🔺 368)</small>|{{% game 39856 %}}Dixit{{% /game %}} <small>(2008)</small>|7.5 <small>(🔺 0.3)</small>|
|**#24** <small>(🔻 8)</small>|{{% game 84876 %}}The Castles of Burgundy{{% /game %}} <small>(2011)</small>|7.5 <small>(🔻 0.6)</small>|
|**#25** <small>(🔻 19)</small>|{{% game 316554 %}}Dune: Imperium{{% /game %}} <small>(2020)</small>|7.5 <small>(🔻 0.9)</small>|

I will say: {{% game 2653 %}}Survive: Escape from Atlantis!{{% /game %}} is not a game I would have expected on top of this list. In general, this top 25 is clearly much lighter and less recent than the regular BGG ranking. Personally, I'm up for this: it's a wonderful list full of proven classics, devoid of any cult of the new or Kickstarter bloat.

Some games made huge leaps into the top 100, including {{% game 811 %}}Rummikub{{% /game %}}, {{% game 327 %}}Loopin' Louie{{% /game %}} and {{% game 17329 %}}Animal Upon Animal{{% /game %}} which all jumped up over 1000 positions. The biggest losers of this method – games dropping out of the top 100 – are {{% game 184267 %}}On Mars{{% /game %}}, {{% game 237182 %}}Root{{% /game %}} and {{% game 96848 %}}Mage Knight{{% /game %}}, all of which lost 1000 positions and more. You can download the full debiased ranking [here](ranking_debiased_all.csv).


# Some boring technical details

In order to have good data and comparable values for all those corrections, I had to filter out games by certain criteria. We only considered games which:

- are ranked (i.e., rated by at least 30 users),
- have a complexity score,
- have been released between 1970 and 2024 and
- have a minimum playing time of at most 3 hours.

This includes 23,325 of the 26,266 currently ranked games (88.8%), but does exclude some notable games, such as:

- {{% game 233078 %}}Twilight Imperium{{% /game %}}, {{% game 91 %}}Paths of Glory{{% /game %}} and {{% game 1 %}}Die Macher{{% /game %}} (too long), as well as
- {{% game 521 %}}Crokinole{{% /game %}}, {{% game 188 %}}Go{{% /game %}} and {{% game 5 %}}Acquire{{% /game %}} (too old).

Those are the highest ranked exclusions. While it's definitely sad to miss out on those and some other games, they make up only 2% of the top 1000 games on BGG, so I feel it's a reasonable tradeoff.


# Conclusion

So that's a wrap on our quest for debiased rankings. It's important to remember that *bias* isn't a negative term in this context – we're simply interested in the tendencies that pertain to the BGG user ratings and try to imagine counterfactual rankings if those tendencies didn't exist. By considering not just a single feature like age or complexity, but throwing those two as well as playing time, game type and cooperative into one model, we hope to explain the way those features influence ratings beyond mere correlations. If you're interested in the mathematical background to this method, I highly recommend the [article](https://matheusfacure.github.io/python-causality-handbook/05-The-Unreasonable-Effectiveness-of-Linear-Regression.html) I've already linked above.

*As always, you can find the full analysis code and notebooks on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/debiased_rankings).*
