---
title: Spiel des Jahres 2025 predictions
slug: spiel-des-jahres-2025-predictions
author: Markus Shepherd
type: post
date: 2025-05-16T12:00:00+03:00
tags:
  - SdJ
  - SdJ 2025
  - Spiel des Jahres
  - Spiel des Jahres 2025
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Kennerspiel des Jahres 2025
  - Game of the Year
  - Germany
  - Predictions
  - Spiel des Jahres predictions
  - Spiel des Jahres 2025 predictions
  - SdJ predictions
  - Kennerspiel predictions
  - Kennerspiel des Jahres predictions
  - Kennerspiel des Jahres 2025 predictions
---

{{< img src="sdj-all" size="x300" alt="Spiel des Jahres" >}}

{{% sdj %}}Spiel des Jahres 2025{{% /sdj %}} is around the corner! As [with]({{<ref "posts/sdj_2020/index.md">}}) [the]({{<ref "posts/sdj_2021/index.md">}}) [previous]({{<ref "posts/sdj_2022/index.md">}}) [five]({{<ref "posts/sdj_2023/index.md">}}) [years]({{<ref "posts/sdj_2024/index.md">}}), I'll try to predict what games have the best shot at ending up on the longlist (aka *recommendations*) and the shortlist (aka *nominations*) when the jury announces their picks on May 20th.

As every year, I'll let the algorithms speak, and I've doubled down on the path I've started [last year]({{<ref "posts/sdj_2024/index.md">}}) when I put more focus on jury members' reviews. Back then, I simply averaged all available reviews to obtain a proxy for the "jury review". The major problem with this are of course the gaps in the data for missing reviews. Luckily, we have a method to fill those gaps in the form of our [recommendation algorithm]({{<ref "posts/rg_collaborative_filtering/index.md">}}). So this year, I've put 50% of the weight on the individual recommendations for the 14 jury members and 50% on the ["recommendendations to the jury"](https://recommend.games/#/?for=S_d_J&excludeRated=false&yearMin=2024&yearMax=2025). This way, I was able to calculated a score for all eligible[^eligible] games. Our very own [Kennerspiel score]({{<ref "posts/kennerspiel/index.md">}}) is then used to sort those into their respective list of the top 10 contenders for either award. As always, you can find the complete code on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/sdj_2025) and the [complete results here](predictions.csv).

TODO: Commentary on the year

But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2025{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2025{{% /sdj %}}

{{< img src="sdj-2025" size="x300" alt="Spiel des Jahres 2025" >}}

TODO


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2025{{% /kdj %}}

{{< img src="ksdj-2025" size="x300" alt="Kennerspiel des Jahres 2025" >}}

TODO


# My two cents

It's time for my picks for the nominations. As indicated in the introduction, I think the algorithm has done a pretty good at predicting the longlist, which means there's lots of strong contenders. Let's go with these predictions for the nominations:


## My predictions for nominees for {{% sdj %}}Spiel des Jahres 2025{{% /sdj %}}

* TODO

TODO


## My predictions for nominees for {{% kdj %}}Kennerspiel des Jahres 2025{{% /kdj %}}

* TODO

TODO


# Honourable mentions

Finally, I always like to sneak in a few more games that I think have a good shot at the longlist, even though the algorithm didn't place them in the top 10.

* TODO


# Conclusion

This year is set to be one that lives from its breadth rather than its depth. I'd say the race is pretty open in both awards, much more so than in previous years. While this makes my job as a predictor harder, as a board game fan I'm looking forward to the surprises that the jury will have in store for us.

With every passing year, I also get more and more excited about the picks for {{% kindersdj / %}} – so far all their recommendations were hits with my kids, and I can't wait to see what's the latest hotness in children's games.

Stay tuned for the announcement on June 11th! 🤩


[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2023 and March 2025 into German retail. Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
