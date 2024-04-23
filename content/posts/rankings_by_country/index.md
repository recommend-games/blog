---
title: The world of board games
subtitle: Board game rankings by country
slug: world-of-board-games
author: Markus Shepherd
type: post
date: 2024-04-22T14:00:00+03:00
tags:
  - BoardGameGeek
  - BGG
  - ranking
  - rating
  - Bayesian
  - dummy ratings
  - highest rated games
  - alternative rankings
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.4.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.4.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.4.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.4.1.min.js" ></script>

BoardGameGeek (BGG) users can select their country of residence in their profile. The main purpose is to find other users in your region to play face to face or maybe trade games, but but over here at [Recommend.Games](https://recommend.games/#/) we obviously cannot help ourselves but to use this information for some interesting statistics. 🤓

Let's start with the usual disclaimer: We will have to rely on whatever information BGG provides. In particular, users can freely choose their country. As mentioned, this is meant to be the country of residence, but some users might rather choose their country of origin – or some outright nonsense. There are 19 BGG users who claim to be from Antarctica, for example. While I'm sure that the long polar nights on lonely research stations are perfect for playing board games, I'm not sure if they have a lot of time to rate them on BGG. 🐧 (If they actually did, Antarctica would have 6,880 ratings per 100 thousand residents, which would make them by far the biggest board game enthusiasts in the world – more on that later.)

On a more serious note, what exactly is a country is a *very* political question and frequently highly controversial. I'm trying to stick with the sovereign nations recognized by the United Nations and️ add users from subdivisions and autonomous regions to the parent country. BGG allows users to choose England 🏴󠁧󠁢󠁥󠁮󠁧󠁿, Scotland 🏴󠁧󠁢󠁳󠁣󠁴󠁿 or Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿 as their residence (but not Northern Ireland 🤔) – but for now, they're all stuck together in a United Kingdom 🇬🇧, if they like it or not. The borders in the map that follows shortly are even more contentious – I just had to stick with what the provider chose, and they emphasised the actual situation on the ground.

{{% bokeh "board_games_world_map.json" %}}
