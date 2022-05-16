---
title: Spiel des Jahres 2022 predictions
slug: spiel-des-jahres-2022-predictions
author: Markus Shepherd
type: post
date: 2022-05-16T18:40:51+03:00
tags:
  - SdJ
  - SdJ 2022
  - Spiel des Jahres
  - Spiel des Jahres 2022
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Kennerspiel des Jahres 2022
  - Game of the Year
  - Germany
  - Predictions
  - Spiel des Jahres predictions
  - Spiel des Jahres 2022 predictions
  - SdJ predictions
  - Kennerspiel predictions
  - Kennerspiel des Jahres predictions
  - Kennerspiel des Jahres 2022 predictions
---

{{< img src="sdj-all" size="x300" alt="Spiel des Jahres" >}}

{{% sdj %}}Spiel des Jahres 2022{{% /sdj %}} is around the corner! (Has it really been a year already since we last spoke with each other? 😅) We're blessed with another strong year full of wonderful games that all compete for the most prestigious awards in board gaming. As in the [previous]({{<ref "posts/sdj_2020/index.md">}}) [years]({{<ref "posts/sdj_2021/index.md">}}), I'll try to predict what games have the best shot at ending up on the longlist (aka *recommendations*) and the shortlist (aka *nominations*) when the jury announces their picks on May 23rd.

Even more so than in previous years, I didn't have much time (thanks, kids 👨‍👩‍👧‍👧), so I've mostly used the same algorithmic approach as last year. First, I took all eligible[^eligible] games and separated them into two lists: one for {{% sdj / %}} and one for {{% kdj / %}}, depending on their [{{% kdj %}}Kennerspiel{{% /kdj %}} score]({{<ref "posts/kennerspiel/index.md">}}).[^kennerspiel] Then I ranked those games in a couple of different ways, and finally combined those into the final result:

* Recommend.Games [recommendation algorithm](https://recommend.games/#/?for=S_d_J&yearMin=2021&yearMax=2022&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (50% ranking, 25% score). This has proven to be a powerful and reliable method to capture the jury's taste, but it's slow to recommend new games with few ratings.
* {{% sdj / %}} probability (10%). Similar to the model that calculates the {{% kdj %}}Kennerspiel{{% /kdj %}} score, I've trained a model that tries to predict a game's chances to end up on the jury's longlist. This is particularly designed to unearth candidates with few votes, but it's still rudimentary at this point.
* Average BoardGameGeek rating (5%). Let the gamers speak! In order to give new games a chance, we'll take a look at the simple average rating.
* Geek score (aka [Bayesian average]({{<ref "posts/reverse_engineer_bgg/index.md">}}), 5%). This score starts out at 5.5, and gets closer to the actual average the more ratings come in. It's more reliable, but also strongly favours games that have been around for longer and hence gathered more ratings.
* Recommend.Games ranking (5%). We introduced a new default ranking on R.G a couple of months ago, which seems to pick up new games shooting up the hotness a little faster than on BGG, so let's give it a shot as part of these predictions. 🤓

You can find the [detailed analysis here](predictions.py) and [complete results here](predictions.csv). But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2022{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2022{{% /sdj %}}

{{< img src="sdj-blank" size="x300" alt="Spiel des Jahres 2022" >}}


## #1: {{% game 355483 %}}Die wandelnden Türme{{% /game %}}

*2–6 players, 30 minutes, 8+ years, medium light (2.0), 96% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="355483" size="x300" alt="Die wandelnden Türme" >}}

Well, this is something of a surprise prediction since {{% game 355483 %}}Die wandelnden Türme{{% /game %}} doesn't even have an English title yet and only a handful of ratings on BGG. There must be something about this game if the algorithm could still pick it up amongst the crowd.


## #2: {{% game 329839 %}}So Clover!{{% /game %}}

*3–6 players, 30 minutes, 10+ years, light (1.1), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="329839" size="x300" alt="So Clover!" >}}

A cooperative word–association game by publisher Repos Production, in many ways reminiscent of {{% sdj / %}} winner {{% game 254640 %}}Just One{{% /game %}}. The jury generally doesn't mind repeating themselves, so {{% game 329839 %}}So Clover!{{% /game %}} is definitely in the running.


## #3: {{% game 300905 %}}Top Ten{{% /game %}}

*4–9 players, 30 minutes, 14+ years, light (1.1), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300905" size="x300" alt="Top Ten" >}}

Another cooperative party game, light and with an immediate hook – exactly what the jury is looking for.


## #4: {{% game 327831 %}}Lost Cities: Roll & Write{{% /game %}}

