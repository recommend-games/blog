---
title: The world of board games
subtitle: Board game rankings by country
slug: world-of-board-games
share_img: /posts/world-of-board-games/board_games_world_map.png
author: Markus Shepherd
type: post
date: 2024-04-25T23:02:24+03:00
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

With that out of the way, let's look at some basic statistics. For this analysis, we used **19.8 million ratings** by **347 thousand users** who selected one of the **199 countries** as their residence. Close to **88 thousand games** received at least one rating.

In order to understand how board game preferences differ around the globe, we want to calculate a ranking similar to the way BGG ranks games. Remember that BGG calculates their "[geek score]({{<ref "posts/reverse_engineer_bgg/index.md">}})" based on a Bayesian average by adding a number of dummy ratings of 5.5 to each game. That [number of dummy ratings]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}) is determined by the total number of ratings divided by 10,000. We can apply exactly the same logic to calculate a ranking by country. Since we want to apply at least one dummy rating to each game, we only consider countries with at least 10,000 ratings in total – **62 countries** meet this criterion. BGG ranks games with at least 30 ratings. If we applied the same rule to the country rankings, we would often have very short lists. So, I decided to include games with at least 3 times the number of dummy ratings in the country ranking, but never more than the BGG standard of 30.

Enough of the boring technicalities, on to the fun part! 😎 Let's first answer some basic questions: How many users from that country? How many ratings have the entered? How many ratings per capita? And maybe most interestingly: What is their favourite game? Here's a quick overview over the 10 largest communities on BGG:

| Country           | Population | Users  | Ratings | Per 100k residents | #1 rated game                                                                 |
|:------------------|-----------:|-------:|--------:|-------------------:|:------------------------------------------------------------------------------|
| **🇺🇸 United States**  | 331.9 mil  | 131.7k | 7,724k   | 2,327               | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |
| **🇩🇪 Germany**        | 83.2 mil   | 19.0k  | 1,457k   | 1,751               | {{% game 342942 %}}Ark Nova{{% /game %}}                                      |
| **🇨🇦 Canada**         | 38.2 mil   | 23.4k  | 1,390k   | 3,636               | {{% game 174430 %}}Gloomhaven{{% /game %}}                                    |
| **🇬🇧 United Kingdom** | 67.3 mil   | 24.3k  | 1,300k   | 1,931               | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |
| **🇪🇸 Spain**          | 47.4 mil   | 16.0k  | 913k    | 1,926               | {{% game 224517 %}}Brass: Birmingham{{% /game %}}                             |
| **🇵🇱 Poland**         | 37.7 mil   | 11.8k  | 620k    | 1,644               | {{% game 187645 %}}Star Wars: Rebellion{{% /game %}}                          |
| **🇮🇹 Italy**          | 59.1 mil   | 9.1k   | 550k    | 930                | {{% game 182028 %}}Through the Ages: A New Story of Civilization{{% /game %}} |
| **🇫🇷 France**         | 67.7 mil   | 10.6k  | 529k    | 782                | {{% game 342942 %}}Ark Nova{{% /game %}}                                      |
| **🇳🇱 Netherlands**    | 17.5 mil   | 7.5k   | 469k    | 2,680               | {{% game 224517 %}}Brass: Birmingham{{% /game %}}                             |
| **🇦🇺 Australia**      | 25.7 mil   | 9.2k   | 468k    | 1,824               | {{% game 161936 %}}Pandemic Legacy: Season 1{{% /game %}}                     |

We see lots of familiar names amongst the highest rated games. The 62 country rankings have 26 different games in the top spot. These nine games are favourites in more than one country:

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

This looks almost identical to the BGG top 10 list – only {{% game 316554 %}}Dune: Imperium{{% /game %}} is missing, though it is 🇦🇷 Argentina's favourite game. Overall, the country rankings are dominated by international hits, but there are a couple of local favourites with a strong tie to the country, such as {{% game 188 %}}Go{{% /game %}} in 🇨🇳 China and {{% game 368789 %}}AFU: Armed Forces of Ukraine{{% /game %}} in 🇺🇦 Ukraine.

Explore more details about the different countries in this interactive map:

{{% bokeh "board_games_world_map.json" %}}

As much fun as it is to browse the map, there's also the blank spaces staring in our faces: Africa and South Asia, together representing over 40% of the world's population, are almost completely missing from the international board gaming community. 🌍 Obviously, BGG being an American website only available in English means their data really only represents the Anglo-American gaming world, but still, it's notable how Latin America and other parts of Asia are present much stronger on BGG. I think some focus and effort needs to go into closing those gaps on the world map. 🕊️

I couldn't possibly leave you without circling back to the question of what country is the most enthusiastic about board games. We've already mentioned the statistical anomalities that are the 🇻🇦 Vatican and 🇦🇶 Antarctica, but if we only consider the 62 countries with their own rankings, which of those has the most ratings per capita? Here's the top 5:

1. **🇫🇮 Finland** (4953 per 100k residents)
2. **🇮🇸 Iceland** (4932 per 100k residents)
3. **🇨🇦 Canada** (3636 per 100k residents)
4. **🇧🇪 Belgium** (3575 per 100k residents)
5. **🇸🇪 Sweden** (3337 per 100k residents)

Those who were looking for the reason why my chosen home is the [happiest country in the world](https://yle.fi/a/74-20080027) [🗄️](https://web.archive.org/web/https://yle.fi/a/74-20080027), you've finally got the answers: we seem to play more board games than anyone else! (*Torille! 🇫🇮*) In general, the Nordic countries sure hit the sweet spot here, with their highly educated populations (well versed in English) and strong emphasis on work–life balance. Also, you gotta have something to do during those long, dark winter nights. 🌌

Finally, if you're interested in the full country overview, you can find it [here](countries.csv). Browse the full rankings for each country here:

[🇦🇷 Argentina](rankings/ar.csv) | [🇦🇺 Australia](rankings/au.csv) | [🇦🇹 Austria](rankings/at.csv) | [🇧🇾 Belarus](rankings/by.csv) | [🇧🇪 Belgium](rankings/be.csv) | [🇧🇷 Brazil](rankings/br.csv) | [🇧🇬 Bulgaria](rankings/bg.csv) | [🇨🇦 Canada](rankings/ca.csv) | [🇨🇱 Chile](rankings/cl.csv) | [🇨🇳 China](rankings/cn.csv) | [🇨🇴 Colombia](rankings/co.csv) | [🇨🇷 Costa Rica](rankings/cr.csv) | [🇭🇷 Croatia](rankings/hr.csv) | [🇨🇿 Czechia](rankings/cz.csv) | [🇩🇰 Denmark](rankings/dk.csv) | [🇪🇪 Estonia](rankings/ee.csv) | [🇫🇮 Finland](rankings/fi.csv) | [🇫🇷 France](rankings/fr.csv) | [🇩🇪 Germany](rankings/de.csv) | [🇬🇷 Greece](rankings/gr.csv) | [🇭🇰 Hong Kong](rankings/hk.csv) | [🇭🇺 Hungary](rankings/hu.csv) | [🇮🇸 Iceland](rankings/is.csv) | [🇮🇳 India](rankings/in.csv) | [🇮🇩 Indonesia](rankings/id.csv) | [🇮🇷 Iran](rankings/ir.csv) | [🇮🇪 Ireland](rankings/ie.csv) | [🇮🇱 Israel](rankings/il.csv) | [🇮🇹 Italy](rankings/it.csv) | [🇯🇵 Japan](rankings/jp.csv) | [🇱🇻 Latvia](rankings/lv.csv) | [🇱🇹 Lithuania](rankings/lt.csv) | [🇱🇺 Luxembourg](rankings/lu.csv) | [🇲🇾 Malaysia](rankings/my.csv) | [🇲🇽 Mexico](rankings/mx.csv) | [🇳🇱 Netherlands](rankings/nl.csv) | [🇳🇿 New Zealand](rankings/nz.csv) | [🇳🇴 Norway](rankings/no.csv) | [🇵🇪 Peru](rankings/pe.csv) | [🇵🇭 Philippines](rankings/ph.csv) | [🇵🇱 Poland](rankings/pl.csv) | [🇵🇹 Portugal](rankings/pt.csv) | [🇷🇴 Romania](rankings/ro.csv) | [🇷🇺 Russia](rankings/ru.csv) | [🇷🇸 Serbia](rankings/rs.csv) | [🇸🇬 Singapore](rankings/sg.csv) | [🇸🇰 Slovakia](rankings/sk.csv) | [🇸🇮 Slovenia](rankings/si.csv) | [🇿🇦 South Africa](rankings/za.csv) | [🇰🇷 South Korea](rankings/kr.csv) | [🇪🇸 Spain](rankings/es.csv) | [🇸🇪 Sweden](rankings/se.csv) | [🇨🇭 Switzerland](rankings/ch.csv) | [🇹🇼 Taiwan](rankings/tw.csv) | [🇹🇭 Thailand](rankings/th.csv) | [🇹🇷 Türkiye](rankings/tr.csv) | [🇺🇦 Ukraine](rankings/ua.csv) | [🇦🇪 United Arab Emirates](rankings/ae.csv) | [🇬🇧 United Kingdom](rankings/gb.csv) | [🇺🇸 United States](rankings/us.csv) | [🇺🇾 Uruguay](rankings/uy.csv) | [🇻🇳 Vietnam](rankings/vn.csv)

*PS: As always, the complete code for this analysis can be found from [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/rankings_by_country).*
