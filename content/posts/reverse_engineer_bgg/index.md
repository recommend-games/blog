---
title: Reverse engineering the BoardGameGeek ranking
slug: reverse-engineering-boardgamegeek-ranking
author: Markus Shepherd
type: post
date: 2020-09-11T00:00:00+03:00
tags:
  - BoardGameGeek
  - BGG
  - ranking
---

I often describe [BoardGameGeek (BGG)](https://boardgamegeek.com/) as "the [Internet Movie Database (IMDb)](https://www.imdb.com/) for games". Much like its cinematic counterpart, the biggest board game database not only collects all sorts of information obsessively, but also allows users to rate games on a scale from \\(1\\) (*awful - defies game description*) to \\(10\\) (*outstanding - will always enjoy playing*). These ratings are then used to rank games, with {{% game 174430 %}}Gloomhaven{{% /game %}} occupying the top spot since December 2017.

While BGG founder Scott Alden admitted in a recent interview on the excellent [Five Games For Doomsday](https://fivegamesfordoomsday.com/2020/07/06/scott-alden/) podcast that he doesn't care all that much about the rankings, gamers around the world certainly do. They would discuss heatedly any movement in the rankings, question why games X is up there while game Y is missing, and generally criticise the selection for either having *too many* or *not enough* recent releases.

Reason enough for me to take a closer look at how the rankings work and some of the maths behind it.

Generally speaking, we want to rank a game higher the better its score is. The first instinct would be to just sum up all the ratings users gave to that particular game, divide by the number of ratings, and rank games from highest to lowest. What I just described would be the *arithmetic mean* (or just *average* if you feel less fancy) of the ratings, which is simple and intuitive, but suffers from a sever defect: A game with a single rating of \\(10\\) would always sit on top of the ranking, well ahead of much beloved games with thousands of votes that couldn't possibly be all \\(10\\)s.

The easiest fix is filtering out games with less than a certain number of ratings, say \\(100\\). That's a decent enough approach, and yields the following top 5 games as of the time of writing:

1. {{% game 261393 %}}Dungeon Universalis{{% /game %}}
2. {{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}
3. {{% game 219217 %}}Arena: The Contest{{% /game %}}
4. {{% game 240271 %}}Core Space{{% /game %}}
5. {{% game 209877 %}}World At War 85: Storming the Gap{{% /game %}}

Notably, those are all very recent games with relatively few ratings.[^jotl] Some might consider this a feature, not a bug, but when your intention is to create a list of the best board games, you probably do want to give a nod to proven classics, and not just the latest hotness. How to balance out these ends of the spectrum is in the end a choice you have to make, and no matter what it is, People on the Internet™ will not like it.

The way both IMDb and BGG chose to tackle this issue is by essentially not trusting the ratings – at least not too much. The method boils down to assigning a new item in the database (be it movie or game) a predefined average by default, and only gradually trusting the ratings' average as thousands and thousands of users have cast their votes. More concretely the rankings are calculated by adding a number of dummy votes with a chosen average value, say \\(5.5\\), to each game's regular ratings. The result is that initially each game will have a score close to \\(5.5\\), but as more users rate the game, that score will move closer and closer to the conventional mean.

BGG calls this their **geek score**. Mathematically speaking, it is a *Bayesian average*, and calculates as follows:

\\[ \textrm{geek score} = \frac{\textrm{number of ratings} \cdot \textrm{average rating} + \textrm{number of dummies} \cdot \textrm{dummy value}}{\textrm{number of ratings} + \textrm{number of dummies}} \\]

Don't worry too much about the details though – *adding dummy votes* is really all you need to understand.

OK, so that's the concept, but crucially that's not all the details. You still need to choose *how many* dummy votes you want to add and *what value* they should take.

# TODO: link to some external resources:

* https://www.peterjezik.com/bgg/
* https://youtu.be/Y1t_0LhpDmU

[^jotl]: {{% game 291457 %}}Jaws of the Lion{{% /game %}} is something of an exception here and will undoubtably shoot into the BGG top 10 very soon. In fact, it might be the only game with the potential to unseat {{% game 174430 %}}Gloomhaven{{% /game %}} as the number 1.
