---
title: What makes a Kennerspiel?
# slug: and-the-spiel-des-jahres-2020-goes-to
author: Markus Shepherd
type: post
date: 2021-02-19T12:00:00+02:00
tags:
  - SdJ
  - Spiel des Jahres
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Game of the Year
  - Germany
  - Logistic regression
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

| Game                                                      | Year | Complexity | Age | Award                    | 🤔 |
|:----------------------------------------------------------|:----:|-----------:|----:|:------------------------:|:-:|
| {{% game 125618 %}}Libertalia{{% /game %}}                | 2013 |        2.2 | 14+ | {{% sdj %}}S{{% /sdj %}} | ❌ |
| {{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}} | 2018 |        1.9 | 10+ | {{% kdj %}}K{{% /kdj %}} | ❌ |
| {{% game 244522 %}}That's Pretty Clever!{{% /game %}}     | 2018 |        1.9 |  8+ | {{% kdj %}}K{{% /kdj %}} | ❌ |
| {{% game 263918 %}}Cartographers{{% /game %}}             | 2020 |        1.9 | 10+ | {{% kdj %}}K{{% /kdj %}} | ❌ |
| {{% game 284083 %}}The Crew{{% /game %}}                  | 2020 |        2.0 | 10+ | {{% kdj %}}K{{% /kdj %}} | ❌ |
| {{% game 295486 %}}My City{{% /game %}}                   | 2020 |        2.1 | 10+ | {{% sdj %}}S{{% /sdj %}} | ❌ |
| {{% game 223953 %}}Kitchen Rush{{% /game %}}              | 2020 |        2.2 | 12+ | {{% sdj %}}S{{% /sdj %}} | ❌ |

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

| Game                                                                | Year | Award                    | Kennerspiel? | 🤔 |
|:--------------------------------------------------------------------|:----:|:------------------------:|-------------:|:-:|
| {{% game 125618 %}}Libertalia{{% /game %}}                          | 2013 | {{% sdj %}}S{{% /sdj %}} |        91.2% | 🤬 |
| {{% game 244521 %}}The Quacks of Quedlinburg{{% /game %}}           | 2018 | {{% kdj %}}K{{% /kdj %}} |        65.3% | ✅ |
| {{% game 244522 %}}That's Pretty Clever!{{% /game %}}               | 2018 | {{% kdj %}}K{{% /kdj %}} |        51.8% | ✅ |
| {{% game 263918 %}}Cartographers{{% /game %}}                       | 2020 | {{% kdj %}}K{{% /kdj %}} |        84.7% | ✅ |
| {{% game 284083 %}}The Crew: The Quest for Planet Nine{{% /game %}} | 2020 | {{% kdj %}}K{{% /kdj %}} |        41.7% | 😕 |
| {{% game 295486 %}}My City{{% /game %}}                             | 2020 | {{% sdj %}}S{{% /sdj %}} |        36.0% | ✅ |
| {{% game 223953 %}}Kitchen Rush{{% /game %}}                        | 2020 | {{% sdj %}}S{{% /sdj %}} |        37.4% | ✅ |

This picture certainly has improved, and we're even classifying games like {{% game 244522 %}}That's Pretty Clever!{{% /game %}} (just about) and {{% game 223953 %}}Kitchen Rush{{% /game %}} right that caused us a lot of headaches before. However, {{% game 284083 %}}The Crew{{% /game %}} still eludes correct classification, and {{% game 125618 %}}Libertalia{{% /game %}} is so far off that I'd argue the jury simply got that one wrong…

# But how does the model work?

Our model takes the different features of a game as described above as input, multiplies each with a certain weight it learned by looking at all the games from previous year, sums those values up, and then yields a prediction in the form of a confidence (0–100%) score.

To make things a little more concret, let's look at the ten most important features and how they impact the outcome:

{{< img src="shap_summary" alt="Summary of feature importance" >}}

As you can see, the *complexity* is the most important feature: the higher the value (blue = 1, red = 5), the higher our confidence that the game in question is a {{% kdj %}}Kennerspiel{{% /kdj %}}. This makes a lot of sense. Likewise, the next features are equally intuitive: the higher *play time* and *minimum age* are, the more likely it is we're dealing with a games for experts. And of course, in a way *strategy games* are much more frequently found in the {{% kdj %}}Kennerspiel{{% /kdj %}} column. (Here, red means strategy game, blue means not).