*2–5 players, 30 minutes, 8+ years, light (1.1), 97% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="327831" size="x300" alt="Lost Cities: Roll & Write" >}}

This is an interesting one: While the jury completely ignored the original {{% game 50 %}}Lost Cities{{% /game %}} (now considered a classic), it did pin the main award on {{% game 34585 %}}Keltis{{% /game %}} (essentially the board game version). Will they come back to the same system for the {{% game 327831 %}}Roll & Write{{% /game %}} version?


## #5: {{% game 300753 %}}Cross Clues{{% /game %}}

*2–6 players, 5–10 minutes, 7+ years, light (1.0), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300753" size="x300" alt="Cross Clues" >}}

…and another cooperative word–association party game… I sense a pattern! 😅 Does {{% game 300753 %}}Cross Clues{{% /game %}} have what it takes to set itself apart from its competitors?


## #6: {{% game 342927 %}}Fire & Stone{{% /game %}}

*2–4 players, 45–60 minutes, 10+ years, medium light (2.0), 86% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="342927" size="x300" alt="Fire & Stone" >}}

The latest game by "Mr. {{% game 822 %}}Carcassonne{{% /game %}}", so this fact alone makes {{% game 342927 %}}Fire & Stone{{% /game %}} an interesting game to watch.


## #7: {{% game 330174 %}}Explorers{{% /game %}}

*1–4 players, 20 minutes, 8+ years, medium light (1.8), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="330174" size="x300" alt="Explorers" >}}

Phil Walker-Harding has built an impressive portfolio of award winning games over the past years, so {{% game 330174 %}}Explorers{{% /game %}} could be his next shot at winning {{% sdj / %}}.


## #8: {{% game 346703 %}}7 Wonders: Architects{{% /game %}}

*2–7 players, 25 minutes, 8+ years, light (1.4), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="346703" size="x300" alt="7 Wonders: Architects" >}}

The little sibling of the inaugural {{% kdj / %}} winner already won the 2022 As d'Or, the French equivalent of {{% sdj / %}}, so this is definitely one to watch.


## #9: {{% game 328859 %}}Hula-Hoo!{{% /game %}}

*2–6 players, 10–20 minutes, 8+ years, medium light (2.0), 95% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="328859" size="x300" alt="Hula-Hoo!" >}}

There's been many cute and/or ugly animal themed light games by Jacques Zeimet that were often well received by the jury, so {{% game 328859 %}}Hula-Hoo!{{% /game %}} could be the next in that line.


## #10: {{% game 338628 %}}TRAILS{{% /game %}}

*2–4 players, 20–40 minutes, 10+ years, medium light (1.8), 93% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="338628" size="x300" alt="TRAILS" >}}

{{% game 266524 %}}PARKS{{% /game %}} wasn't as well received in Germany as it was internationally, so maybe its successor {{% game 338628 %}}TRAILS{{% /game %}} will fare better.


## My two cents

Alrighty, so these were the top ten candidates for a recommendation as determined by our algorithm. As always, I'll add my personal best guess for the three nominees:

* {{% game 327831 %}}Lost Cities: Roll & Write{{% /game %}}
* {{% game 329839 %}}So Clover!{{% /game %}}
* {{% game 300905 %}}Top Ten{{% /game %}}


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2022{{% /kdj %}}

{{< img src="ksdj-blank" size="x300" alt="Kennerspiel des Jahres 2022" >}}


## #1: {{% game 246784 %}}Cryptid{{% /game %}}

*3–5 players, 30–50 minutes, 10+ years, medium light (2.2), 74% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="246784" size="x300" alt="Cryptid" >}}

A bit of a latecomer to Germany, {{% game 246784 %}}Cryptid{{% /game %}} already gathered a lot of momentum internationally and hence is an easy recommendation for our algorithm.


## #2: {{% game 295947 %}}Cascadia{{% /game %}}

*1–4 players, 30–45 minutes, 10+ years, medium light (1.9), 53% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="295947" size="x300" alt="Cascadia" >}}

{{% game 295947 %}}Cascadia{{% /game %}} is another international favourite that was met with positive reviews, though most find it soothing rather than exciting. Also, it seems to be just on the border between the two awards, so could end up on either list.


## #3: {{% game 342942 %}}Ark Nova{{% /game %}}

*1–4 players, 90–150 minutes, 14+ years, medium heavy (3.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="342942" size="x300" alt="Ark Nova" >}}

{{% game 342942 %}}Ark Nova{{% /game %}} is *the* heavy eurogame of the season and has a good shot at a spot on the longlist. It's way too heavy for a nomination though.


