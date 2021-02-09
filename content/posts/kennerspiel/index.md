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

# Outline

Simple 2D model, quite good at separating:

{{% bokeh "complexity_vs_min_age.json" %}}

We can do better with more features, multinomial logistic regression.

Interpret / highlight some features

What games do we still get wrong and why?

Apply to old SdJ winners / nominees: which ones would be a Kennerspiel by today's standards?

{{% bokeh "complexity_vs_min_age_before_2011.json" %}}

Shapley values?

Looking ahead to some 2021 candidates