Somewhat more confusing is the player count though. Pay close attention to whether a game is playable with five or six players. Again, red means that game is playable with that head count, while blue means it is not. So a game that is playable with five players is *more* likely to be a {{% kdj %}}Kennerspiel{{% /kdj %}}, while a game for six players is *less* likely. This certainly is a little confusing, and might well be an artifact of our small sample size. Still, there's a system to this madness: whilst the vast majority of games accomodate three and four players, {{% sdj %}}Spiel{{% /sdj %}} candidates often either stop at that count to keep components and costs down, or are for a much larger audience anyways and really shine with six, eight, or even more players. A {{% kdj %}}Kennerspiel{{% /kdj %}} on the other hand can be a little more luxurious, and hence often includes components for a fifth player by default, but their more strategic nature limits the scalability beyond that point.

Lastly, we have some mechanics in the top 10. While it's probably no surprise that solo modes are more common amongst more strategic games, the other mechanics are less intuitive. As it turns out, rolling dice is more prevalent in a {{% kdj %}}Kennerspiel{{% /kdj %}}, whilst hand management and worker placement are indicative of a lighter {{% sdj %}}Spiel{{% /sdj %}}. But of course, all those different features and weights interact with each other in a little more subtle ways and often balance each other out.

Let's make things more concret and visualise how our model scored some of those difficult to classify games above, starting from {{% game 295486 %}}My City{{% /game %}}:

{{< img src="shap_295486" alt="My City force plot" >}}

This so called force plot shows how some values push the score up, while some pull it down. In this case, complexity, strategy, and player count push the score towards {{% kdj %}}Kennerspiel{{% /kdj %}}, while a tile laying game playable in 30 minutes pull it towards {{% sdj %}}Spiel{{% /sdj %}}. In the sum, our model and the jury agree: this game falls on the red side of the line.

{{< img src="shap_244522" alt="That's Pretty Clever! force plot" >}}

We contrast this with {{% game 244522 %}}That's Pretty Clever!{{% /game %}} Again, its play time of 30 minutes with players from 8 years old smell like a lighter game, but soloable dice rolling clearly push the needle (very narrowly) over the line of a {{% kdj %}}Kennerspiel{{% /kdj %}}.

In the end, our evidence is a little thin – even after a decade of {{% kdj %}}Kennerspiel{{% /kdj %}} winners and nominees, the patterns aren't very clear, and of course the jury's fickle opinion might drift over time as well. So while I'm pretty confident in the predictions our model makes, they still need to be taken with a grain of salt.

"Not so fast!", you might say. "Aren't you simply overfitting here?" Why, yes, you're right. The dataset is so small that there's a high risk of fine tuning the model too much for the data we're seeing. And of course, it's **bad bad bad** to assess your model's performance with items it was trained on – that's just cheating. So let's test the model on some games it hadn't seen yet!

# What about old games?

Pre-2011 {{% sdj / %}} winners and nominees make a marvellous test set for this model. A lot of those games would be considered a {{% kdj %}}Kennerspiel{{% /kdj %}} by today's standards, so let's find out which ones.

Again, we'll start with the simple model that takes the two input variables *complexity* and *minimum age*. We can then plot those 70 games and check what side of the line they fall on:

{{% bokeh "complexity_vs_min_age_before_2011.json" %}}

We observe a pretty similar spread along those two axes as in the plot above, so apparently the jury covered games of a broad variety already before 2011, but under the single {{% sdj /%}} brand.

Let's dive deeper and check what {{% kdj %}}Kennerspiel{{% /kdj %}} scores our more complex model assigns to some of the more noteworthy {{% sdj / %}} winners and nominees:

| Game                                                                 | Year | Kennerspiel? |
|:---------------------------------------------------------------------|:----:|-------------:|
| {{% game 93 %}}El Grande{{% /game %}}                                | 1996 |       100.0% |
| {{% game 2511 %}}Sherlock Holmes Consulting Detective{{% /game %}}   | 1985 |        99.9% |
| {{% game 13 %}}Catan{{% /game %}}                                    | 1995 |        99.7% |
| {{% game 54 %}}Tikal{{% /game %}}                                    | 1999 |        96.4% |
| {{% game 36218 %}}Dominion{{% /game %}}                              | 2009 |        87.2% |
| {{% game 21790 %}}Thurn and Taxis{{% /game %}}                       | 2006 |        77.0% |
| {{% game 30549 %}}Pandemic{{% /game %}}                              | 2009 |        69.4% |
| {{% game 6249 %}}Alhambra{{% /game %}}                               | 2003 |        24.8% |
| {{% game 9209 %}}Ticket to Ride{{% /game %}}                         | 2004 |        12.0% |
| {{% game 822 %}}Carcassonne{{% /game %}}                             | 2001 |         8.6% |
| {{% game 39856 %}}Dixit{{% /game %}}                                 | 2010 |         0.1% |

