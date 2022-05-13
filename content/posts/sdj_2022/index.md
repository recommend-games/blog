---
title: Spiel des Jahres 2022 predictions
slug: spiel-des-jahres-2022-predictions
author: Markus Shepherd
type: post
date: 2022-05-10T22:30:00+03:00
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

{{% sdj %}}Spiel des Jahres 2022{{% /sdj %}} is around the corner! (Has it really been a year already since we last spoke with each other? 😅) We're blessed with another strong year full of wonderful games that all compete for the most prestigious award in board gaming. As in the [previous]({{<ref "posts/sdj_2020/index.md">}}) [years]({{<ref "posts/sdj_2021/index.md">}}), I'll try to predict what games have the best shot at ending up on the longlist (aka *recommendations*) and the shortlist (aka *nominations*).

Even more so than in previous years, I didn't have much time (thanks, kids 👨‍👩‍👧‍👧), so I've mostly used the same algorithmic approach as last year. First, I took all eligible games and separated them into two lists: one for {{% sdj / %}} and one for {{% kdj / %}}, depending on their [{{% kdj %}}Kennerspiel{{% /kdj %}} score]({{<ref "posts/kennerspiel/index.md">}}). Then I scored those games in a couple of different ways, and finally combined those into the final result:

* Recommend.Games [recommendation algorithm](https://recommend.games/#/?for=S_d_J&yearMin=2021&yearMax=2022&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (TBD%). This has proven to be a powerful and reliable method to capture the jury's taste, but it's slow to recommend new games with few ratings.
* {{% sdj / %}} probability (TBD%). Similar to the model that calculates the {{% kdj %}}Kennerspiel{{% /kdj %}} score, I've trained a model that tries to predict a game's chances to end up on the jury's longlist. This is particularly designed to unearth candidates with few votes, but it's still rudimentary at this point.
* Average BoardGameGeek rating (TBD%). Let the gamers speak! In order to give new games a chance, we'll take a look at the simple average rating.
* Geek score (aka [Bayesian average]({{<ref "posts/reverse_engineer_bgg/index.md">}}), TBD%). This score starts out at 5.5, and gets closer to the actual average the more ratings come in. It's more reliable, but also strongly favours games that have been around for longer and hence gathered more ratings.
* [Recommend.Games ranking](TBD) (TBD%). We introduced a new default ranking on R.G a couple of months ago, which seems to pick up new games shooting up the hotness a little faster than on BGG, so let's give it a shot as part of these predictions. 🤓

You can find the [detailed analysis here](predictions.py) and [complete results here](predictions.csv). But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2022{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2022{{% /sdj %}}

{{< img src="sdj-blank" size="x300" alt="Spiel des Jahres 2022" >}}


## #1: {{% game 327831 %}}Lost Cities: Roll & Write{{% /game %}}

*2–5 players, 30 minutes, 8+ years, light (1.1), 97% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="327831" size="x300" alt="Lost Cities: Roll & Write" >}}

This is an interesting one: While the jury completely ignored the original {{% game 50 %}}Lost Cities{{% /game %}} (now considered a classic), it did pin the main award on {{% game 34585 %}}Keltis{{% /game %}} (essentially the board game version). Will they come back to the same system for the {{% game 327831 %}}Roll & Write{{% /game %}} version?


## #2: {{% game 300905 %}}Top Ten{{% /game %}}

*4–9 players, 30 minutes, 14+ years, light (1.1), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300905" size="x300" alt="Top Ten" >}}

Another cooperative party game, light and with an immediate hook – exactly what the jury is looking for.


## #3: {{% game 329839 %}}So Clover!{{% /game %}}

*3–6 players, 30 minutes, 10+ years, light (1.1), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="329839" size="x300" alt="So Clover!" >}}

Another cooperative word–association game by publisher Repos Production, in many ways reminiscent of {{% sdj / %}} winner {{% game 254640 %}}Just One{{% /game %}}. The jury generally doesn't mind repeating themselves, so {{% game 329839 %}}So Clover!{{% /game %}} is definitely in the running.


## #4: {{% game 346703 %}}7 Wonders: Architects{{% /game %}}

*2–7 players, 25 minutes, 8+ years, light (1.4), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="346703" size="x300" alt="7 Wonders: Architects" >}}

The little sibling of the inaugural {{% kdj / %}} winner already won the 2022 As d'Or, the French equivalent of {{% sdj / %}}, so this is definitely one to watch.


## #5: {{% game 339484 %}}Savannah Park{{% /game %}}

*1–4 players, 20–40 minutes, 8+ years, medium light (1.7), 95% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="339484" size="x300" alt="Savannah Park" >}}

{{% game 339484 %}}Savannah Park{{% /game %}} by Kramer & Kiesling follows another trend in 2022: animals. Can this one stand out?


## #6: {{% game 303672 %}}Trek 12: Himalaya{{% /game %}}

*1–50 players, 15–30 minutes, 8+ years, light (1.4), 89% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="303672" size="x300" alt="Trek 12: Himalaya" >}}

Roll & write games have garnered many nominations and recommendations, but never the main award. {{% game 303672 %}}Trek 12{{% /game %}} could change that.


## #7: {{% game 346995 %}}Kings & Creatures{{% /game %}}

*2–6 players, 30 minutes, 10+ years,  (nan), 87% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="346995" size="x300" alt="Kings & Creatures" >}}

{{% game 346995 %}}Kings & Creatures{{% /game %}}


## #8: {{% game 300753 %}}Cross Clues{{% /game %}}

*2–6 players, 5–10 minutes, 7+ years, light (1.0), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300753" size="x300" alt="Cross Clues" >}}

