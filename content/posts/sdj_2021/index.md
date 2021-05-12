---
title: Spiel des Jahres 2021 predictions
slug: spiel-des-jahres-2021-predictions
author: Markus Shepherd
type: post
date: 2021-05-09T10:00:00+03:00
tags:
  - SdJ
  - SdJ 2021
  - Spiel des Jahres
  - Spiel des Jahres 2021
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Kennerspiel des Jahres 2021
  - Game of the Year
  - Germany
  - Predictions
  - Spiel des Jahres predictions
  - Spiel des Jahres 2021 predictions
  - SdJ predictions
  - Kennerspiel predictions
  - Kennerspiel des Jahres predictions
  - Kennerspiel des Jahres 2021 predictions
---

It's our favourite time of the year again: time for {{% sdj / %}} nominations! On Monday, May 17th, the jury will once again announce their longlist (aka recommendations) and shortlist (aka nominations) for {{% sdj / %}}, {{% kdj / %}} and {{% kindersdj %}}Kinderspiel des Jahres 2021{{% /kindersdj %}}. Just like [last year]({{<ref "posts/sdj_2020/index.md">}}), I'll try to produce a list of the most promising games to land on the longlist for {{% sdj %}}Spiel{{% /sdj %}} and {{% kdj %}}Kennerspiel{{% /sdj %}}. (I'll promise to get around to {{% kindersdj %}}Kinderspiel{{% /kindersdj %}} predictions [in a couple of years](https://twitter.com/recommend_games/status/1373396030616694785?s=20).)

Unlike last year, I won't use hard filters though to distinguish between {{% sdj %}}red{{% /sdj %}} and {{% kdj %}}anthracite{{% /sdj %}} games, but will rely on the **{{% kdj %}}Kennerspiel{{% /sdj %}} score** I developed [a couple of months back]({{<ref "posts/kennerspiel/index.md">}}). This model tries to predict if a game is a {{% kdj %}}Kennerspiel{{% /sdj %}} or not based on some key features, like complexity, play time, age recommendations and game type. The jury's decision this year what list a game belongs to will be the first actual test for that model too, so let's hope it actually made sense! 🤞

Another difference is that I took an entirely algorithmic approach. That is, I do not follow my own taste or gut feeling, but I let the numbers talk. First, I took all eligible games[^eligible] and separated them into two lists: one for {{% sdj / %}} and one for {{% kdj / %}}, depending on their {{% kdj %}}Kennerspiel{{% /sdj %}} score. Then I ranked those games in a couple of different ways, and finally combined those into the final result:

* Sorted by the Recommend.Games [recommendation algorithm](https://recommend.games/#/?for=S_d_J&yearMin=2020&yearMax=2021&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (90%). This has proven to be a powerful and reliable method to capture the jury's taste, but it's slow to recommend new games with few ratings.
* {{% sdj / %}} probability (5%). Similar to the model that calculates the {{% kdj %}}Kennerspiel{{% /sdj %}} score, I've trained a model that tries to predict a game's chances to end up on the jury's longlist. This is particularly designed to unearth candidates with few votes, but it's still rudimentary at this point.
* Average BoardGameGeek rating (2.5%). Let the gamers speak! In order to give new games a chance, we'll take a look at the simple average rating.
* Geek score (aka [Bayesian average]({{<ref "posts/reverse_engineer_bgg/index.md">}}), 2.5%). This score starts out at 5.5, and gets closer to the actual average the more ratings come in. It's more reliable, but also strongly favours games that have been around for longer and hence gathered more ratings.

You can find the detailed analysis [here](predictions.py). But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2021{{% /sdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2021{{% /sdj %}}

<!-- TODO update logo -->

{{< img src="sdj-2021" size="x300" alt="Spiel des Jahres 2021" >}}

<!-- TODO data for each game: designers, player count, play time, age, complexity, Kennerspiel score -->

## #1: {{% game 266524 %}}PARKS{{% /game %}}

*1–5 players, 30–60 minutes, 10+ years, medium light (2.2), 88% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="266524" size="x300" alt="PARKS" >}}

{{% game 266524 %}}PARKS{{% /game %}}


## #2: {{% game 318977 %}}MicroMacro: Crime City{{% /game %}}

*1–4 players, 15–45 minutes, 10+ years, light (1.1), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="318977" size="x300" alt="MicroMacro: Crime City" >}}

