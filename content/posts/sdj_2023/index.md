---
title: Spiel des Jahres 2023 predictions
slug: spiel-des-jahres-2023-predictions
author: Markus Shepherd
type: post
date: 2023-05-19T00:00:00+03:00
tags:
  - SdJ
  - SdJ 2023
  - Spiel des Jahres
  - Spiel des Jahres 2023
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Kennerspiel des Jahres 2023
  - Game of the Year
  - Germany
  - Predictions
  - Spiel des Jahres predictions
  - Spiel des Jahres 2023 predictions
  - SdJ predictions
  - Kennerspiel predictions
  - Kennerspiel des Jahres predictions
  - Kennerspiel des Jahres 2023 predictions
---

{{< img src="sdj-all" size="x300" alt="Spiel des Jahres" >}}

{{% sdj %}}Spiel des Jahres 2023{{% /sdj %}} is around the corner! (Has it really been a year already since we last spoke with each other? 😅) We're blessed with another strong year full of wonderful games that all compete for the most prestigious awards in board gaming. As in [the]({{<ref "posts/sdj_2020/index.md">}}) [previous]({{<ref "posts/sdj_2021/index.md">}}) [years]({{<ref "posts/sdj_2022/index.md">}}), I'll try to predict what games have the best shot at ending up on the longlist (aka *recommendations*) and the shortlist (aka *nominations*) when the jury announces their picks on May 22nd.

Even more so than in previous years, I didn't have much time (thanks, kids 👨‍👩‍👧‍👧), so I've mostly used the same algorithmic approach as last year. First, I took all eligible[^eligible] games and separated them into two lists: one for {{% sdj / %}} and one for {{% kdj / %}}, depending on their [{{% kdj %}}Kennerspiel{{% /kdj %}} score]({{<ref "posts/kennerspiel/index.md">}}).[^kennerspiel] Then I ranked those games in a couple of different ways, and finally combined those into the final result:

* Recommend.Games [recommendation algorithm](https://recommend.games/#/?for=S_d_J&yearMin=2021&yearMax=2022&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (50% ranking, 25% score). This has proven to be a powerful and reliable method to capture the jury's taste, but it's slow to recommend new games with few ratings.
* {{% sdj / %}} probability (10%). Similar to the model that calculates the {{% kdj %}}Kennerspiel{{% /kdj %}} score, I've trained a model that tries to predict a game's chances to end up on the jury's longlist. This is particularly designed to unearth candidates with few votes, but it's still rudimentary at this point.
* Average BoardGameGeek rating (5%). Let the gamers speak! In order to give new games a chance, we'll take a look at the simple average rating.
* Geek score (aka [Bayesian average]({{<ref "posts/reverse_engineer_bgg/index.md">}}), 5%). This score starts out at 5.5, and gets closer to the actual average the more ratings come in. It's more reliable, but also strongly favours games that have been around for longer and hence gathered more ratings.
* Recommend.Games ranking (5%). We introduced a new default ranking on R.G a couple of months ago, which seems to pick up new games shooting up the hotness a little faster than on BGG, so let's give it a shot as part of these predictions. 🤓

You can find the [detailed analysis here](predictions.py) and [complete results here](predictions.csv). But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2023{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2023{{% /sdj %}}

{{< img src="sdj-2022" size="x300" alt="Spiel des Jahres 2023" >}}


## #1: {{% game 353545 %}}Next Station: London{{% /game %}}

*1–4 players, 25–30 minutes, 8+ years, light (1.4), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="353545" size="x300" alt="Next Station: London" >}}

Draw tube lines to cross the Thames and connect London.


## #2: {{% game 364073 %}}Splendor Duel{{% /game %}}

*2 players, 30 minutes, 10+ years, medium light (2.0), 70% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="364073" size="x300" alt="Splendor Duel" >}}

Renaissance merchants go head to head to please nobility.


## #3: {{% game 354729 %}}Wonder Woods{{% /game %}}

*2–5 players, 20–25 minutes, 8+ years, light (1.2), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="354729" size="x300" alt="Wonder Woods" >}}

Use bluff and deduction in order to find the best mushroom spots.


## #4: {{% game 297658 %}}[kosmopoli:t]{{% /game %}}

*4–8 players, 6 minutes, 10+ years, light (1.3), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="297658" size="x300" alt="[kosmopoli:t]" >}}

Cooperative Kitchen Work serving client from all over the world.


## #5: {{% game 357563 %}}Akropolis{{% /game %}}

*2–4 players, 20–30 minutes, 8+ years, medium light (1.8), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="357563" size="x300" alt="Akropolis" >}}

Build your Greek city on multiple levels to keep your districts perfectly placed.


## #6: {{% game 356742 %}}KuZOOkA{{% /game %}}

