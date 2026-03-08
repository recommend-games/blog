---
title: TODO
subtitle: TODO
slug: rules-ratio
author: Markus Shepherd
type: post
date: 2026-03-08T12:00:00+02:00
tags:
  - Rules ratio
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.8.2.min.js" ></script>

[W. Eric Martin](https://www.wericmartin.com) (WEM), known for having run the BoardGameGeek (BGG) [news section](https://boardgamegeek.com/blog/1/boardgamegeek-news) for over a decade, launched his own outlet called [Board Game Beat](https://www.boardgamebeat.com) a couple of weeks ago.[^fediverse] In between his signature game release updates, he writes entertaining and insightful analyses of the broader hobby. In one of his [recent articles](https://www.wericmartin.com/the-rules-ratio-a-new-stat-to-geek-out-about/), he proposed the **Rules Ratio**. The title invites us to geek out about it, so geek out we shall! 🤓


# What is the Rules Ratio?

The basic idea behind the Rules Ratio is to look at how many rules question a game generates. It stands to reason that a game with clear concepts and well written instructions will leave players less confused than a poorly written rulebook. BGG offers a direct proxy for number of rules questions via its forums. Every game listing has a variety of such forums attached, including one titled *Rules*. Depending on the game, this particular forum might be the busiest, or completly void of any traffic. WEM proposes the share of rules threads[^threads] of all threads as the Rules Ratio[^ratio] (RR):

\\[
  \text{RR} = \frac{\text{rules threads}}{\text{total threads}}.
\\]

Concretely, let's look at one of my favourite games: {{% game 51 %}}Ricochet Robots{{% /game %}}. As of the time of writing, there are a total of [183 forum threads](https://boardgamegeek.com/boardgame/51/ricochet-robots/forums/0), 22 of which concern rules:

{{% img src="ricochet_robots" alt="Screenshot of Ricochet Robots forums, highlighting the total thread count (183) and the number of rules questions (22)." %}}

So its RR is \\(22 / 183 \approx 12\\%\\). Simple and to the point.


## Make it smootheRR…

As it turns out: a little too simple. WEM's examples are all massively popular games with hundreds of forum posts. But if we want to expand this metric to the long tail of games, we need to make sure that we don't get "this game has 0 rules questions out of 3 posts" noise.

Mathematically speaking, we're trying to estimate the probability that a forum thread will be posted in the rules section. There's a simple and well established trick known as [additive smoothing](https://en.wikipedia.org/wiki/Additive_smoothing) (or Laplace's [rule of succession](https://en.wikipedia.org/wiki/Rule_of_succession)) for scenarios like this. The idea is to pretend there are two more threads than there really are: one with a rules question and one without.[^3b1b] In other words: we increase the number of rules threads by 1 and that of all threads by 2. But since this is a little too opinionated and can skew the metric a bit too much, we're actually using 0.5 and 1 instead:

\\[
  \text{RR} = \frac{\text{rules threads} + 0.5}{\text{total threads} + 1}.
\\]

This is the formula we'll use for all the calculations that follow. In popular games, this will be no more than a rounding error, but it'll make a meaningful difference in titles with less forum activity.

You might recognise this idea of "adding pseudo counts to stabilise estimates based on small samples" from our discussion of the BGG rankings and their usage of a Bayesian average of ratings. It's the same principle: pick a prior and update it as more and more data comes in.


# RR in the wild

TODO: Examples / top / bottom lists, plot

{{% bokeh "rules_ratio_vs_complexity.json" %}}


# RR vs complexity: the Residual Rules Ratio

TODO: RRW is right instinct (a higher complexity budget prices in more rules questions), but BGG complexity is not multiplicative. Instead: Regression model, residuals, more lists, plot. Unit: wem.

{{% bokeh "residual_rules_ratio_vs_complexity.json" %}}


# Summary / conclusion

Does it mean anything? I really hope it never will be taken serious enough just so the same people who do 1/10 rating bombs will create rules questions with the sole purpose of messing with games' RRs/RRRs.


# Appendix: Methodology

TODO: data etc.


[^fediverse]: TODO: [No tracking](https://www.wericmartin.com/board-game-beat-policies/). [Fediverse first](https://www.wericmartin.com/federated-social-media-video/).
[^threads]: WEM talks about forum posts in his article, but from the screenshot and numbers it's evident he's using threads. I think this is the correct choice for what we're interested in: every distinct rules question typically goes into its own thread, and we want to know how many rules questions a given game triggers, not how many posts it takes to resolve them.
[^ratio]: Ackshually… 🤓 Calling this metric a "ratio" isn't technically wrong, but "share", "proportion" or "fraction" would be more accurate. WEM told us to geek out, so please indulge me in this little pedantry.
[^3b1b]: If you want to learn more about this technique, I highly recommend the always excellent Grant Sanderson and his [3blue1brown video](https://youtu.be/8idr1WZ1A7Q) on the topic.