{{% game 318977 %}}MicroMacro: Crime City{{% /game %}}


## #3: {{% game 276498 %}}Paris: La Cité de la Lumière{{% /game %}}

*2 players, 30 minutes, 8+ years, medium light (2.1), 96% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="276498" size="x300" alt="Paris: La Cité de la Lumière" >}}

{{% game 276498 %}}Paris: La Cité de la Lumière{{% /game %}}


## #4: {{% game 283864 %}}Trails of Tucana{{% /game %}}

*1–8 players, 15 minutes, 8+ years, light (1.3), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="283864" size="x300" alt="Trails of Tucana" >}}

{{% game 283864 %}}Trails of Tucana{{% /game %}}


## #5: {{% game 223040 %}}Fantasy Realms{{% /game %}}

*3–6 players, 20 minutes, 14+ years, medium light (1.7), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="223040" size="x300" alt="Fantasy Realms" >}}

{{% game 223040 %}}Fantasy Realms{{% /game %}}


## #6: {{% game 274960 %}}Point Salad{{% /game %}}

*2–6 players, 15–30 minutes, 8+ years, light (1.2), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="274960" size="x300" alt="Point Salad" >}}

{{% game 274960 %}}Point Salad{{% /game %}}


## #7: {{% game 256788 %}}Detective Club{{% /game %}}

*4–8 players, 45 minutes, 8+ years, light (1.2), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="256788" size="x300" alt="Detective Club" >}}

{{% game 256788 %}}Detective Club{{% /game %}}


## #8: {{% game 300877 %}}New York Zoo{{% /game %}}

*1–5 players, 30–60 minutes, 10+ years, medium light (2.0), 96% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300877" size="x300" alt="New York Zoo" >}}

{{% game 300877 %}}New York Zoo{{% /game %}}


## #9: {{% game 326494 %}}The Adventures of Robin Hood{{% /game %}}

*2–4 players, 60 minutes, 10+ years, medium light (1.7), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="326494" size="x300" alt="The Adventures of Robin Hood" >}}

{{% game 326494 %}}The Adventures of Robin Hood{{% /game %}}


## #10: {{% game 295948 %}}Aqualin{{% /game %}}

*2 players, 20 minutes, 10+ years, medium light (1.8), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="295948" size="x300" alt="Aqualin" >}}

{{% game 295948 %}}Aqualin{{% /game %}}


## #11: {{% game 300327 %}}The Castles of Tuscany{{% /game %}}

*2–4 players, 45–60 minutes, 10+ years, medium light (2.2), 89% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300327" size="x300" alt="The Castles of Tuscany" >}}

{{% game 300327 %}}The Castles of Tuscany{{% /game %}}


## #12: {{% game 299172 %}}The Key: Murder at the Oakdale Club{{% /game %}}

*1–4 players, 15–20 minutes, 8+ years, medium light (2.0), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="299172" size="x300" alt="The Key: Murder at the Oakdale Club" >}}

{{% game 299172 %}}The Key: Murder at the Oakdale Club{{% /game %}}


## My two cents

Alright, that's what the algorithms say. But just like last year, I'd like to let my guts have some say as well. These are the three games I consider having the best shot at ending up on the jury's shortlist:

* {{% game 318977 %}}MicroMacro: Crime City{{% /game %}}
* {{% game 326494 %}}The Adventures of Robin Hood{{% /game %}}
* {{% game 300327 %}}The Castles of Tuscany{{% /game %}}


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2021{{% /kdj %}}

