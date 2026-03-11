---
title: Rules Ratio
subtitle: From WEM's geeky stat to smoothing, residuals and the new unit "wem"
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

[W. Eric Martin](https://www.wericmartin.com) (WEM) ran the BoardGameGeek (BGG) [news section](https://boardgamegeek.com/blog/1/boardgamegeek-news) for 15 years. Earlier this year, he launched his own outlet[^fediverse] called [Board Game Beat](https://www.boardgamebeat.com). In between his signature game release updates, he writes entertaining and insightful analyses of the broader hobby. In one of his [recent articles](https://www.wericmartin.com/the-rules-ratio-a-new-stat-to-geek-out-about/), he proposed the **Rules Ratio**. The title invites us to geek out about it, so geek out we shall! 🤓


# What is the Rules Ratio?

The basic idea behind the Rules Ratio is to look at how many rules questions a game generates. It stands to reason that a game with clear concepts and well-written instructions will leave players less confused than a poorly written rulebook. BGG offers a direct proxy for number of rules questions via its forums. Every game listing has a variety of such forums attached, including one titled *Rules*. Depending on the game, this particular forum might be the busiest, or completely void of any traffic. WEM proposes defining the Rules Ratio[^ratio] (RR) as the share of *Rules* threads[^threads] among all forum threads:

\\[
  \text{RR} = \frac{\text{rules threads}}{\text{total threads}}.
\\]

Concretely, consider one of my favourite games: {{% game 51 %}}Ricochet Robots{{% /game %}}. As of the time of writing, there are a total of [183 forum threads](https://boardgamegeek.com/boardgame/51/ricochet-robots/forums/0), 22 of which concern rules:

{{% img src="ricochet_robots" alt="Screenshot of Ricochet Robots forums, highlighting the total thread count (183) and the number of rules questions (22)." %}}

So its RR is \\(22 / 183 \approx 12\\%\\). Simple and to the point.


## Make it smootheRR…

As it turns out: a little too simple. WEM's examples are all massively popular games with hundreds of forum threads. But if we want to expand this metric to the long tail of games, we need to make sure that we don’t get noisy extremes like "0 out of 3".

Mathematically speaking, we're trying to estimate the probability that a forum thread will be posted in the rules section. There's a simple and well-established trick known as [additive smoothing](https://en.wikipedia.org/wiki/Additive_smoothing) (or Laplace's rule of succession) for scenarios like this. The idea is to pretend there are two more threads than there really are: one with a rules question and one without.[^3b1b] In other words: we increase the number of rules threads by 1 and that of all threads by 2. But since this is a bit too opinionated and can skew the metric too much, we're actually using 0.5 and 1 (Jeffreys prior) instead:

\\[
  \text{RR} = \frac{\text{rules threads} + 0.5}{\text{total threads} + 1}.
\\]

This is the formula we'll use for all the calculations that follow. In popular games, this will be no more than a rounding error, but it'll make a meaningful difference in titles with less forum activity.

You might recognise this idea of "adding pseudo counts to stabilise estimates based on small samples" from our discussion of the [BGG rankings]({{<ref "posts/reverse_engineer_bgg/index.md">}}) and their usage of a Bayesian average of ratings. It's the same principle: pick a prior and update it as more and more data comes in.


# RR in the wild


## High RR: when rules dominate

WEM already gave quite a few interesting examples of RRs, especially for popular and highly rated games. Here are some more games that stuck out. The highest RR of all games in my sample belongs to {{% game 182094 %}}BANG! The Duel{{% /game %}}: a staggering 87 out of the 99 threads are about rules, for an RR of 88%. That’s… a lot of clarifications.

One surprisingly high RR belongs to {{% game 399088 %}}UNO: Show 'Em No Mercy{{% /game %}}: 24 out of the 31 threads (RR: 77%) are about the rules. I don't know what's more surprising: that the 'geeks take such an interest in an UNO variant at all, or how much they seem to struggle with its rules.

The highest RR amongst the highly rated games (ranked amongst the top 1000 games) is that of {{% game 408180 %}}Shackleton Base{{% /game %}} at 69%. When looking at very popular games (more than 10k ratings), we find another unexpected title in this field: {{% game 234190 %}}Unstable Unicorns{{% /game %}} at a whopping 64%. Apparently players really struggle with *neighing* — and now I feel like I need to play the game just to find out what that means. 🦄


## Low RR: when rules barely show up

The other extreme — extremely low RRs — is dominated by games without any rules questions. WEM already mentioned one example ({{% game 318977 %}}MicroMacro{{% /game %}}, which is also the highest ranked and most popular game with such a low RR), but there is one game with an even lower RR after smoothing: {{% game 155250 %}}TseuQuesT{{% /game %}}. Of its 221 threads, not a single one deals with rules questions. What sounds like a great achievement is actually quite the opposite: almost all that forum chatter is about its unfulfilled crowdfunding campaign — a typical Kickstarter drama. Note: treat extreme RRs with caution.

Most other games with low RR are fairly simple party or storytelling games, but there are also war games without rules questions (who would've thought?!), e.g., {{% game 36241 %}}Israeli Independence: The First Arab-Israeli War{{% /game %}} (0 rules questions out of 35 threads).


## A quick intuition for smoothing

Low RRs are where smoothing matters most. While said war game {{% game 36241 %}}Israeli Independence{{% /game %}} doesn't have a single rules question, its (smoothed) RR is still (0 + 0.5) / (35 + 1) = 1.4%. So there are some games with more rules threads, but lower RR. Take, for instance, the classic party game {{% game 74 %}}Apples to Apples{{% /game %}}: 2 out of 200 threads deal with rules, for an RR of (2 + 0.5) / (200 + 1) = 1.2%. This can look counterintuitive, but that’s the point: we distrust ratios based on tiny samples.


# RR vs complexity

Readers of this blog will be familiar with BGG's *complexity* (or *weight*) rating: a number between 1 (*light*) and 5 (*heavy*) based on user votes. It’s an imperfect measure, but it's still an interesting and widely quoted data point to characterise a game.

For this article, the intuition is simple: heavier games should generate more rules questions. Designers sometimes talk about a game’s complexity budget — depending on the intended audience, you can “spend” complexity on more mechanisms, more edge cases and more interactions. The more moving parts players have to keep straight, the more clarifications they may need.


## The trend: heavier games, more rules threads

Let's visualise this:

{{% bokeh "rules_ratio_vs_complexity.json" %}}

Every dot represents a game, positioned by its complexity (x-axis) and RR (y-axis). Games with more ratings will be larger, while the colour encodes the game type. This is an interactive plot, so I'll invite you to explore it by hovering over the dots and finding your favourite game. (For readability, the plot only includes games in the BGG top 1000 or with ≥10k ratings.)

The trend is clear: higher complexity tends to mean higher RR — but with plenty of spread.


## WEM's RRW (and why I’m not dividing by weight)

WEM’s suggestion to account for complexity when reasoning about RR is RRW: **Rules Ratio by Weight**, i.e. RR divided by BGG weight:

\\[
  \text{RRW} = \frac{\text{RR}}{\text{complexity}}.
\\]

Taking complexity into account is exactly the right instinct — I just don’t love plain division here. BGG weight is a bounded, subjective 1–5 score; it’s useful, but it’s not a ratio scale where “4” is meaningfully “twice” a “2”. Dividing RR by weight implicitly assumes that kind of multiplicative structure, and I’d rather avoid baking that assumption into the metric.


## RRR: Residual Rules Ratio

Instead, I suggest RRR: Residual Rules Ratio. The idea is to estimate the *expected RR* of a game of a certain complexity, then compare the actual RR to this expected RR. Their difference is the RRR.

Let's take this step by step. First we need to find said expected RR for a given weight. As usual, regression is our friend: we fit a simple model to explain RR in relationship to complexity. Since RR is a fraction between 0 and 1, we'll use a logistic model. Feeding the data into your favourite statistical software yields the fitted curve for the expected RR:

\\[
  \widehat\text{RR} = \sigma(0.3381 \cdot \text{complexity} - 1.6104),
\\]

where \\(\sigma\\) is the [sigmoid function](https://en.wikipedia.org/wiki/Sigmoid_function) we most recently encountered in the context of the [Elo ratings]({{<ref "posts/elo_1/index.md">}}).


### Interpreting the fitted curve

Let’s build an intuition for what this fitted curve is saying. The model works in *odds*: for each +1 step on the BGG weight scale (say, from 2 to 3), the odds that a random forum thread is about rules are multiplied by \\(e^{0.3381} \approx 1.40\\) — about a 40% increase.

Odds aren’t everyone’s favourite unit, so here are a few concrete values of the expected RR implied by the curve:

| Complexity | Expected RR |
|:----------:|:-----------:|
| 1 (light)  | 22%         |
| 2          | 28%         |
| 3          | 36%         |
| 4          | 44%         |
| 5 (heavy)  | 52%         |

In other words: the model expects a light game to have roughly a fifth of its threads about rules, and a heavy game about half.


### From expected RR to residuals

Equipped with this baseline, we can define the **Residual Rules Ratio** (RRR):

\\[
  \text{RRR} = \text{RR} - \widehat\text{RR}.
\\]

The intuition behind RRR is that it measures how much more (or less) rules-focused forum activity a game attracts than its peers in the same “weight class”. Since both RR and \\(\widehat{\text{RR}}\\) are proportions, their difference is naturally expressed in percentage points. In a time-honoured scientific tradition, I suggest naming this unit **wem**:

> **1 wem = 1 percentage point of RRR**.

In theory, RRR ranges from −100 to +100 wem (a game can’t have less than 0% or more than 100% rules threads). In practice, values are much less extreme — and should be interpreted as a behavioural proxy, not a definitive verdict on rulebook quality.


### Above and below the line

What does this look like in practice? First, let's do the same plot as before, but with RRR instead of RR:

{{% bokeh "residual_rules_ratio_vs_complexity.json" %}}

Note how the upward trend has turned into a horizontal line. This is the same idea we used to [debias the BGG rankings]({{<ref "posts/debiased_rankings/index.md">}}).


#### High RRR

One of the dots that immediately sticks out is (again) {{% game 234190 %}}Unstable Unicorns{{% /game %}}. While it didn't have the highest RR in the plot above, it does raise a lot more rules questions than a typical light game and hence takes the somewhat unexpected lead in this plot at +39 wem RRR. Another light game with a high RRR is {{% game 1111 %}}Taboo{{% /game %}} at +33 wem. Most of the rules questions seem to be disputes about allowed or forbidden clues, which isn't your typical rules question, but then again it does show that the system has some fuzziness about it that requires interpretation, which does hit the core of RR.


#### Low RRR

On the other end of the spectrum we see the three original EXIT games which won the 2017 {{% kdj %}}Kennerspiel{{% /kdj %}} award with RRRs from -31 to -28 wem. I don't know if the rules are written so well, or if it's their real-time one-and-done nature that makes few people stop and post rules questions. {{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}} has a similarly low RRR of -28 wem. Apparently, it pays off when the rules are in the story you're experiencing.

It's also interesting to see that WEM's poster child {{% game 318977 %}}MicroMacro{{% /game %}} isn't so exceptional anymore: its RRR of -22 wem is comparable to the -21 wem of the heavyweight {{% game 120677 %}}Terra Mystica{{% /game %}}. The latter's rule clarity is even more remarkable when you remember that significant portion of its appeal is due to the asymmetric factions, which is usually a recipe for a crowded *Rules* forum.


## Leaderboards

Time to look at some top 10 lists! You can also download the [full results](rules_ratios.csv).


### Most popular games

| Game                                                     | RR                | RRW             | RRR     |
|----------------------------------------------------------|-------------------|-----------------|---------|
| {{% game 13 %}}Catan{{% /game %}} (1995)                 | 16% (464 / 2916)  | 7% (16% / 2.3)  | -14 wem |
| {{% game 822 %}}Carcassonne{{% /game %}} (2000)          | 19% (539 / 2891)  | 10% (19% / 1.9) | -9 wem  |
| {{% game 30549 %}}Pandemic{{% /game %}} (2008)           | 19% (544 / 2887)  | 8% (19% / 2.4)  | -12 wem |
| {{% game 167791 %}}Terraforming Mars{{% /game %}} (2016) | 26% (1512 / 5742) | 8% (26% / 3.3)  | -11 wem |
| {{% game 266192 %}}Wingspan{{% /game %}} (2019)          | 28% (719 / 2596)  | 11% (28% / 2.5) | -4 wem  |
| {{% game 68448 %}}7 Wonders{{% /game %}} (2010)          | 24% (413 / 1703)  | 10% (24% / 2.3) | -6 wem  |
| {{% game 173346 %}}7 Wonders Duel{{% /game %}} (2015)    | 36% (321 / 896)   | 16% (36% / 2.2) | +6 wem  |
| {{% game 230802 %}}Azul{{% /game %}} (2017)              | 21% (144 / 683)   | 12% (21% / 1.8) | -6 wem  |
| {{% game 178900 %}}Codenames{{% /game %}} (2015)         | 17% (134 / 803)   | 13% (17% / 1.3) | -7 wem  |
| {{% game 9209 %}}Ticket to Ride{{% /game %}} (2004)      | 8% (148 / 1877)   | 4% (8% / 1.8)   | -19 wem |


### Highest RRR

| Game                                                                                                     | RR              | RRW             | RRR     |
|----------------------------------------------------------------------------------------------------------|-----------------|-----------------|---------|
| {{% game 182094 %}}BANG! The Duel{{% /game %}} (2015)                                                    | 88% (87 / 99)   | 46% (88% / 1.9) | +60 wem |
| {{% game 399088 %}}UNO: Show 'Em No Mercy{{% /game %}} (2023)                                            | 77% (24 / 31)   | 50% (77% / 1.5) | +52 wem |
| {{% game 301441 %}}Drawn to Adventure{{% /game %}} (2021)                                                | 77% (57 / 74)   | 37% (77% / 2.1) | +48 wem |
| {{% game 173200 %}}Epic Spell Wars of the Battle Wizards: Rumble at Castle Tentakill{{% /game %}} (2015) | 72% (48 / 66)   | 45% (72% / 1.6) | +47 wem |
| {{% game 339302 %}}Winterhaven Woods{{% /game %}} (2022)                                                 | 72% (44 / 61)   | 46% (72% / 1.6) | +47 wem |
| {{% game 392513 %}}Mindbug: Beyond Eternity{{% /game %}} (2023)                                          | 76% (33 / 43)   | 34% (76% / 2.2) | +46 wem |
| {{% game 278120 %}}God of War: The Card Game{{% /game %}} (2019)                                         | 78% (118 / 151) | 31% (78% / 2.5) | +46 wem |
| {{% game 385833 %}}Freaky Frogs From Outaspace{{% /game %}} (2023)                                       | 75% (40 / 53)   | 35% (75% / 2.2) | +46 wem |
| {{% game 256728 %}}Raiatea{{% /game %}} (2018)                                                           | 82% (24 / 29)   | 27% (82% / 3.1) | +46 wem |
| {{% game 358812 %}}Basketboss{{% /game %}} (2022)                                                        | 73% (39 / 53)   | 38% (73% / 1.9) | +46 wem |


### Lowest RRR

| Game                                                                                         | RR           | RRW           | RRR     |
|----------------------------------------------------------------------------------------------|--------------|---------------|---------|
| {{% game 1589 %}}Star Fleet Battles{{% /game %}} (1979)                                      | 5% (4 / 98)  | 1% (5% / 4.2) | -41 wem |
| {{% game 99630 %}}Rolling Stock{{% /game %}} (2011)                                          | 3% (2 / 92)  | 1% (3% / 3.9) | -40 wem |
| {{% game 147537 %}}Malifaux (Second Edition){{% /game %}} (2013)                             | 1% (0 / 45)  | 0% (1% / 3.7) | -40 wem |
| {{% game 29663 %}}Star Fleet Battles: Captain's Edition Basic Set{{% /game %}} (1990)        | 6% (8 / 130) | 2% (6% / 4.3) | -40 wem |
| {{% game 2162 %}}Warhammer 40,000 (Third Edition){{% /game %}} (1998)                        | 4% (5 / 154) | 1% (4% / 3.5) | -36 wem |
| {{% game 345976 %}}System Gateway (fan expansion for Android: Netrunner){{% /game %}} (2021) | 3% (2 / 73)  | 1% (3% / 3.4) | -36 wem |
| {{% game 126613 %}}Warhammer 40,000 (Sixth Edition){{% /game %}} (2012)                      | 4% (1 / 33)  | 1% (4% / 3.5) | -35 wem |
| {{% game 299371 %}}The Emerald Flame{{% /game %}} (2021)                                     | 4% (2 / 55)  | 1% (4% / 3.5) | -35 wem |
| {{% game 12166 %}}Funkenschlag{{% /game %}} (2001)                                           | 6% (2 / 39)  | 2% (6% / 3.6) | -34 wem |
| {{% game 4154 %}}Yu-Gi-Oh! Trading Card Game{{% /game %}} (1999)                             | 1% (0 / 46)  | 0% (1% / 2.9) | -33 wem |


# A proxy, not a verdict

Does it mean anything? Perhaps not as a definitive quality metric, but it's a fascinating proxy for *game clarity*. A heavyweight like {{% game 120677 %}}Terra Mystica{{% /game %}} (-21 wem) sitting well below the regression line suggests its rules, despite asymmetric factions and depth, are remarkably coherent. Conversely, a light game like {{% game 234190 %}}Unstable Unicorns{{% /game %}} (+39 wem) has a high "rulebook debt" — it triggers far more rules questions than other games in its weight class.

I hope WEM will be proud of how seriously I took his advice to geek out about his RR. It might be a toy metric, but I certainly found it very interesting to dive deep. Let's just hope nobody starts "ratio-bombing" BGG threads to mess with the stats! 😅


# Appendix: Methodology


## Data sources

Forum thread counts come from scraped BGG forum listings: for each game we have the number of threads per forum section (e.g. *Rules*, *Strategy*, *Sessions*). Only forums titled *Rules* are counted as rules threads. (Note: almost all games have exactly 10 standard subforums, but a handful — like {{% game 3076 %}}Puerto Rico{{% /game %}} — have special additional forums. Have fun finding them all! 😎)


## Inclusion criteria

A game is included only if it has at least 250 ratings, a non-null BGG complexity, and at least 25 total forum threads. Publication year is restricted to 1950–present. Compilations are excluded. The criteria were chose to obtain a large and representative dataset without too much noise or anomalies.


## Regression model

The expected RR for a given complexity is estimated with a binomial (logistic) GLM: the response is the smoothed RR and the single predictor is BGG complexity. Observations are weighted by the number of ratings so that games with more ratings (and thus more stable RR estimates) have greater influence. The fitted model gives the expected RR curve; the residual (actual RR minus fitted RR) is the RRR in percentage points (wem).


## Visualisation

The scatter plots show only games that are either in the BGG top 1000 by rank or have at least 10,000 ratings.


[^fediverse]: Come for the board game news, stay for their policy of [not tracking users](https://www.wericmartin.com/board-game-beat-policies/) and their [Fediverse first](https://www.wericmartin.com/federated-social-media-video/) approach. 🤓
[^threads]: WEM mentions forum posts in his article, but from the screenshot and numbers it's evident he's using threads. I think this is the correct choice for what we're interested in: every distinct rules question typically goes into its own thread, and we want to know how many rules questions a given game triggers, not how many posts it takes to resolve them.
[^ratio]: Ackshually… 🤓 Calling this metric a "ratio" isn't technically wrong, but "share", "proportion" or "fraction" would be more accurate. WEM told us to geek out, so please indulge me in this little pedantry.
[^3b1b]: If you want to learn more about this technique, I highly recommend the always excellent Grant Sanderson and his [3blue1brown video](https://youtu.be/8idr1WZ1A7Q) on the topic.