<!-- | {{% game 3076 %}}Puerto Rico{{% /game %}}                            | 2002 |     100.0% |
| {{% game 34635 %}}Stone Age{{% /game %}}                             | 2008 |      99.5% |
| {{% game 88 %}}Torres{{% /game %}}                                   | 2000 |      97.9% |
| {{% game 478 %}}Citadels{{% /game %}}                                | 2000 |      95.3% |
| {{% game 9217 %}}Saint Petersburg{{% /game %}}                       | 2004 |      94.5% |
| {{% game 37380 %}}Roll Through the Ages: The Bronze Age{{% /game %}} | 2010 |      90.7% |
| {{% game 30869 %}}Thebes{{% /game %}}                                | 2007 |      21.5% |
| {{% game 9674 %}}Ingenious{{% /game %}}                              | 2004 |       5.4% | -->

On the one hand, it's weird to see games like {{% game 13 %}}Catan{{% /game %}} and {{% game 30549 %}}Pandemic{{% /game %}} so firmly in the {{% kdj %}}Kennerspiel{{% /kdj %}} column when they are considered some of the quintessential modern gateway games. On the other hand, their complexity clearly does exceed by far what the jury demands of the average gamer these days. It's also worth observing that {{% game 13 %}}Catan{{% /game %}} did pave the way for some pretty complex games in the second half of the 90s, when the *euro revolution* was in full swing.

As far as validating the model goes: I'd agree with every single one of the model's assessments, though I'm a little surprised that {{% game 478 %}}Citadels{{% /game %}} got a score of 95.3%. I see good reasons for putting this one into the {{% kdj %}}Kennerspiel{{% /kdj %}} camp, but would do so with far more uncertainty.

Overall, according to our model, **9 out of 32** {{% sdj / %}} winners between 1979 and 2010 should really be considered a {{% kdj %}}Kennerspiel{{% /kdj %}} now. I wonder how many people trusted the red meeple, bought what they thought to be a welcoming game, only to get frustrated by 12 densely filled A4 pages[^elgrande] of {{% game 93 %}}El Grande{{% /game %}} rules? Or did people really have much longer attention spans in the pre-smartphone era? We might never know…

<!-- {{< img src="shap_30549" alt="Pandemic force plot" >}}

{{< img src="shap_6249" alt="Alhambra force plot" >}} -->

# (Kenner-)Spiel des Jahres 2021

I'll send you off with a teaser for {{% sdj %}}Spiel des Jahres 2021{{% /sdj %}}. I've taken some of the [hottest contenders for the 2021 awards](https://recommend.games/#/?for=S_d_J&yearMin=2020&yearMax=2021&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (as of the time of writing), and sort them by their {{% kdj %}}Kennerspiel{{% /kdj %}} score for your convenience.

| Game                                                                   | Kennerspiel? |
|:-----------------------------------------------------------------------|-------------:|
| {{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}           |       100.0% |
| {{% game 318553 %}}Rajas of the Ganges: The Dice Charmers{{% /game %}} |        80.5% |
| {{% game 300531 %}}Paleo{{% /game %}}                                  |        77.5% |
| {{% game 300877 %}}New York Zoo{{% /game %}}                           |        63.0% |
| {{% game 300327 %}}The Castles of Tuscany{{% /game %}}                 |        39.3% |
| {{% game 297895 %}}Divvy Dice{{% /game %}}                             |         4.7% |
| {{% game 301767 %}}Mysterium Park{{% /game %}}                         |         2.8% |
| {{% game 318977 %}}MicroMacro: Crime City{{% /game %}}                 |         1.4% |
| {{% game 299171 %}}The Key: Raub in der Cliffrock Villa{{% /game %}}   |         0.9% |
| {{% game 319114 %}}Krazy Pix{{% /game %}}                              |         0.8% |

I think this makes a pretty interesting early list of six candidates for {{% sdj %}}Spiel des Jahres 2021{{% /sdj %}} and four candidates for {{% kdj %}}Kennerspiel des Jahres 2021{{% /kdj %}}, don't you think? Stay tuned!

[^kennerspiel]: In 2011, there was no separate recommendation list for the two awards, so I only included the nominees for 2011. I also added the special award winners {{% game 18602 %}}Caylus{{% /game %}}, {{% game 31260 %}}Agricola{{% /game %}}, {{% game 43528 %}}World Without End{{% /game %}}, and {{% game 221107 %}}Pandemic Legacy: Season 2{{% /game %}} to the {{% kdj %}}Kennerspiel{{% /kdj %}} list.
[^logistic]: Using logistic regression with F1–score as target metric. Other definitions of "best line" of course might yield different results.
[^elgrande]: Yes, I did pull out my old copy and counted. You're welcome. 🤓