*2–6 players, 30–45 minutes, 8+ years, medium light (2.0), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="356742" size="x300" alt="KuZOOkA" >}}

Discover the most promising escape option and break out of the zoo.


## #7: {{% game 367047 %}}Caldera Park{{% /game %}}

*1–4 players, 30–40 minutes, 10+ years, medium light (2.0), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="367047" size="x300" alt="Caldera Park" >}}

Take care of animals in your park by forming big herds and avoiding bad weather.


## #8: {{% game 324914 %}}Inside Job{{% /game %}}

*2–5 players, 20–30 minutes, 10+ years, medium light (1.7), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="324914" size="x300" alt="Inside Job" >}}

Agents work together to complete missions and gather intel but who's "The Insider"?


## #9: {{% game 266830 %}}QE{{% /game %}}

*3–5 players, 45 minutes, 8+ years, medium light (1.6), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="266830" size="x300" alt="QE" >}}

Bid ANYTHING to bail out companies, but just don’t bid the MOST!


## #10: {{% game 370591 %}}Dorfromantik: The Board Game{{% /game %}}

*1–6 players, 30–60 minutes, 8+ years, medium light (1.7), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="370591" size="x300" alt="Dorfromantik: The Board Game" >}}

Experience the peaceful and relaxed atmosphere of the video game on your table.


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2023{{% /kdj %}}

{{< img src="ksdj-2022" size="x300" alt="Kennerspiel des Jahres 2023" >}}


## #1: {{% game 364186 %}}Terra Nova{{% /game %}}

*2–4 players, 60–90 minutes, 12+ years, medium (2.8), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="364186" size="x300" alt="Terra Nova" >}}

Control one of ten asymmetric factions in a streamlined version of Terra Mystica.


## #2: {{% game 177478 %}}IKI{{% /game %}}

*2–4 players, 60–90 minutes, 14+ years, medium (3.0), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="177478" size="x300" alt="IKI" >}}

Hire artisans, set them up in the market and acquire prestige in feudal Japan.


## #3: {{% game 336986 %}}Flamecraft{{% /game %}}

*1–5 players, 60 minutes, 10+ years, medium light (2.2), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="336986" size="x300" alt="Flamecraft" >}}

In a magical realm a village awakes, and artisan dragons make coffee and cakes!


## #4: {{% game 362452 %}}Atiwa{{% /game %}}

*1–4 players, 30–120 minutes, 12+ years, medium (2.7), 99% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="362452" size="x300" alt="Atiwa" >}}

Choose your actions carefully as you balance the needs of the community and nature.


## #5: {{% game 351913 %}}Tiletum{{% /game %}}

*1–4 players, 60–100 minutes, 14+ years, medium (3.4), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="351913" size="x300" alt="Tiletum" >}}

Use dice for resources and actions to gain riches in the Renaissance.


## #6: {{% game 369880 %}}Beer & Bread{{% /game %}}

*2 players, 30–45 minutes, 10+ years, medium light (2.4), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="369880" size="x300" alt="Beer & Bread" >}}

Two villages face off in the traditions of brewing beer and baking bread.


## #7: {{% game 350933 %}}The Guild of Merchant Explorers{{% /game %}}

*1–4 players, 45 minutes, 14+ years, medium light (2.1), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="350933" size="x300" alt="The Guild of Merchant Explorers" >}}

Explore strange lands, establish trade routes, and search for treasure.


## #8: {{% game 335275 %}}Whirling Witchcraft{{% /game %}}

*2–5 players, 15–30 minutes, 14+ years, medium light (1.8), 98% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="335275" size="x300" alt="Whirling Witchcraft" >}}

Use your recipes to generate ingredients and overflow your opponent's cauldron.


## #9: {{% game 339906 %}}The Hunger{{% /game %}}

*2–6 players, 60 minutes, 12+ years, medium light (2.3), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="339906" size="x300" alt="The Hunger" >}}

As a vampire, you want to hunt humans, but you must return home before sunrise…


## #10: {{% game 293835 %}}Oltréé{{% /game %}}

*2–4 players, 60–120 minutes, 8+ years, medium light (2.4), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="293835" size="x300" alt="Oltréé" >}}

Rangers help local communities and defend their Kingdom in order to restore hope.


# My two cents

TODO


# Honourable mentions

This is always the section where I squeeze in a few more title in order to increase my chance of covering the whole list. There's plenty of strong games I could mention, but I'll restrict myself to two additional candidates for {{% sdj / %}} that the algorithm just wouldn't quite pick up:

* TODO


# Conclusion

TODO


[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2022 and March 2023 into German retail. Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
[^kennerspiel]: I'll trust the algorithm and the scores it outputs blindly. As every year, it'll be an interesting validation of the Kennerspiel score to see whether the jury agrees or not.
