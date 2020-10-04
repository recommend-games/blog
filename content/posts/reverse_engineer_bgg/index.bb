[b][i]This post was originally published on the [url=https://blog.recommend.games/posts/reverse-engineering-boardgamegeek-ranking/]Recommend.Games blog[/url]. Check it out for more board game analyses![/i][/b]

[b][i]TL;DR[/i][/b]: [i]BoardGameGeek calculates its ranking by adding around [b]1500-1600 dummy ratings of 5.5[/b] to the regular users' ratings. They called it their geek score, statisticians call it a Bayesian average. We use this knowledge to calculate some alternative rankings.[/i]

I often describe [url=https://boardgamegeek.com/]BoardGameGeek (BGG)[/url] as "the [url=https://www.imdb.com/]Internet Movie Database (IMDb)[/url] for games". Much like its cinematic counterpart, the biggest board game database not only collects all sorts of information obsessively, but also allows users to rate games on a scale from 1 ([i]awful - defies game description[/i]) to 10 ([i]outstanding - will always enjoy playing[/i]). These ratings are then used to rank games, with [thing=174430]Gloomhaven[/thing] occupying the top spot since December 2017.

While BGG founder Scott Alden admitted in a recent interview on the excellent [url=https://fivegamesfordoomsday.com/2020/07/06/scott-alden/]Five Games For Doomsday[/url] podcast that he doesn't care all that much about the rankings, gamers around the world certainly do. They would discuss heatedly any movement in the rankings, question why games X is up there while game Y is missing, and generally criticise the selection for either having [i]too many[/i] or [i]not enough[/i] recent releases.

Reason enough for me to take a closer look at how the rankings work and some of the maths behind it.

Generally speaking, we want to rank a game higher the better its score is. The first instinct would be to just sum up all the ratings users gave to that particular game, divide by the number of ratings, and rank games from highest to lowest. What I just described would be the [i]arithmetic mean[/i] (or just [i]average[/i] if you feel less fancy) of the ratings, which is simple and intuitive, but suffers from a sever defect: a game with a single rating of 10 would always sit on top of the ranking, well ahead of much beloved games with thousands of votes that couldn't possibly be all 10s.

The easiest fix is filtering out games with less than a certain number of ratings, say 100. That's a decent enough approach, and yields the following top 5 games as of the time of writing:

1. [thing=261393]Dungeon Universalis[/thing]
2. [thing=219217]Arena: The Contest[/thing]
3. [thing=291457]Gloomhaven: Jaws of the Lion[/thing]
4. [thing=240271]Core Space[/thing]
5. [thing=209877]World At War 85: Storming the Gap[/thing]

Notably, those are all very recent games with relatively few ratings. Some might consider this a feature, not a bug, but when your intention is to create a list of the best board games, you probably do want to give a nod to proven classics, and not just the latest hotness. How to balance out these ends of the spectrum is in the end a choice you have to make, and no matter what it is, People on the Internet™ will not like it.

The way both IMDb and BGG chose to tackle this issue is by essentially not trusting the ratings – at least not too much. The method boils down to assigning a new item in the database (be it movie or game) a predefined average by default, and only gradually trusting the ratings' average as thousands and thousands of users have cast their votes. More concretely the rankings are calculated by adding a number of dummy ratings with a chosen average value, say 5.5, to each game's regular ratings. The result is that initially each game will have a score close to 5.5, but as more users rate the game, that score will move closer and closer to the conventional mean.

BGG calls this their [b]geek score[/b]. Mathematically speaking, it is a [i]Bayesian average[/i], and calculates as follows:

geek score = (sum of ratings + number of dummies * dummy value) / (number of ratings + number of dummies),

where sum of ratings can be calculated either by, well, summing up all ratings or via number of ratings * average rating. Don't worry too much about the details though – [i]adding dummy ratings[/i] is really all you need to understand.

OK, so that's the concept, but crucially that's not all the details. You still need to choose [i]how many[/i] dummy ratings you want to add and [i]what value[/i] they should take. Since People on the Internet™ who disagree with your ranking will try to manipulate it in whatever way they can, sites are usually very cagey about said details. [url=https://en.wikipedia.org/wiki/IMDb#Rankings]IMDb used to be more transparent[/url], [url=https://www.boardgamegeek.com/thread/103639/new-game-ranking-system]as was BGG[/url], but now we have to dig a little deeper.

Let's start from the easier of the two, the value of the dummy ratings. It is commonly chosen to represent some [i]prior mean[/i], i.e., some decent estimate of the rating a new game in the database would have. A frequent choice would be to use the average rating across [i]all[/i] games. It's a fair assumption – without further information about a game, we don't know if it's any better or worse than the average game. However, Scott Alden actually gave away the answer in that interview from the beginning: BGG chose the dummy value to be [b]5.5[/b]. Their rationale is that ratings range from 1 through 10, so 5.5 is the midpoint. Of course, people tend to rather play and rate much more the games they like, and so the average rating is around 7. Opting for the lower value here is part of the design of the ranking: it means a new game would enter the ranking rather at the end of the pack. On the other hand, using the mean as the dummy value means a new game is placed more or less in the middle. It is worth mentioning that IMBd does use the mean (or at least used to), but they only ever publish the top 250 movies, and don't care about the crowd behind.

The other value, the [i]number[/i] of dummy ratings, requires more work. Because some of the details and data are unknown, we cannot actually pin down the exact number that BGG is using. Instead, we'll try three different approaches, and compare their results.

[size=24][b]Formula[/b][/size]

On the surface, this should be super easy to solve: in the formula above, we know every single value but the number of dummy ratings. BGG publishes the number of ratings, their arithmetic mean, and the "geek score" or Bayesian average for every game, and we know that the dummy value is 5.5. With a little high school algebra we solve the formula for [i]number of dummies[/i]:

number of dummies = number of ratings * (average rating - geek score) / (geek score - dummy value).

Now we should be able to plug in those values for any given game, say [thing=199478]Flamme Rouge[/thing], and get the result. With 10,936 ratings that average 7.562, and a geek score of 7.266, this yield:

number of dummies = 10936 * (7.562 - 7.266) / (7.266 - 5.5) ≈ 1830.

So, there's about 1830 dummy ratings, end of story. Right? Unfortunately, not quite. When computing this formula for different games, the results vary [i]wildly[/i], as you can see from this histogram over the results for the same calculation with other games:

[IMG]https://blog.recommend.games/posts/reverse-engineering-boardgamegeek-ranking/num_dummies_hist.svg[/IMG]

And this plot is even cropped, the results vary from -1.4 million to +810 thousand, though some 90% lie within the above range, with a mean of around 1604 and a median of around 1590.

What's going on, why are the results so inconsistent? The problem is the ranking's [i]secret sauce[/i]. Both IMDb and BGG stress is that they only consider [i]regular[/i] voters for their rankings. That's the most mysterious part of the system as it's the easiest to manipulate, so we'll just have to take their word for it. For this investigation it means that the average rating BGG publishes includes all the ratings, but the geek score might [i]not[/i].

Still, clearly something is happening around the [b]1600 ratings[/b] mark, so we are at least getting closer to an answer. If exact calculations won't work, maybe we can approximate the correct value instead?

[size=24][b]Trial & error[/b][/size]

Let's take a step back here. What we're really trying to achieve here is not finding the exact formula for that mysterious "geek score", but rather recreate the BGG ranking. That is, we want to find the values in the above formula, such that the resulting ranking matches BGG's ranking as closely as possible. Luckily, statistics has all the tools we need. [url=https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient]Spearman correlation[/url] measures rank correlation – just what we need. This will be 1 if both rankings sort in exactly the same way, 0 if there's no relation, and -1 if they sort exactly the opposite way. Again, don't worry about the details, just trust the maths.

What we can do now is fairly simply and quickly compute the rankings for different number of dummy ratings, and pick the value with the highest Spearman correlation. Without further ado, here are the results:

[IMG]https://blog.recommend.games/posts/reverse-engineering-boardgamegeek-ranking/num_dummies_corr.svg[/IMG]

The best correlation of around 0.996 is achieved with [b]1488 dummy ratings[/b]. However, it is worth noticing that the changes in the correlation are very, [i]very[/i] small throughout the range we examined here (1000 to 2500), so let's dig still a little deeper.

[size=24][b]Optimisation[/b][/size]

What we have here at hand is actually a classic optimisation task: a real valued function in one unknown (or two if we allow a variable dummy value as well) which we'd like to maximise. This is a well-studied field, with many fast and simple implementations that provide us the solution in no time. Unsuprisingly, we get the same result as above: the best possible correlation is 0.996 with around [b]1488 dummy ratings[/b].

But since we made it this far, let's take it one step further. So far, we tried to optimise the correlation in order to recreate BGG's ranking. However, we can also try to recreate the actual [i]geek scores[/i]. That is, we can look for the number of dummy ratings that will yield the closest to the actual geek score with our calculations. What exactly we mean by "closest" is up to us to define. A common metric is the [i]mean squared error[/i]. It's not worth getting into the maths here either, but the general idea is that we want to punish outliers in our estimates more (qudratically so) the further away they lie from the actual datapoint. Long story short, this yields a minimum for around [b]1636 dummy ratings[/b].

Let's take one last swing and see what happens if we don't fix the dummy value at 5.5 but allow that to be variable as well. This is no problem for the optimisation algorithm and yields the following results:

* the best correlation with [b]1942 dummy ratings of 5.554[/b], and
* the least squared error with [b]1616 dummy ratings of 5.494[/b].

Either of those improvements in the performance metrics are hardly noticable (in fact insible after rounding), but they do confirm nicely a dummy value of 5.5.

[size=24][b]Conclusion[/b][/size]

All things consider, we can be confident that BoardGameGeek calculates their rankings by adding around [b]1500 to 1600 dummy ratings of 5.5[/b] to the regular users' ratings. What exactly constitutes a regular user, and what ratings might be discarded due to shilling, remains a well guarded secret though. Note that the number of dummies is pegged to the overall number of ratings, so this is a moving target, and the calculations would change as time passes.

Now I must applaud anybody who actually made it all the way through this pretty dry and technical article. The real reason why I dwelled so much on the ratings, and how they are compressed into the BGG rankings, is to get a feeling of what's going on behind the scenes, what the can express, and what they cannot or even [i]do not try to[/i] express. Another major take-away is that any of these decisions are choices that need to be made and that come with certain tradeoffs – like them or not.

In this particular case, I have the feeling that both the Cult of the New™ and connoisseurs of classic games are equally unhappy about the BGG top 100, which one should probably consider a compliment.

[size=24][b]Alternative rankings[/b][/size]

I'll send you off with some rankings that were obtained by making different choices for the two values that we discussed throughout this article: the number of dummy ratings and their value.

[size=18][b]Using the ratings average as dummy value[/b][/size]

I've mentioned before that the average rating across all games is around 7 – a little more precisely 7.08278. What if we chose that as the dummy rating, but left their number at 1600? The result should be a ranking that is a little friendlier to newer titles with fewer ratings as their score isn't dragged all the way down to 5.5 in the beginning.

1. [thing=174430]Gloomhaven[/thing]
2. [thing=161936]Pandemic Legacy: Season 1[/thing]
3. [thing=233078]Twilight Imperium (Fourth Edition)[/thing]
4. [thing=224517]Brass: Birmingham[/thing]
5. [thing=55690]Kingdom Death: Monster[/thing]
6. [thing=167791]Terraforming Mars[/thing]
7. [thing=291457]Gloomhaven: Jaws of the Lion[/thing]
8. [thing=220308]Gaia Project[/thing]
9. [thing=182028]Through the Ages: A New Story of Civilization[/thing]
10. [thing=187645]Star Wars: Rebellion[/thing]

Sure enough, the brand new [thing=291457]Jaws of the Lion[/thing] with less than 3000 ratings already shows up in the top 10. The other game that sticks out here is [thing=55690]Kingdom Death: Monster[/thing]. This Kickstarter success story clearly attracted a lot of enthusiasts, but not necessarily the mass.

[size=18][b]Using the top 250 number of ratings[/b][/size]

Just like IMDb publishes only their top 250 movies, we can consider the same and crank up the number of dummy ratings. A good number seems to be the 250th most rated game on BGG, which has been rated 12,014 times. Using BGG's standard dummy value of 5.5, we obtain a ranking that is much more skewed towards proven classics:

1. [thing=174430]Gloomhaven[/thing]
2. [thing=167791]Terraforming Mars[/thing]
3. [thing=161936]Pandemic Legacy: Season 1[/thing]
4. [thing=169786]Scythe[/thing]
5. [thing=12333]Twilight Struggle[/thing]
6. [thing=173346]7 Wonders Duel[/thing]
7. [thing=3076]Puerto Rico[/thing]
8. [thing=84876]The Castles of Burgundy[/thing]
9. [thing=31260]Agricola[/thing]
10. [thing=120677]Terra Mystica[/thing]

The most recent release on this list is [thing=174430]Gloomhaven[/thing], but we also meet again old BGG #1's: [thing=3076]Puerto Rico[/thing] and [thing=31260]Agricola[/thing].

[size=18][b]Combining both![/b][/size]

Finally, let's do what IMDb does (or used to do), and add to each game's ratings 12,014 dummy ratings of 7.08278:

1. [thing=174430]Gloomhaven[/thing]
2. [thing=161936]Pandemic Legacy: Season 1[/thing]
3. [thing=167791]Terraforming Mars[/thing]
4. [thing=169786]Scythe[/thing]
5. [thing=12333]Twilight Struggle[/thing]
6. [thing=224517]Brass: Birmingham[/thing]
7. [thing=182028]Through the Ages: A New Story of Civilization[/thing]
8. [thing=187645]Star Wars: Rebellion[/thing]
9. [thing=193738]Great Western Trail[/thing]
10. [thing=173346]7 Wonders Duel[/thing]

The effects of more, but higher dummy ratings seem to almost cancel each other out. Compared to BGG's actual top 10, only [thing=233078]Twilight Imperium[/thing] and [thing=220308]Gaia Project[/thing] are missing, otherwise this ranking looks very familiar. Turns out, BGG did a pretty good job designing its ranking!

[b][i]PS[/i][/b]: You can find the notebook I used to do all the calculations [url=https://www.kaggle.com/mshepherd/reverse-engineering-the-boardgamegeek-ranking]on Kaggle[/url].
