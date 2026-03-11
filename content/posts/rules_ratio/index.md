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

You might recognise this idea of "adding pseudo counts to stabilise estimates based on small samples" from our discussion of the [BGG rankings]({{<ref "posts/reverse_engineer_bgg/index.md">}}) and their usage of a Bayesian average of ratings. It's the same principle: pick a prior and update it as more and more data comes in.


# RR in the wild

WEM already gave quite a few interesting examples of RRs, especially for popular and highly rated games. Here are some more games that stuck out. The highest RR of all games in my sample belongs to {{% game 182094 %}}BANG! The Duel{{% /game %}}: a staggering 87 out of the 99 threads are about rules, for an RR of 88%. Looks like there's a rulebook in desperate need of an editor.

The perhaps most surprisingly high RR belongs to {{% game 399088 %}}UNO: Show 'Em No Mercy{{% /game %}}: 24 out of the 31 threads (RR: 77%) are about the rules. I don't know what's more surprising: that the 'geeks take such an interest in an UNO variant at all, or how much they seem to struggle with its rules.

The highest RR amongst the highly rated games (ranked amongst the top 1000 games) is that of {{% game 408180 %}}Shackleton Base{{% /game %}} at 69%. When looking at very popular games (more than 10k ratings), we find another unexpected title in this field: {{% game 234190 %}}Unstable Unicorns{{% /game %}} at a whooping 64%. Apparently players really struggle with *neighing* — and now I feel like I need to play the game just to find out what that means. 🦄

The other extreme — extremely low RRs — is dominated by games without any rules questions. WEM already mentioned one example ({{% game 318977 %}}MicroMacro{{% /game %}}, which is also the highest ranked and most popular game with such a low RR), but there is one game with an even lower RR after smoothing: {{% game 155250 %}}TseuQuesT{{% /game %}}. Of its 221 threads, not a single one deals with rules questions. What sounds like a great achievement at first sight is actually quite the opposite: almost all that forum chatter is about its unfulfilled crowdfunding campaign — a typical Kickstarter drama. Note: consume RR values with caution.

