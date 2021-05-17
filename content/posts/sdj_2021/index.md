---
title: Spiel des Jahres 2021 predictions
slug: spiel-des-jahres-2021-predictions
author: Markus Shepherd
type: post
date: 2021-05-14T02:30:00+03:00
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

{{< img src="sdj-all" size="x300" alt="Spiel des Jahres" >}}

It's our favourite time of the year again: time for {{% sdj / %}} nominations! On Monday, May 17th, the jury will once again announce their longlist (aka recommendations) and shortlist (aka nominations) for {{% sdj / %}}, {{% kdj / %}} and {{% kindersdj %}}Kinderspiel des Jahres 2021{{% /kindersdj %}}. Just like [last year]({{<ref "posts/sdj_2020/index.md">}}), I'll try to produce a list of the most promising games to land on the longlist for {{% sdj %}}Spiel{{% /sdj %}} and {{% kdj %}}Kennerspiel{{% /kdj %}}. (I'll promise to get around to {{% kindersdj %}}Kinderspiel{{% /kindersdj %}} predictions [in a couple of years](https://twitter.com/recommend_games/status/1373396030616694785?s=20).)

Unlike last year, I won't use hard filters though to distinguish between {{% sdj %}}red{{% /sdj %}} and {{% kdj %}}anthracite{{% /sdj %}} games, but will rely on the **{{% kdj %}}Kennerspiel{{% /kdj %}} score** I developed [a couple of months back]({{<ref "posts/kennerspiel/index.md">}}). This model tries to predict if a game is a {{% kdj %}}Kennerspiel{{% /kdj %}} or not based on some key features, like complexity, play time, age recommendations and game type. The jury's decision this year what list a game belongs to will be the first actual test for that model too, so let's hope it actually made sense! 🤞

Even more so than the previous year, I'll take an algorithmic approach. That is, I do not follow my own taste or gut feelings, but I let the numbers talk. First, I took all eligible games[^eligible] and separated them into two lists: one for {{% sdj / %}} and one for {{% kdj / %}}, depending on their {{% kdj %}}Kennerspiel{{% /kdj %}} score. Then I ranked those games in a couple of different ways, and finally combined those into the final result:

* Sorted by the Recommend.Games [recommendation algorithm](https://recommend.games/#/?for=S_d_J&yearMin=2020&yearMax=2021&excludeOwned=false&playerCount=4&playerCountType=box&playTime=120&playTimeType=max&playerAge=16&playerAgeType=box) (90%). This has proven to be a powerful and reliable method to capture the jury's taste, but it's slow to recommend new games with few ratings.
* {{% sdj / %}} probability (5%). Similar to the model that calculates the {{% kdj %}}Kennerspiel{{% /kdj %}} score, I've trained a model that tries to predict a game's chances to end up on the jury's longlist. This is particularly designed to unearth candidates with few votes, but it's still rudimentary at this point.
* Average BoardGameGeek rating (2.5%). Let the gamers speak! In order to give new games a chance, we'll take a look at the simple average rating.
* Geek score (aka [Bayesian average]({{<ref "posts/reverse_engineer_bgg/index.md">}}), 2.5%). This score starts out at 5.5, and gets closer to the actual average the more ratings come in. It's more reliable, but also strongly favours games that have been around for longer and hence gathered more ratings.

You can find the [detailed analysis here](predictions.py) and [complete results here](predictions.csv). But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2021{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2021{{% /sdj %}}

{{< img src="sdj-2021" size="x300" alt="Spiel des Jahres 2021" >}}

## #1: {{% game 318977 %}}MicroMacro: Crime City{{% /game %}}

*1–4 players, 15–45 minutes, 10+ years, light (1.1), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="318977" size="x300" alt="MicroMacro: Crime City" >}}

Some games can be played without reading any rules. {{% game 318977 %}}MicroMacro{{% /game %}} goes one step further: You can start playing the game right on the box. This alone makes it a strong contender. I wonder though if the jury will consider a game full of murders and crimes a pleasant pastime for families.


## #2: {{% game 266524 %}}PARKS{{% /game %}}

*1–5 players, 30–60 minutes, 10+ years, medium light (2.2), 88% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="266524" size="x300" alt="PARKS" >}}