…and another cooperative word–association party game… I sense a pattern! 😅 Does {{% game 300753 %}}Cross Clues{{% /game %}} have what it takes to set itself apart from its competitors?


## #9: {{% game 338628 %}}TRAILS{{% /game %}}

*2–4 players, 20–40 minutes, 10+ years, medium light (1.8), 93% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="338628" size="x300" alt="TRAILS" >}}

{{% game 338628 %}}TRAILS{{% /game %}}


## #10: {{% game 330038 %}}Llamaland{{% /game %}}

*2–4 players, 45 minutes, 10+ years, medium light (2.0), 80% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="330038" size="x300" alt="Llamaland" >}}

{{% game 330038 %}}Llamaland{{% /game %}}


## #11: {{% game 314503 %}}Codex Naturalis{{% /game %}}

*1–4 players, 20–30 minutes, 7+ years, medium light (1.8), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="314503" size="x300" alt="Codex Naturalis" >}}

{{% game 314503 %}}Codex Naturalis{{% /game %}}


## #12: {{% game 330174 %}}Explorers{{% /game %}}

*1–4 players, 20 minutes, 8+ years, medium light (1.8), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="330174" size="x300" alt="Explorers" >}}

{{% game 330174 %}}Explorers{{% /game %}}


## My two cents

TODO


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2022{{% /kdj %}}

{{< img src="ksdj-blank" size="x300" alt="Kennerspiel des Jahres 2022" >}}


## #1: {{% game 246784 %}}Cryptid{{% /game %}}

*3–5 players, 30–50 minutes, 10+ years, medium light (2.2), 74% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="246784" size="x300" alt="Cryptid" >}}

A bit of a latecomer to Germany, {{% game 246784 %}}Cryptid{{% /game %}} already gathered a lot of momentum internationally and hence is an easy recommendation for our algorithm.


## #2: {{% game 295947 %}}Cascadia{{% /game %}}

*1–4 players, 30–45 minutes, 10+ years, medium light (1.9), 53% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="295947" size="x300" alt="Cascadia" >}}

{{% game 295947 %}}Cascadia{{% /game %}} is another international favourite that was met with positive reviews, though most find it soothing rather than exciting.


## #3: {{% game 342942 %}}Ark Nova{{% /game %}}

*1–4 players, 90–150 minutes, 14+ years, medium heavy (3.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="342942" size="x300" alt="Ark Nova" >}}

{{% game 342942 %}}Ark Nova{{% /game %}} is *the* heavy eurogame of the season and has a good shot at a spot on the longlist. It's way too heavy for a nomination though.


## #4: {{% game 314491 %}}Meadow{{% /game %}}

*1–4 players, 60–90 minutes, 10+ years, medium light (2.2), 97% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="314491" size="x300" alt="Meadow" >}}

{{% game 314491 %}}Meadow{{% /game %}}


## #5: {{% game 279537 %}}The Search for Planet X{{% /game %}}

*1–4 players, 60 minutes, 13+ years, medium light (2.3), 98% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="279537" size="x300" alt="The Search for Planet X" >}}

{{% game 279537 %}}The Search for Planet X{{% /game %}}


## #6: {{% game 316554 %}}Dune: Imperium{{% /game %}}

*1–4 players, 60–120 minutes, 14+ years, medium (3.0), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="316554" size="x300" alt="Dune: Imperium" >}}

{{% game 316554 %}}Dune: Imperium{{% /game %}} is another game that shot up the BGG rankings (currently at #16). My feeling is that games with a strong franchise generally are somewhat outside the jury's scope, but this game might be the exception to the rule since the reviews were really strong.


## #7: {{% game 227224 %}}The Red Cathedral{{% /game %}}

*1–4 players, 80 minutes, 10+ years, medium (2.8), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="227224" size="x300" alt="The Red Cathedral" >}}

Another game that was available internationally and has recently seen a German release from Kosmos, who certainly know how to win awards with their games.


## #8: {{% game 290236 %}}Canvas{{% /game %}}

*1–5 players, 30 minutes, 14+ years, medium light (1.7), 88% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="290236" size="x300" alt="Canvas" >}}

{{% game 290236 %}}Canvas{{% /game %}} definitely has some stunning artwork, though the critical response to the gameplay was rather lackluster…


## #9: {{% game 318560 %}}Witchstone{{% /game %}}

*2–4 players, 60–90 minutes, 12+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="318560" size="x300" alt="Witchstone" >}}

{{% game 318560 %}}Witchstone{{% /game %}}


## #10: {{% game 328871 %}}Terraforming Mars: Ares Expedition{{% /game %}}

*1–4 players, 45–60 minutes, 14+ years, medium (2.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="328871" size="x300" alt="Terraforming Mars: Ares Expedition" >}}

{{% game 328871 %}}Terraforming Mars: Ares Expedition{{% /game %}}


## #11: {{% game 328479 %}}Living Forest{{% /game %}}

*1–4 players, 40 minutes, 10+ years, medium light (2.2), 77% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="328479" size="x300" alt="Living Forest" >}}

{{% game 328479 %}}Living Forest{{% /game %}} is definitely the latest {{% kdj %}}Kennerspiel{{% /kdj %}} hotness. It got quite recently released and hasn't received a lot of ratings yet, but is definitely on the jury's radar.


## #12: {{% game 346501 %}}Mille Fiori{{% /game %}}

*2–4 players, 60–90 minutes, 10+ years, medium light (2.2), 92% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="346501" size="x300" alt="Mille Fiori" >}}

{{% game 346501 %}}Mille Fiori{{% /game %}}


## My two cents

TODO


# Honourable mentions

TODO


## {{% sdj / %}}

* TODO


## {{% kdj / %}}

* TODO
