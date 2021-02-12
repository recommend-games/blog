---
title: What makes a Kennerspiel?
# slug: and-the-spiel-des-jahres-2020-goes-to
author: Markus Shepherd
type: post
date: 2021-02-09T12:00:00+02:00
tags:
  - Spiel des Jahres
  - Kennerspiel
  - Kennerspiel des Jahres
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-2.2.3.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.2.3.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.2.3.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-2.2.3.min.js" ></script>

{{% sdj %}}Spiel des Jahres 2021{{% /sdj %}} nominations might still be a couple of months away, but I thought now is still a good time to return to one of the harder questions in [my predictions post from last year]({{<ref "posts/sdj_2020/index.md">}}): What exactly makes a game a {{% kdj %}}Kennerspiel{{% /kdj %}}? By that I don't mean the qualities that earn a game the award, but the distinction between the more casual {{% sdj %}}Spiel{{% /sdj %}} and the more complex {{% kdj %}}Kennerspiel{{% /kdj %}} categories.

This question was particularly pertinent in 2020 when four out of the six nominees for the two adult awards straddled the line between {{% sdj %}}Spiel{{% /sdj %}} and {{% kdj %}}Kennerspiel{{% /kdj %}}: {{% game 295486 %}}My City{{% /game %}}, {{% game 284435 %}}Nova Luna{{% /game %}}, {{% game 263918 %}}Cartographers{{% /game %}}, and {{% game 284083 %}}The Crew{{% /game %}} could all have landed in either category. Jury member Udo Bartsch wrote a [very interesting essay](https://www.spiel-des-jahres.de/rot-oder-anthrazit-spiele-im-grenzbereich/) about the very topic of this article, giving some insight into the reasoning behind the jury's decision. Basically, the distinction isn't so much about complexity or depth of play, but *approachability*. How many people can take the hurdles that are in the way before playing a particular game? According to Mr Bartsch, this question doesn't have a simple answer:

> Which game is a game for everyone and which is not is unfortunately not recognised by generally applicable, precisely measurable characteristics, but only when playing with as many different people as possible.

Challenge accepted! Who needs humans when we can just deal with data instead? 🤓

# Let's look at the data

Since the introduction of {{% kdj %}}Kennerspiel des Jahres{{% /kdj %}} in 2011 there were a total of **90** games on the longlist for {{% sdj %}}Spiel des Jahres{{% /sdj %}} and **64** games for {{% kdj %}}Kennerspiel{{% /kdj %}}[^kennerspiel]. It's not a large amount of data to make any inferences on, but we'll try anyways.

The first step is always to familiarise yourself with the task and data at hand. With [BoardGameGeek](https://boardgamegeek.com/) collecting all sorts of data about games, we know features of those jury recommendations like complexity, player age and count, play time, mechanics, themes, …

Why don't we start simple and plot the games by their complexity (also known as weight) and minimum age?

{{% bokeh "complexity_vs_min_age.json" %}}

You see the jury's favourites of the past decade lining up from simple (left) to complex (right), and from child friendly (bottom) to more mature (top). Unsurprisingly, the red {{% sdj %}}Spiel des Jahres{{% /sdj %}} recommendations generally cluster in the bottom left, while the anthracite {{% kdj %}}Kennerspiel{{% /kdj %}} games tend towards the top right. The dotted line is the one that best[^logistic] separates {{% sdj %}}Spiel{{% /sdj %}} from {{% kdj %}}Kennerspiel{{% /kdj %}}.

However, there is some significant overlap. In particular, a lot of games of either award can be found around the 10 year / complexity 2 (medium light) intersect. I've marked games with squares that fall on the "wrong" side of the line. Some notable outliers are:

| Name                                                                | Year | Complexity | Min age | Award |
|:--------------------------------------------------------------------|:----:|-----------:|--------:|:-----:|
| {{% game 125618 %}}Libertalia{{% /game %}}                          | 2013 |        2.2 |      14 |  SdJ  |
| {{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}}           | 2018 |        1.9 |      10 |  KdJ  |
| {{% game 244522 %}}That's Pretty Clever!{{% /game %}}               | 2018 |        1.9 |       8 |  KdJ  |
| {{% game 263918 %}}Cartographers{{% /game %}}                       | 2020 |        1.9 |      10 |  KdJ  |
| {{% game 284083 %}}The Crew: The Quest for Planet Nine{{% /game %}} | 2020 |        2.0 |      10 |  KdJ  |
| {{% game 295486 %}}My City{{% /game %}}                             | 2020 |        2.1 |      10 |  SdJ  |
| {{% game 223953 %}}Kitchen Rush{{% /game %}}                        | 2020 |        2.2 |      12 |  SdJ  |

So by all means, 2020 *did* contain a lot of games just on the border of the two awards.

Generally, this works pretty well for such a simple model (a linear function in two variables is really first semester kind of stuff). But some games seem to really push far into the other side, e.g., {{% game 244522 %}}That's Pretty Clever!{{% /game %}} and {{% game 223953 %}}Kitchen Rush{{% /game %}}. Are there some other characteristics of those games that explain the jury's classification?

# Can we do better?

Complexity and minimum age make a pretty powerful pair, but the only reason I picked two features is because we can nicely visualise everything in 2D. I don't know about you, but my brain can only handle three dimensions – on a good day…

Mathematics to the rescue! Higher dimensions pose no challenge to our old friend, and we can throw as many variables at it as we want. So let's add some more features to our model:

* complexity (weight between 1 and 5),
* minimum age (between 6 and 16 years),
* minimum and maximum play time (between 1 minute 🏃 and 3 hours),
* player count (between 1 and 100 👀 players),
* cooperative or competitive game,
* types (e.g., family, strategy, or party game),
* categories (e.g., card, economic, or medieval game), and
* mechanics (e.g., hand management, set collection, or worker placement).

Using the same set of games, but incorporating all those values, we can go through the same process that produced the separating line in the plot above (multivariate logistic regression, in case you're curious). This time, that dividing line would rather be a *hyperplane* in high dimensional space, but don't worry about that. In fact, we can do better that just a yes/no classification: We can estimate our *confidence* that a certain game is in fact a {{% kdj %}}Kennerspiel{{% /kdj %}}.

This model classifies a whooping 150 out of 154 games correctly as either {{% sdj %}}Spiel{{% /sdj %}} or {{% kdj %}}Kennerspiel{{% /kdj %}} – that's 97.4% accurate. 🤯 So much for not being measurable, Mr Bartsch!

So, let's take a look back at our problem games from before and check how much confidence our model has that the respective game is for connoisseurs:

| Name                                                                | Year | Award | Confidence | 🤔 |
|:--------------------------------------------------------------------|:----:|:-----:|-----------:|:-:|
| {{% game 125618 %}}Libertalia{{% /game %}}                          | 2013 |  SdJ  |      91.2% | 🤬 |
| {{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}}           | 2018 |  KdJ  |      65.3% | ✅ |
| {{% game 244522 %}}That's Pretty Clever!{{% /game %}}               | 2018 |  KdJ  |      51.8% | ✅ |
| {{% game 263918 %}}Cartographers{{% /game %}}                       | 2020 |  KdJ  |      84.7% | ✅ |
| {{% game 284083 %}}The Crew: The Quest for Planet Nine{{% /game %}} | 2020 |  KdJ  |      41.7% | 😕 |
| {{% game 295486 %}}My City{{% /game %}}                             | 2020 |  SdJ  |      36.0% | ✅ |
| {{% game 223953 %}}Kitchen Rush{{% /game %}}                        | 2020 |  SdJ  |      37.4% | ✅ |

This picture certainly has improved, and we're even classifying games like {{% game 244522 %}}That's Pretty Clever!{{% /game %}} (just about) and {{% game 223953 %}}Kitchen Rush{{% /game %}} right that caused us a lot of headaches before. However, {{% game 284083 %}}The Crew{{% /game %}} still eludes correct classification, and {{% game 125618 %}}Libertalia{{% /game %}} is so far off that I'd argue the jury simply got that one wrong…

"Not so fast!", you might say. "Aren't you simply overfitting here?" Why, yes, you're right. The dataset is so small that there's a high risk of fine tuning the model too much for the data we're seeing. And of course, it's **bad bad bad** to assess you're model's performance on items it was trained on – that's just cheating. So let's test the model on some games it hadn't seen yet!

# What about old games?

{{% bokeh "complexity_vs_min_age_before_2011.json" %}}

# Outline

Interpret / highlight some features

What games do we still get wrong and why?

Apply to old SdJ winners / nominees: which ones would be a Kennerspiel by today's standards?


Shapley values?

Looking ahead to some 2021 candidates

[^kennerspiel]: In 2011, there was no separate recommendation list for the two awards, so I only included the nominees for 2011. I also added the special award winners {{% game 18602 %}}Caylus{{% /game %}}, {{% game 31260 %}}Agricola{{% /game %}}, {{% game 43528 %}}World Without End{{% /game %}}, and {{% game 221107 %}}Pandemic Legacy: Season 2{{% /game %}} to the {{% kdj %}}Kennerspiel{{% /kdj %}} list.
[^logistic]: Using logistic regression with F1–score as target metric. Other definitions of "best line" of course might yield different results.