Something of a latecomer to Germany, the looks and theme of {{% game 266524 %}}PARKS{{% /game %}} are somewhat reminiscent of the previous {{% kdj %}}Kennerspiel{{% /kdj %}} winner {{% game 266192 %}}Wingspan{{% /game %}}. Will this work to its advantage?


<!-- ## #3: {{% game 276498 %}}Paris: La Cité de la Lumière{{% /game %}}

*2 players, 30 minutes, 8+ years, medium light (2.1), 96% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="276498" size="x300" alt="Paris: La Cité de la Lumière" >}}

While the algorithm ranks this highly, I still do not see a pure 2-player-game win the main award. A place on the recommendation list on the other hand is always possible. -->


## #3: {{% game 256788 %}}Detective Club{{% /game %}}

*4–8 players, 45 minutes, 8+ years, light (1.2), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="256788" size="x300" alt="Detective Club" >}}

Light and social, just like the jury likes their {{% sdj %}}red games{{% /sdj %}}. {{% game 256788 %}}Detective Club{{% /game %}} requires at least four players though, and the jury generally wants three players as well.


## #4: {{% game 223040 %}}Fantasy Realms{{% /game %}}

*3–6 players, 20 minutes, 14+ years, medium light (1.7), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="223040" size="x300" alt="Fantasy Realms" >}}

Quite an old game by international standards, but it garnered its share of positive review. A breezy card game might just be what the jury is looking for!


## #5: {{% game 300327 %}}The Castles of Tuscany{{% /game %}}

*2–4 players, 45–60 minutes, 10+ years, medium light (2.2), 89% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300327" size="x300" alt="The Castles of Tuscany" >}}

There's no doubt that the jury is a fan of [Stefan Feld](https://recommend.games/#/?designer=4958)'s work. {{% game 300327 %}}The Castles of Tuscany{{% /game %}} could earn him his first {{% sdj / %}} nomination.


## #6: {{% game 274960 %}}Point Salad{{% /game %}}

*2–6 players, 15–30 minutes, 8+ years, light (1.2), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="274960" size="x300" alt="Point Salad" >}}

By all accounts, this seems to be a light and fun card game that could well be in the jury's wheelhouse. I love the self-ironic title, but will the average gamer get the joke?


## #7: {{% game 283864 %}}Trails of Tucana{{% /game %}}

*1–8 players, 15 minutes, 8+ years, light (1.3), 100% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="283864" size="x300" alt="Trails of Tucana" >}}

Yet another simple roll/flip'n'write. It reminds me a lot of last year's {{% game 270673 %}}Silver & Gold{{% /game %}} which I had high hopes for, but was completely ignored by the jury. Might not be the best omen for {{% game 283864 %}}Trails of Tucana{{% /game %}}.


## #8: {{% game 299172 %}}The Key: Murder at the Oakdale Club{{% /game %}} & {{% game 299171 %}}Theft at Cliffrock Villa{{% /game %}}

*1–4 players, 15–20 minutes, 8+ years, medium light (2.0), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="299172" size="x300" alt="The Key: Murder at the Oakdale Club" >}}

One year after his smash hit {{% game 284083 %}}The Crew{{% /game %}}, [Thomas Sing](https://recommend.games/#/?designer=45563) might reach for {{% sdj / %}} this time. A real-time deduction game sure sounds like a winning combo!


## #9: {{% game 300877 %}}New York Zoo{{% /game %}}

*1–5 players, 30–60 minutes, 10+ years, medium light (2.0), 96% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="300877" size="x300" alt="New York Zoo" >}}

Another puzzle game by [Uwe Rosenberg](https://recommend.games/#/?designer=10), this time filled to the brim with cute animals. Who could resist this proposition?


## #10: {{% game 326494 %}}The Adventures of Robin Hood{{% /game %}}

*2–4 players, 60 minutes, 10+ years, medium light (1.7), 99% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="326494" size="x300" alt="The Adventures of Robin Hood" >}}