<!-- TODO update logo -->

{{< img src="ksdj-2021" size="x300" alt="Kennerspiel des Jahres 2021" >}}


## #1: {{% game 281259 %}}The Isle of Cats{{% /game %}}

*1–4 players, 60–90 minutes, 8+ years, medium light (2.3), 94% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="281259" size="x300" alt="The Isle of Cats" >}}

{{% game 281259 %}}The Isle of Cats{{% /game %}}


## #2: {{% game 312484 %}}Lost Ruins of Arnak{{% /game %}}

*1–4 players, 30–120 minutes, 12+ years, medium (2.8), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="312484" size="x300" alt="Lost Ruins of Arnak" >}}

{{% game 312484 %}}Lost Ruins of Arnak{{% /game %}}


## #3: {{% game 283155 %}}Calico{{% /game %}}

*1–4 players, 30–45 minutes, 13+ years, medium light (2.2), 62% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="283155" size="x300" alt="Calico" >}}

{{% game 283155 %}}Calico{{% /game %}}


## #4: {{% game 224517 %}}Brass: Birmingham{{% /game %}}

*2–4 players, 60–120 minutes, 14+ years, medium heavy (3.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="224517" size="x300" alt="Brass: Birmingham" >}}

{{% game 224517 %}}Brass: Birmingham{{% /game %}}


## #5: {{% game 317311 %}}Switch & Signal{{% /game %}}

*2–4 players, 45 minutes, 10+ years, medium light (2.2), 83% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="317311" size="x300" alt="Switch & Signal" >}}

{{% game 317311 %}}Switch & Signal{{% /game %}}


## #6: {{% game 300531 %}}Paleo{{% /game %}}

*1–4 players, 45–60 minutes, 10+ years, medium (2.6), 88% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="300531" size="x300" alt="Paleo" >}}

{{% game 300531 %}}Paleo{{% /game %}}


## #7: {{% game 293014 %}}Nidavellir{{% /game %}}

*2–5 players, 30–60 minutes, 10+ years, medium light (2.2), 96% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="293014" size="x300" alt="Nidavellir" >}}

{{% game 293014 %}}Nidavellir{{% /game %}}


## #8: {{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}

*1–4 players, 30–120 minutes, 14+ years, medium heavy (3.6), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="291457" size="x300" alt="Gloomhaven: Jaws of the Lion" >}}

{{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}


## #9: {{% game 286096 %}}Tapestry{{% /game %}}

*1–5 players, 90–120 minutes, 12+ years, medium (2.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="286096" size="x300" alt="Tapestry" >}}

{{% game 286096 %}}Tapestry{{% /game %}}


## #10: {{% game 271324 %}}It's a Wonderful World{{% /game %}}

*1–5 players, 30–60 minutes, 14+ years, medium light (2.3), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="271324" size="x300" alt="It's a Wonderful World" >}}

{{% game 271324 %}}It's a Wonderful World{{% /game %}}


## #11: {{% game 283294 %}}Yukon Airways{{% /game %}}

*1–4 players, 60–90 minutes, 14+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="283294" size="x300" alt="Yukon Airways" >}}

{{% game 283294 %}}Yukon Airways{{% /game %}}


## #12: {{% game 282954 %}}Paris{{% /game %}}

*2–4 players, 90 minutes, 12+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="282954" size="x300" alt="Paris" >}}

{{% game 282954 %}}Paris{{% /game %}}


## My two cents

* {{% game 312484 %}}Lost Ruins of Arnak{{% /game %}}
* {{% game 300531 %}}Paleo{{% /game %}}
* {{% game 281259 %}}The Isle of Cats{{% /game %}}


# Honourable mentions


## {{% sdj / %}}

* TODO


## {{% kdj / %}}

* TODO


[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2020 and March 2021 into German retail (though because of COVID–19 hitting in March last year we might see a few latecomers this year). Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