Most other games with low RR are fairly simple party or storytelling games, but there are also war games without rules questions (who would've thought?!), e.g., {{% game 36241 %}}Israeli Independence: The First Arab-Israeli War{{% /game %}} (0 rules questions out of 35 threads).

Low RRs demonstrate the effect of smoothing well: Whilst said war game {{% game 36241 %}}Israeli Independence{{% /game %}} doesn't have a single rule question, its (smoothed) RR is still (0 + 0.5) / (35 + 1) = 1.4%. So there are some games with more rules threads, but lower RR. Take, for instance, the classic party game {{% game 74 %}}Apples to Apples{{% /game %}}: 2 out of 200 threads deal with rules, for an RR of (2 + 0.5) / (200 + 1) = 1.2%. This might be somewhat counterintuitive, but the important assumption is that we don't trust values based on sparse data too much.


# RR vs complexity: the Residual Rules Ratio

Undoubtedly, readers of this blog will be familiar with the *complexity* or *weight* rating at BGG: a numerical value between 1 (*light complexity*) and 5 (*heavy complexity*), based on users' votes. This metric has its own issues, but it's still an interesting and widely quoted datapoint to characterise a game. As far as this article is concerned, it stands to reason that more complex games will generate more rules questions. Designers frequently talk about a game's complexity budget: depending on the target audience and its appetite for complexity, a game can afford more mechanisms, elements and their interactions. The more details one needs to understand in order to play the game, the more rules clarifications might be required — at least intuitively this should hold true.

Let's visualise this:

{{% bokeh "rules_ratio_vs_complexity.json" %}}

Every dot represents a game, positioned by its complexity (x-axis) and RR (y-axis). Games with more ratings will be larger, whilst the colour encodes the game type. This is an interactive plot, so I'll invite you to explore it by hovering over the dots and find your favourite game.

This plot supports our intuition well: more complex games tend to have higher RR, though the spread is considerable.

WEM's suggestion to account for the complexity budget when reasoning about RR is the RRW: **Rules Ratio by Weight**, i.e., the game's RR divided by its weight:

\\[
  \text{RRW} = \frac{\text{RR}}{\text{complexity}}.
\\]

As discussed, taking complexity into account is the right instinct, but simply dividing would make only sense if complexity was a multiplicative measure. But while BGG is intentionally vague about what their complexity metric means, it should be clear that a game of weight 4 isn't "twice as heavy" as a game of weight 2.

Instead, I suggest the RRR: the Residual Rules Ratio. The idea is to estimate the "typical RR" of a game of a certain complexity, then compare the actual RR to this "typical RR". Their difference is the RRR.

Let's take this step by step. First we need to find said "typical RR" for a given weight. As usually, regression is our friend: we fit a simple model to explain RR in relationship to complexity. Since RR is a fraction between 0 and 1 (because of the smoothing *strictly* between those values), we'll use a logistic model. Feeding the data into the statistical software of your choice yields this formula:

\\[
  \widehat\text{RR} = \sigma(0.3381 \cdot \text{complexity} - 1.6104),
\\]

where \\(\sigma\\) is the [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function) we most recently encountered in the context of the [Elo ratings]({{<ref "posts/elo_1/index.md">}}).

TODO: What does this mean? Odds ratio interpretation / example values.

Equipped with this estimator, we can define the **Residual Rules Ratio** (RRR):

\\[
  \text{RRR} = \text{RR} - \widehat\text{RR}.
\\]

The intuition behind RRR is that we measure how much more or less confusing a rulebook is than the peers in its "weight class". Since both constituent values are in %, RRR itself would be naturally denoted in percentage points. In a time-honoured scientific tradition, I suggest naming the unit **wem**:

> **1 wem = 1 percentage point of RRR**.

RRR can range from +100 wem (a game with lots more rules questions than expected) to -100 wem (a game much clearer than expected).

What does this look like in practice? First, let's do the same plot as before, but with RRR instead of RR:

{{% bokeh "residual_rules_ratio_vs_complexity.json" %}}

Note how the upward trend has turned into a horizontal line. This is the same idea we used to [debias the BGG rankings]({{<ref "posts/debiased_rankings/index.md">}}).

One of the dots that immediately sticks out is (again) {{% game 234190 %}}Unstable Unicorns{{% /game %}}. While it didn't have the highest RR in the plot above, it does raise a lot more rules questions than a typical light game and hence takes the somewhat questionable lead in this plot at +39 wem RRR. Another light game with a high RRR is {{% game 1111 %}}Taboo{{% /game %}} at +33 wem. Most of the rules questions seem be disputes about allowed or forbidden clues, which isn't your typical rules question, but then again it does show that the system has some fuzziness about it that requires interpretation, which does hit the core of RR.

On the other end of the spectrum we see the three original EXIT games which one the 2017 {{% kdj %}}Kennerspiel{{% /kdj %}} award with RRR of -31 to -28 wem. I don't know if the rules are written so well, or if it's their real-time one-and-done nature that makes few people stop and post rules questions. {{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} has a similarly low RRR of -28 wem. Apparently, it pays off when the rules are in the story you're experiencing.

It's also interesting to see that WEM's poster child {{% game 318977 %}}MicroMacro{{% /game %}} isn't so exceptional anymore: its RRR of -22 wem is comparable to the -21 wem of the heavyweight {{% game 120677 %}}Terra Mystica{{% /game %}}. The latter's rule clarity is even more remarkable when you remember that significant portion of its appeal is due to the asymmetric factions, which is usually a receipt for a crowded rules forum.

TODO: Top / bottom 10 lists, link to CSV.


# Summary / conclusion

Does it mean anything? Perhaps not as a definitive quality metric, but it’s a fascinating proxy for *game clarity*. A game like {{% game 224517 %}}Brass: Birmingham{{% /game %}} (-3 wem) sitting below the regression line suggests its rules, while heavy, are remarkably coherent. Conversely, {{% game 342942 %}}Ark Nova{{% /game %}} (+9 wem) has a high "rulebook debt", likely due to the massive variety of unique card effects.

The goal isn't to punish complex games, but to celebrate the ones that manage to stay intuitive despite their depth. Let's just hope nobody starts "ratio-bombing" BGG threads to mess with the stats! 😅


# Appendix: Methodology

TODO: data etc.


[^fediverse]: Come for the board game news, stay for their policy of [not tracking users](https://www.wericmartin.com/board-game-beat-policies/) and their [Fediverse first](https://www.wericmartin.com/federated-social-media-video/) approach. 🤓
[^threads]: WEM talks about forum posts in his article, but from the screenshot and numbers it's evident he's using threads. I think this is the correct choice for what we're interested in: every distinct rules question typically goes into its own thread, and we want to know how many rules questions a given game triggers, not how many posts it takes to resolve them.
[^ratio]: Ackshually… 🤓 Calling this metric a "ratio" isn't technically wrong, but "share", "proportion" or "fraction" would be more accurate. WEM told us to geek out, so please indulge me in this little pedantry.
[^3b1b]: If you want to learn more about this technique, I highly recommend the always excellent Grant Sanderson and his [3blue1brown video](https://youtu.be/8idr1WZ1A7Q) on the topic.