As a very recent release, {{% game 326494 %}}Robin Hood{{% /game %}} doesn't have many ratings yet, so it's hard for the algorithm to pick up. But by all appearances, [Michael Menzel](https://recommend.games/#/?designer=11825) of {{% game 127398 %}}Andor{{% /game %}} fame pulled off another great story game.


<!-- ## #12: {{% game 274841 %}}Cóatl{{% /game %}}

*1–4 players, 30–60 minutes, 10+ years, medium light (2.0), 98% {{% sdj %}}Spiel{{% /sdj %}}*

{{< img src="274841" size="x300" alt="Cóatl" >}}

{{% game 274841 %}}Cóatl{{% /game %}} -->


## My two cents

Alright, that's what the algorithms say. But just like last year, I'd like to let my guts have some say as well. These are the three games I consider having the best shot at ending up on the jury's shortlist:

* **{{% game 318977 %}}MicroMacro: Crime City{{% /game %}}**
* **{{% game 326494 %}}The Adventures of Robin Hood{{% /game %}}**
* **{{% game 299172 %}}The Key: Murder at the Oakdale Club{{% /game %}} & {{% game 299171 %}}Theft at Cliffrock Villa{{% /game %}}**


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2021{{% /kdj %}}

{{< img src="ksdj-2021" size="x300" alt="Kennerspiel des Jahres 2021" >}}


## #1: {{% game 281259 %}}The Isle of Cats{{% /game %}}

*1–4 players, 60–90 minutes, 8+ years, medium light (2.3), 94% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="281259" size="x300" alt="The Isle of Cats" >}}

The Internet loves cats, and, apparently, so does the BGG crowd. Card drafting and tile laying combined with lots of cats – what's there not to like?


## #2: {{% game 283155 %}}Calico{{% /game %}}

*1–4 players, 30–45 minutes, 13+ years, medium light (2.2), 62% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="283155" size="x300" alt="Calico" >}}

More cats, more puzzling – I sense a theme here. {{% game 283155 %}}Calico{{% /game %}} is held in high regards as well, even for {{% sdj / %}} by some. It'll be exciting to see if the jury has it on their list, and, if so, on which.


## #3: {{% game 312484 %}}Lost Ruins of Arnak{{% /game %}}

*1–4 players, 30–120 minutes, 12+ years, medium (2.8), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="312484" size="x300" alt="Lost Ruins of Arnak" >}}

This game seems to be on everybody's mind, and even though nobody seems excited by it, the consensus is that {{% game 312484 %}}Lost Ruins of Arnak{{% /game %}} perfectly executes its combination of deckbuilding and worker placement.


## #4: {{% game 224517 %}}Brass: Birmingham{{% /game %}}

*2–4 players, 60–120 minutes, 14+ years, medium heavy (3.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="224517" size="x300" alt="Brass: Birmingham" >}}

Certainly a fan favourite, it climbed to #3 on BGG before it finally received a German release. It's definitely way too heavy to win {{% kdj %}}Kennerspiel{{% /kdj %}}, but that wouldn't stop the jury from recommending it.


## #5: {{% game 283294 %}}Yukon Airways{{% /game %}}

*1–4 players, 60–90 minutes, 14+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="283294" size="x300" alt="Yukon Airways" >}}

The only thing on my mind about this game: Would the jury really award a game about flying after we've been collectively grounded for over a year?


## #6: {{% game 317311 %}}Switch & Signal{{% /game %}}

*2–4 players, 45 minutes, 10+ years, medium light (2.2), 83% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="317311" size="x300" alt="Switch & Signal" >}}

Train games have a long tradition in board gaming, but {{% game 317311 %}}Switch & Signal{{% /game %}} is the first one I know of to approach the topic co-operatively. Colour me intrigued.


## #7: {{% game 300531 %}}Paleo{{% /game %}}

*1–4 players, 45–60 minutes, 10+ years, medium (2.6), 88% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="300531" size="x300" alt="Paleo" >}}

{{% game 300531 %}}Paleo{{% /game %}} already received so much love for the game, and so much criticism for the rule book. The jury is known to exclude games when they just put an undue burden on the players to learn, but in this case the qualities of the game probably win.


## #8: {{% game 281075 %}}Welcome to New Las Vegas{{% /game %}}

*1–50 players, 35 minutes, 10+ years, medium (2.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="281075" size="x300" alt="Welcome to New Las Vegas" >}}

The jury ignored the original {{% game 233867 %}}Welcome To…{{% /game %}}, but will it notice this more complex version set in Nevada?


## #9: {{% game 286096 %}}Tapestry{{% /game %}}

