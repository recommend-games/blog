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

Let's start with the usual disclaimer: We will have to rely on whatever information BGG provides. In particular, users can freely choose their country. As mentioned, this is meant to be the country of residence, but some users might rather choose their country of origin – or some outright nonsense. There are 19 BGG users who claim to be from 🇦🇶 Antarctica, for example. While I'm sure that the long polar nights on lonely research stations are perfect for playing board games, I'm not sure if they have a lot of time to rate them on BGG. 🐧 (If they actually did, Antarctica would have 6,880 ratings per 100 thousand residents, which would make them the second biggest board game enthusiasts in the world – only behind the 🇻🇦 Vatican's 6 reported users, resulting in almost 20,000 ratings per 100 thousand residents. 🙏)

On a more serious note, what exactly is a country is a *very* political question and frequently highly controversial. I'm trying to stick with the sovereign nations recognized by the United Nations and️ add users from subdivisions and autonomous regions to the parent country. BGG allows users to choose 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland or 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales as their residence (not Northern Ireland though 🤔) – but for now, they're all stuck together in a 🇬🇧 United Kingdom, if they like it or not. The borders in the map that follows shortly are even more contentious – I just had to stick with what the provider chose, and they emphasised the actual situation on the ground.

With that out of the way, let's look at some basic statistics. For this analysis, we used almost **20 million ratings** by **346,697 users** who selected one of the **200 countries** as their residence. Close to **88 thousand games** received at least one rating.

In order to understand how board game preferences differ around the globe, we want to calculate a ranking similar to the way BGG ranks games. Remember that BGG calculates their "[geek score]({{<ref "posts/reverse_engineer_bgg/index.md">}})" based on a Bayesian average by adding a number of dummy ratings of 5.5 to each game. That [number of dummy ratings]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}) is determined by the total number of ratings divided by 10,000. We can apply exactly the same logic to calculate a ranking by country. Since we want to apply at least one dummy rating to each game, we only consider countries with at least 10,000 ratings in total – **62 countries** meet this criterion. BGG ranks games with at least 30 ratings. If we applied the same rule to the country rankings, we would often have very short lists. So, I decided to include games with at least 3 times the number of dummy ratings in the country ranking, but never more than the BGG standard of 30.

Enough of the boring technicalities, on to the fun part! 😎

| Country           | Population | Number of users | Total ratings | Ratings per 100k | #1 game                                                                       |
|-------------------|------------|-----------------|---------------|------------------|-------------------------------------------------------------------------------|
| 🇺🇸 United States  | 331.9 mil  | 131.7k          | 7724k         | 2327             | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |
| 🇩🇪 Germany        | 83.2 mil   | 19.0k           | 1457k         | 1751             | {{% game 342942 %}}Ark Nova{{% /game %}}                                      |
| 🇨🇦 Canada         | 38.2 mil   | 23.4k           | 1390k         | 3636             | {{% game 174430 %}}Gloomhaven{{% /game %}}                                    |
| 🇬🇧 United Kingdom | 67.3 mil   | 24.3k           | 1300k         | 1931             | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |
| 🇪🇸 Spain          | 47.4 mil   | 16.0k           | 913k          | 1926             | {{% game 224517 %}}Brass: Birmingham{{% /game %}}                             |
| 🇵🇱 Poland         | 37.7 mil   | 11.8k           | 620k          | 1644             | {{% game 187645 %}}Star Wars: Rebellion{{% /game %}}                          |
| 🇮🇹 Italy          | 59.1 mil   | 9.1k            | 550k          | 930              | {{% game 182028 %}}Through the Ages: A New Story of Civilization{{% /game %}} |
| 🇫🇷 France         | 67.7 mil   | 10.6k           | 529k          | 782              | {{% game 342942 %}}Ark Nova{{% /game %}}                                      |
| 🇳🇱 Netherlands    | 17.5 mil   | 7.5k            | 469k          | 2680             | {{% game 224517 %}}Brass: Birmingham{{% /game %}}                             |
| 🇦🇺 Australia      | 25.7 mil   | 9.2k            | 468k          | 1824             | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |

| Game                                                              | Count |
|-------------------------------------------------------------------|-------|
| {{% game 224517 %}}Brass: Birmingham{{% /game %}}                 | 14    |
| {{% game 174430 %}}Gloomhaven{{% /game %}}                        | 8     |
| {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}         | 6     |
| {{% game 342942 %}}Ark Nova{{% /game %}}                          | 5     |
| {{% game 233078 %}}Twilight Imperium: Fourth Edition{{% /game %}} | 4     |
| {{% game 167791 %}}Terraforming Mars{{% /game %}}                 | 3     |
| {{% game 115746 %}}War of the Ring: Second Edition{{% /game %}}   | 2     |
| {{% game 187645 %}}Star Wars: Rebellion{{% /game %}}              | 2     |
| {{% game 291457 %}}Gloomhaven: Jaws of the Lion{{% /game %}}      | 2     |

{{% bokeh "board_games_world_map.json" %}}
