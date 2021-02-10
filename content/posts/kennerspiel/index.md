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

Spiel des Jahres 2021 nominations might still be a couple of months away, but I thought now is still a good time to return to one of the harder questions in [my predictions post from last year]({{<ref "posts/sdj_2020/index.md">}}): What exactly makes a game a {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}}? By that I don't mean the qualities that earn a game the award, but the distinction between the more casual {{% color "#E30613" %}}***Spiel***{{% /color %}} and the more complex {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}} categories.

This question was particularly pertinent in 2020 when four out of the six nominees for the two adult awards straddled the line between {{% color "#E30613" %}}***Spiel***{{% /color %}} and {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}}: {{% game 295486 %}}My City{{% /game %}}, {{% game 284435 %}}Nova Luna{{% /game %}}, {{% game 263918 %}}Cartographers{{% /game %}}, and {{% game 284083 %}}The Crew{{% /game %}} could all have landed in either category. Jury member Udo Bartsch wrote a [very interesting essay](https://www.spiel-des-jahres.de/rot-oder-anthrazit-spiele-im-grenzbereich/) about the very topic of this article, giving some insight into the reasoning behind the jury's decision. Basically, the distinction isn't so much about complexity or depth of play, but *approachability*. How many people can take the hurdles that are in the way before playing a particular game? According to Mr Bartsch, this question doesn't have a simple answer:

> Which game is a game for everyone and which is not is unfortunately not recognised by generally applicable, precisely measurable characteristics, but only when playing with as many different people as possible.

Challenge accepted! Who needs humans when we can just deal with data instead? 🤓

# Let's look at the data

Since the introduction of {{% color "#193F4A" %}}***Kennerspiel des Jahres***{{% /color %}} in 2011 there were a total of **90** games on the longlist for {{% color "#E30613" %}}***Spiel des Jahres***{{% /color %}} and **64** games for {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}}[^kennerspiel]. It's not a large amount of data to make any inferences on, but we'll try anyways.

The first step is always to familiarise yourself with the task and data at hand. With [BoardGameGeek](https://boardgamegeek.com/) collecting all sorts of data about games, we know features of those jury recommendations like complexity, player age and count, play time, mechanics, themes, …

Why don't we start simple and plot the games by their complexity (also known as weight) and minimum age?

{{% bokeh "complexity_vs_min_age.json" %}}

You see the jury's favourites of the past decade lining up from simple (left) to complex (right), and from child friendly (bottom) to more mature (top). Unsurprisingly, the red {{% color "#E30613" %}}***Spiel des Jahres***{{% /color %}} recommendations generally cluster in the bottom left, while the anthracite {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}} games tend towards the top right. The dotted line is the one that best[^logistic] separates {{% color "#E30613" %}}***Spiel***{{% /color %}} from {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}}.

However, there is some significant overlap. In particular, a lot of games of either award can be found around the 10 year / complexity 2 (medium light) intersect. I've marked games with squares that fall on the "wrong" side of the line. Some notable outliers are:

| Name                                                                | Year | Complexity | Min age | Award |
|:--------------------------------------------------------------------|:----:|-----------:|--------:|:------|
| {{% game 125618 %}}Libertalia{{% /game %}}                          | 2013 |        2.2 |      14 | SdJ   |
| {{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}}           | 2018 |        1.9 |      10 | KdJ   |
| {{% game 244522 %}}That's Pretty Clever!{{% /game %}}               | 2018 |        1.9 |       8 | KdJ   |
| {{% game 263918 %}}Cartographers{{% /game %}}                       | 2020 |        1.9 |      10 | KdJ   |
| {{% game 284083 %}}The Crew: The Quest for Planet Nine{{% /game %}} | 2020 |        2.0 |      10 | KdJ   |
| {{% game 295486 %}}My City{{% /game %}}                             | 2020 |        2.1 |      10 | SdJ   |
| {{% game 223953 %}}Kitchen Rush{{% /game %}}                        | 2020 |        2.2 |      12 | SdJ   |

So by all means, 2020 *did* contain a lot of games just on the border of the two awards.

Generally, this works pretty well for such a simple model (a linear function in two variables is really first semester kind of stuff). But some games seem to really push far into the other side, e.g., {{% game 244522 %}}That's Pretty Clever!{{% /game %}} and {{% game 223953 %}}Kitchen Rush{{% /game %}}. Are there some other characteristics of those games that explain the jury's classification?

# Can we do better?

We can do better with more features, multinomial logistic regression.

# Outline

Interpret / highlight some features

What games do we still get wrong and why?

Apply to old SdJ winners / nominees: which ones would be a Kennerspiel by today's standards?

{{% bokeh "complexity_vs_min_age_before_2011.json" %}}

Shapley values?

Looking ahead to some 2021 candidates

[^kennerspiel]: In 2011, there was no separate recommendation list for the two awards, so I only included the nominees for 2011. I also added the special award winners {{% game 18602 %}}Caylus{{% /game %}}, {{% game 31260 %}}Agricola{{% /game %}}, {{% game 43528 %}}World Without End{{% /game %}}, and {{% game 221107 %}}Pandemic Legacy: Season 2{{% /game %}} to the {{% color "#193F4A" %}}***Kennerspiel***{{% /color %}} list.
[^logistic]: Using logistic regression with F1–score as target metric. Other definitions of "best line" of course might yield different results.