*1–5 players, 90–120 minutes, 12+ years, medium (2.9), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="286096" size="x300" alt="Tapestry" >}}

Stonemaier Games sure knows how to put out beautful products, but I think in the case of {{% game 286096 %}}Tapestry{{% /game %}} the result is just too big and too expensive for a {{% kdj / %}}.


## #10: {{% game 282954 %}}Paris{{% /game %}}

*2–4 players, 90 minutes, 12+ years, medium (2.7), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="282954" size="x300" alt="Paris" >}}

The K&K of board gaming show no signs of slowing down, and their latest brain child {{% game 282954 %}}Paris{{% /game %}} has received a lot of love.


<!-- ## #11: {{% game 304420 %}}Bonfire{{% /game %}}

*1–4 players, 70–100 minutes, 12+ years, medium heavy (3.6), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="304420" size="x300" alt="Bonfire" >}}

{{% game 304420 %}}Bonfire{{% /game %}} -->


<!-- ## #12: {{% game 251247 %}}Barrage{{% /game %}}

*1–4 players, 60–120 minutes, 14+ years, medium heavy (4.0), 100% {{% kdj %}}Kennerspiel{{% /kdj %}}*

{{< img src="251247" size="x300" alt="Barrage" >}}

{{% game 251247 %}}Barrage{{% /game %}} -->


## My two cents

Finally, here are my three top candidates for a spot on the shortlist for {{% kdj %}}Kennerspiel des Jahres 2021{{% /kdj %}}:

* {{% game 312484 %}}Lost Ruins of Arnak{{% /game %}}
* {{% game 300531 %}}Paleo{{% /game %}}
* {{% game 317311 %}}Switch & Signal{{% /game %}}

Again, I think this is another year of fantastic games, so competition for the awards will be fierce. I'm certainly looking forward to learning if the jury agrees with my (algorithm's) assessment!


# Honourable mentions

Last but not least I want to send you off with a couple of games that didn't make the algorithm's cut, but are still interesting in their own rights and might end up amongst the recommendations:


## {{% sdj / %}}

* {{% game 276498 %}}Paris: La Cité de la Lumière{{% /game %}}: Highly rated by the algorithm, but no chance for the main award as a two-player-game.
* {{% game 295948 %}}Aqualin{{% /game %}}: Ditto.
* {{% game 319114 %}}Krazy Pix{{% /game %}}: Not many party games on this list, so here's one.
* {{% game 302260 %}}Abandon All Artichokes{{% /game %}}: Such a fresh and unexpected theme, would make a great entry level deckbuilder.
* {{% game 325555 %}}Cantaloop: Book 1 – Breaking into Prison{{% /game %}}: Point-and-click adventures as a board game could draw in a lot of new gamers.
* {{% game 288169 %}}The Fox in the Forest Duet{{% /game %}}: The competitive version has been recommended last year, so maybe the co-operative version has a chance this year.


## {{% kdj / %}}

* {{% game 251247 %}}Barrage{{% /game %}}: A heavy-weight that might receive a recommendation.
* {{% game 293014 %}}Nidavellir{{% /game %}}
* {{% game 271324 %}}It's a Wonderful World{{% /game %}}
* {{% game 301716 %}}Glasgow{{% /game %}}
* {{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}: This lighter and more approachable version of BGG's #1 might be a candidate for {{% kdj / %}}.
* {{% game 306735 %}}Under Falling Skies{{% /game %}}: The jury loves to cover all aspects of gaming, so here's a solo game that received a lot of praises.
* {{% game 283317 %}}The 7th Continent: Classic Edition{{% /game %}}
* {{% game 318983 %}}Faiyum{{% /game %}}
* {{% game 298069 %}}Cubitos{{% /game %}}
* {{% game 311193 %}}Anno 1800{{% /game %}}
* {{% game 314040 %}}Pandemic Legacy: Season 0{{% /game %}}: The jury has a well-documented love for this series, so it seems unlikely they'll say goodbye silently.
* {{% game 191189 %}}Aeon's End{{% /game %}}: Another *very* late arrival to Germany. Thematically probably outside the jury's comfort zone, but they do love their deckbuilders and co-ops…


[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2020 and March 2021 into German retail (though because of COVID–19 hitting in March last year we might see a few latecomers this year). Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
