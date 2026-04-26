---
title: Spiel des Jahres 2026 predictions
slug: spiel-des-jahres-2026-predictions
share_img: /posts/spiel-des-jahres-2026-predictions/sdj-all.webp
author: Markus Shepherd
type: post
date: 2026-05-17T00:05:57+03:00
tags:
  - SdJ
  - SdJ 2026
  - Spiel des Jahres
  - Spiel des Jahres 2026
  - KSdJ
  - Kennerspiel
  - Kennerspiel des Jahres
  - Kennerspiel des Jahres 2026
  - Game of the Year
  - Germany
  - Predictions
  - Spiel des Jahres predictions
  - Spiel des Jahres 2026 predictions
  - SdJ predictions
  - Kennerspiel predictions
  - Kennerspiel des Jahres predictions
  - Kennerspiel des Jahres 2026 predictions
---

{{< img src="sdj-all" size="x300" alt="Spiel des Jahres" >}}

{{% sdj %}}Spiel des Jahres 2026{{% /sdj %}} is around the corner! As [with]({{<ref "posts/sdj_2020/index.md">}}) [the]({{<ref "posts/sdj_2021/index.md">}}) [previous]({{<ref "posts/sdj_2022/index.md">}}) [six]({{<ref "posts/sdj_2023/index.md">}}) [years]({{<ref "posts/sdj_2025/index.md">}}), I'll try to predict what games have the best shot at ending up on the longlist (aka *recommendations*) and the shortlist (aka *nominations*) when the jury announces their picks on May 19th.

As every year, I'll let the algorithms speak, and I've doubled down on the path I've started [last year]({{<ref "posts/sdj_2025/index.md">}}) when I put more focus on jury members' reviews. Back then, I simply averaged all available reviews to obtain a proxy for the "jury review". The major problem with this are of course the gaps in the data for missing reviews. Luckily, we have a method to fill those gaps in the form of our [recommendation algorithm]({{<ref "posts/rg_collaborative_filtering/index.md">}}). So this year, I've put 50% of the weight on the individual recommendations for the 14 jury members and 50% on the ["recommendendations to the jury"](https://recommend.games/#/?for=S_d_J&excludeRated=false&yearMin=2025&yearMax=2026). This way, I was able to calculated a score for all eligible[^eligible] games. Our very own [Kennerspiel score]({{<ref "posts/kennerspiel/index.md">}}) is then used to sort those into their respective list of the top 10 contenders for either award. As always, you can find the complete code on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/sdj_2026) and the [complete results here](predictions.csv).

We have another year with some strong contenders. I think there's one clear nomination (though it's less clear on what list, more on that later), with the rest of the field pretty wide open. My predictions last year weren't particularly good, so the only way is up… 📈

But without further ado, here are the favourite games to win {{% sdj / %}} and {{% kdj %}}Kennerspiel des Jahres 2026{{% /kdj %}}.


# Candidates for {{% sdj %}}Spiel des Jahres 2026{{% /sdj %}}

{{< img src="sdj-2026" size="x300" alt="Spiel des Jahres 2026" >}}

<!-- TODO: Insert generated candidates from predictions.md here -->


# Candidates for {{% kdj %}}Kennerspiel des Jahres 2026{{% /kdj %}}

{{< img src="ksdj-2026" size="x300" alt="Kennerspiel des Jahres 2026" >}}

<!-- TODO: Insert generated candidates from predictions.md here -->


# My two cents

It's time for my picks for the nominations. The algorithms determined the longlist predictions, but my gut feeling takes over from here on.


## My predictions for nominees for {{% sdj %}}Spiel des Jahres 2026{{% /sdj %}}

* TODO

## My predictions for nominees for {{% kdj %}}Kennerspiel des Jahres 2026{{% /kdj %}}

* TODO


# Conclusion

Another year full of wonderful games – let's enjoy being spoiled for choice until the trade wars dry up the supplies. 🙈

Also, let's not forget {{% kindersdj / %}} – my daughters are now 5 and 6 years old, and we've already played through most of the back catalogue of past winners, so the whole family is looking forward to more great recommendations.

Stay tuned for the announcement on May 19th! 🤩


[^eligible]: As every year, it's not straightforward to determine what games are eligible for the awards. Generally speaking, it'd be those games release between April 2025 and March 2026 into German retail. Hence, filtering by BGG release year will exclude games that were released earlier elsewhere, but only recently in Germany, and likewise let some games pass that have not seen a German release in that time window. I did my best to catch what I could, but there's always some that get away.
