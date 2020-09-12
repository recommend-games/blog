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

While BGG founder Scott Alden admitted in a recent interview on the excellent [Five Games For Doomsday](https://fivegamesfordoomsday.com/2020/07/06/scott-alden/) podcast that he doesn't care all that much thought about the rankings, gamers around the world certainly do. They would discuss heatedly any movement in the rankings, question why games X is up there while game Y is missing, and generally criticise the selection for either having *too many* or *not enough* recent releases.

Reason enough for me to take a closer look at how the rankings work and some of the maths behind it.

Generally speaking, we want to rank a game higher the better its score is. The first instinct would be to just sum up all the ratings users gave to that particular game, divide by the number of ratings, and rank games from highest to lowest. What I just described would be the *arithmetic mean* (or just *average* if you feel less fancy) of the ratings, which is simple and intuitive, but suffers from a sever defect: A game with a single rating of \\(10\\) would always sit on top of the ranking, well ahead of much beloved games with thousands of votes that couldn't possibly be all \\(10\\)s.

The easy fix is filtering out games with less than a certain number of ratings, say \\(100\\).

{{% game 261393 %}}Dungeon Universalis{{% /game %}}

# TODO: link to some external resources:

* https://www.peterjezik.com/bgg/
* https://youtu.be/Y1t_0LhpDmU