## #4: {{% game 279537 %}}The Search for Planet X{{% /game %}}

*1–4 players, 60 minutes, 13+ years, medium light (2.3), 98% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="279537" size="x300" alt="The Search for Planet X" >}}

Just like {{% game 246784 %}}Cryptid{{% /game %}}, {{% game 279537 %}}The Search for Planet X{{% /game %}} is a deduction game that gained a lot of recognition internationally and now could receive its share of fame in Germany.


## #5: {{% game 314491 %}}Meadow{{% /game %}}

*1–4 players, 60–90 minutes, 10+ years, medium light (2.2), 97% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="314491" size="x300" alt="Meadow" >}}

Another non–controversial game with a soothing animal theme. I don't have more to say about {{% game 314491 %}}Meadow{{% /game %}}.


## #6: {{% game 316554 %}}Dune: Imperium{{% /game %}}

*1–4 players, 60–120 minutes, 14+ years, medium (3.0), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="316554" size="x300" alt="Dune: Imperium" >}}

My feeling is that games with a strong franchise generally are somewhat outside the jury's scope: While strongly drawing in the enthusiastic fan base, it leaves the majority of the audience rather distance. {{% game 316554 %}}Dune: Imperium{{% /game %}} might just be the exception to the rule since the reviews were really strong.


## #7: {{% game 227224 %}}The Red Cathedral{{% /game %}}

*1–4 players, 80 minutes, 10+ years, medium (2.8), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="227224" size="x300" alt="The Red Cathedral" >}}

Another game that was available internationally and has recently seen a German release from Kosmos, who certainly know how to win awards with their games.


## #8: {{% game 290236 %}}Canvas{{% /game %}}

*1–5 players, 30 minutes, 14+ years, medium light (1.7), 88% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="290236" size="x300" alt="Canvas" >}}

{{% game 290236 %}}Canvas{{% /game %}} definitely has some stunning artwork, though the critical response to the gameplay was rather lackluster…


## #9: {{% game 341048 %}}Free Ride{{% /game %}}

*1–5 players, 50–90 minutes, 10+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="341048" size="x300" alt="Free Ride" >}}

Friedemann Friese's venture into the train game genre. It's been a while since the jury was really excited by one of his creations.


## #10: {{% game 328479 %}}Living Forest{{% /game %}}

*1–4 players, 40 minutes, 10+ years, medium light (2.2), 77% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="328479" size="x300" alt="Living Forest" >}}

{{% game 328479 %}}Living Forest{{% /game %}} is the latest {{% kdj %}}Kennerspiel{{% /kdj %}} hotness. It got quite recently released and hasn't received a lot of ratings yet, but is definitely on the jury's radar.


## My two cents

Same procedure as for {{% sdj / %}}, here are my three top picks for {{% kdj / %}} nomination:

* {{% game 295947 %}}Cascadia{{% /game %}}
* {{% game 316554 %}}Dune: Imperium{{% /game %}}
* {{% game 328479 %}}Living Forest{{% /game %}}


# Honourable mentions

This is always the section where I squeeze in a few more title in order to increase my chance of covering the whole list. There's plenty of strong games I could mention, but I'll restrict myself to two additional candidates for {{% sdj / %}} that the algorithm just wouldn't quite pick up:

* {{% game 346482 %}}Voll verplant{{% /game %}} (internationally known as {{% game 248861 %}}Metro X{{% /game %}}): A simple to learn, yet very difficult to master flip & write subway building game.
* {{% game 291453 %}}SCOUT{{% /game %}}: A highly celebrated ladder–climbing game from highly celebrated publisher Oink Games.


# Conclusion

Looking through the list of games, there's two trends I see:

1. Games arriving late to Germany. More so than in previous years, there's plenty of titles with release date 2020 or earlier in the BGG database which have become only available in the past 12 months to the German market. Of course, there's a bias towards these games in the algorithm since they received more ratings than brand new titles, but there might also be some release delays due to the ongoing effects of COVID–19.
2. Nature. Maybe this is the legacy of smash hit {{% game 266192 %}}Wingspan{{% /game %}} or maybe it's people looking for comfort. But there are definitely *a lot* of animals, plants, parks, etc, on the covers of this list.

Will the jury agree and follow my predictions? We'll see on Monday, May 23. I can't wait! 🤩

[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2021 and March 2022 into German retail. Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
[^kennerspiel]: I'll trust the algorithm and the scores it outputs blindly. As every year, it'll be an interesting validation of the Kennerspiel score to see whether the jury agrees or not.
