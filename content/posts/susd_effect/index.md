---
title: "Measuring the Shut Up & Sit Down effect"
subtitle: "Using synthetic control to make up our own counterfactual world"
slug: susd-effect
author: Markus Shepherd
type: post
date: 2024-03-01T20:00:00+02:00
tags:
  - Shut Up & Sit Down
  - SU&SD
  - Synthetic Control
  - John Company
  - Cole Wehrle
---


## Shut Up & Sit Down

[Shut Up & Sit Down](https://www.shutupandsitdown.com/) (SU&SD) is arguably the largest (at over 400k subscribers) and most influential [YouTube channel](https://www.youtube.com/@shutupandsitdown) in board gaming. A video with a glowing recommendation by them can lead to a game sell out overnight. Or at least that's how the anecdotes go. There's been [previous attempts](https://www.reddit.com/r/boardgames/comments/ngqoow/i_tried_to_quantify_the_shut_up_sit_down_effect/) at quantifying the effect, but over here at Recommend.Games is where board games and data science meet, so obviously, we have to dig a little deeper.


## John Company

Their recent review of {{% game 332686 %}}John Company{{% /game %}} is an interesting case study:

{{< youtube id="ykrqCX2_mhU" >}}

The game was by no means a hidden gem before: designer Cole Wehrle has two games in the BoardGameGeek (BGG) top 50 with {{% game 237182 %}}Root{{% /game %}} and {{% game 256960 %}}Pax Pamir{{% /game %}}, the latter being released by his own publishing house Wehrlegig Games as well. So it's fair to say that {{% game 332686 %}}John Company{{% /game %}} already had a lot of eyes on it. Still, when we look at the number of ratings[^num_ratings] on BGG, it's hard to deny the apparent increase in the slope after the video was released:

{{< img src="332686_ratings" alt="Number of ratings of John Company before and after the SU&SD review" >}}

One might simply draw a line through the number of ratings before the video and extrapolate it to the present, then call the difference to the actual number of ratings the "Shut Up & Sit Down effect". But if you're reading this blog, your mind is probably of the kind that immediately goes: "Hang on, how do we know the increase is actually because of SU&SD and not because of some other unrelated reason?" The problem is that we don't have a "control world": one that has never been exposed to the video, but is otherwise identical to ours. These kinds of counterfactual questions are what keeps business analysts up at night (luckily that's not me, so writing blog posts like this one keeps me up instead 😅).

So how can we know that it really was the SU&SD video that drew the extra attention to the game and not, for instance, just the fact that we approached Christmas and people were just buying, playing and rating more games? 🤔


## Synthetic Control

Enter [synthetic control](https://en.wikipedia.org/wiki/Synthetic_control_method). As said, we don't have a control world that wasn't exposed to the video – so instead we synthesise one! At first, this might sound more like alchemy than science, but the basic idea is really quite simple: we look at the number of ratings up to the day of the video and compare those to other, similar games over the time period. Because {{% game 332686 %}}John Company{{% /game %}} got the SU&SD treatment, but the other games didn't, we can reason that the same weighting of the other games' ratings should give us a good estimate of what would have happened to {{% game 332686 %}}John Company{{% /game %}} if it hadn't been for the video.

Concretely, we'll look at all the games on BGG and sample 300 of them that are most similar to {{% game 332686 %}}John Company{{% /game %}} in terms of the number of ratings before the video. We then try to find a convex combination of these games that best approximates the number of ratings of {{% game 332686 %}}John Company{{% /game %}} before the video. If this all sounds like gibberish, don't worry, just take my word for it that the algorithm spits out this model:

> **Synthetic {{% game 332686 %}}John Company{{% /game %}} =**  
> +30.7% * {{% game 356033 %}}Libertalia: Winds of Galecrest{{% /game %}}  
> +20.9% * {{% game 362986 %}}Tribes of the Wind{{% /game %}}  
> +18.3% * {{% game 340041 %}}Kingdomino Origins{{% /game %}}  
> +12.3% * {{% game 383206 %}}Freelancers: A Crossroads Game{{% /game %}}  
> +8.2% * {{% game 332772 %}}Revive{{% /game %}}  
> +5.5% * {{% game 315767 %}}Cartographers Heroes{{% /game %}}  
> +4.2% * {{% game 318182 %}}Imperium: Legends{{% /game %}}

It's worth stressing one thing: during training, the model only gets to see the number of ratings up to the review date. The idea is that the weighted sum of the ratings of those games are a "synthetic" version of {{% game 332686 %}}John Company{{% /game %}}. Since those games did not receive the SU&SD treatment, this synthetic gives a glimpse into a world, where that video was never made. Without further ado, this is what the fake ratings look like compared to the real ones:

{{< img src="332686_synthetic_control" alt="Number of ratings of John Company before and after the SU&SD review, compared to the synthetic control" >}}

So, it looks as though our synthetic {{% game 332686 %}}John Company{{% /game %}} would have continued to steadily gather attention, just without that bump in the days after the video's release. In the sixty days after the video, our synthetic {{% game 332686 %}}John Company{{% /game %}} received 498 new ratings, while the real one got 662. So it looks like the **SU&SD effect added about 164 ratings** to the game, which is **roughly a quarter** of all new ratings in that period.

Another way to visualise this effect is when we plot the difference between the real and the synthetic {{% game 332686 %}}John Company{{% /game %}}:

{{< img src="332686_susd_effect" alt="Difference between the number of ratings of John Company and the synthetic control before and after the SU&SD review: the SU&SD effect" >}}

Because the synthetic version is meant to approximate the number of ratings of the real numbers until the review is published, the plot dances around 0 in the left hand side. Right after the review, we see a steep incline for about a week, which then flattens out. This is the SU&SD effect in action.

The absolute numbers might not sound impressive for a video with over 300'000 views, but keep in mind that only a fraction of board game enthusiasts are active on BGG. Further, in an industry where a couple of thousand copies sold is considered a success, a couple of hundred additional ratings is nothing to sneeze at. Of course, whether this kind of activity on BGG translates to actual sales is a different question entirely.


## What about the other videos?

Obviously, this was just one video and one game. Can we see a similar effect in other games that SU&SD has covered? Let's check the same plot for some other videos.


### Noticeable increase 📈

Most games covered by SU&SD will see a clearly visible uplift in interest, such as {{% game 330592 %}}Phantom Ink{{% /game %}}. The model predicted interest to somewhat fizzle out, but the video introduced more players to the game:

{{< img src="330592_synthetic_control" alt="Number of ratings of Phantom Ink before and after the SU&SD review, compared to the synthetic control" >}}

The {{% game 351538 %}}Bamboo{{% /game %}} review produced a clear bump in interest, which then continued rather in parallel of the synthetic version after a couple of days:

{{< img src="351538_synthetic_control" alt="Number of ratings of Bamboo before and after the SU&SD review, compared to the synthetic control" >}}

Coverage of {{% game 276086 %}}Hamlet{{% /game %}} clearly led to a similar bump right after the review, but interest continue to rise afterwards:

{{< img src="276086_synthetic_control" alt="Number of ratings of Hamlet before and after the SU&SD review, compared to the synthetic control" >}}


### Supercharged 🚀

Some games, in particular hidden gems, really thrive under the spotlight SU&SD shines on them. {{% game 311031 %}}Five Three Five{{% /game %}} is one such example. Over 70% of the new ratings after the review can be attributed to its review:

{{< img src="311031_synthetic_control" alt="Number of ratings of Five Three Five before and after the SU&SD review, compared to the synthetic control" >}}

The number for {{% game 331571 %}}My Gold Mine{{% /game %}} is even close to 90%. This game was recommended by the [Spiel des Jahres]({{<ref "posts/sdj_2022_2/index.md">}}) jury, so hardly unknown, but clearly it needed SU&SD to introduce it to the English speaking world:

{{< img src="331571_synthetic_control" alt="Number of ratings of My Gold Mine before and after the SU&SD review, compared to the synthetic control" >}}

{{% game 367771 %}}Stomp the Plank{{% /game %}} is a children's game, a genre the BGG crowd generally ignores. Consequently, there was a steep incline in interest right after the review was published. It's interesting though that the model predicts a significant increase even without the video, so the SU&SD effect here is only about 33%:

{{< img src="367771_synthetic_control" alt="Number of ratings of Stomp the Plank before and after the SU&SD review, compared to the synthetic control" >}}


### No (or negative) effect 🫤

Interest in a game doesn't skyrocket in all cases after a SU&SD video, sometimes it seems to make hardly a difference – and some coverage might actually harm a game, even though SU&SD rarely releases truely negative reviews.

{{% game 298383 %}}Golem{{% /game %}}'s reception was definitely rather lackluster, and consequently ratings have gone up a little, but not dramatically:

{{< img src="298383_synthetic_control" alt="Number of ratings of Golem before and after the SU&SD review, compared to the synthetic control" >}}

{{% game 354568 %}}Amun-Re{{% /game %}} (another [Knizia classic]({{<ref "posts/high_society/index.md">}})) saw a bit of a typical SU&SD bump, but by end of the 60 day period we examined here, the effect had completely evaporated:

{{< img src="354568_synthetic_control" alt="Number of ratings of Amun-Re before and after the SU&SD review, compared to the synthetic control" >}}

SU&SD's video about {{% game 295770 %}}Frosthaven{{% /game %}} might have actually harmed that game…? 🤷 The site has been a vocal fan of the series, so the more plausible explanation for declining interest is probably rather saturation:

{{< img src="295770_synthetic_control" alt="Number of ratings of Frosthaven before and after the SU&SD review, compared to the synthetic control" >}}


### Full results

Here's an overview over most of the videos SU&SD has released in 2023 and the impact they had on the games they covered:

| Game | Review date | SU&SD effect | Plot |
| :--- | :---------: | -----------: | :--: |
| {{% game 332686 %}}John Company{{% /game %}} | 2023-11-28 | **+24.6%** | [[link]](332686_synthetic_control.svg) |
| {{% game 330592 %}}Phantom Ink{{% /game %}} | 2023-10-26 | **+43.5%** | [[link]](330592_synthetic_control.svg) |
| {{% game 368061 %}}Zoo Vadis{{% /game %}} | 2023-10-19 | **+64.9%** | [[link]](368061_synthetic_control.svg) |
| {{% game 358386 %}}Moon{{% /game %}} | 2023-10-12 | **+69.2%** | [[link]](358386_synthetic_control.svg) |
| {{% game 351538 %}}Bamboo{{% /game %}} | 2023-10-05 | **+50.3%** | [[link]](351538_synthetic_control.svg) |
| {{% game 350184 %}}Earth{{% /game %}} | 2023-09-28 | **-19.0%** | [[link]](350184_synthetic_control.svg) |
| {{% game 354568 %}}Amun-Re{{% /game %}} | 2023-09-22 | **+1.7%** | [[link]](354568_synthetic_control.svg) |
| {{% game 11 %}}Bohnanza{{% /game %}} | 2023-09-14 | **+20.9%** | [[link]](11_synthetic_control.svg) |
| {{% game 311031 %}}Five Three Five{{% /game %}} | 2023-08-23 | **+71.6%** | [[link]](311031_synthetic_control.svg) |
| {{% game 298383 %}}Golem{{% /game %}} | 2023-08-17 | **+12.8%** | [[link]](298383_synthetic_control.svg) |
| {{% game 386937 %}}Lacuna{{% /game %}} | 2023-08-03 | **+104.7%** | [[link]](386937_synthetic_control.svg) |
| {{% game 331571 %}}My Gold Mine{{% /game %}} | 2023-07-19 | **+89.6%** | [[link]](331571_synthetic_control.svg) |
| {{% game 367771 %}}Stomp the Plank{{% /game %}} | 2023-07-06 | **+33.2%** | [[link]](367771_synthetic_control.svg) |
| {{% game 177478 %}}IKI{{% /game %}} | 2023-06-29 | **+32.5%** | [[link]](177478_synthetic_control.svg) |
| {{% game 362944 %}}War of the Ring: The Card Game{{% /game %}} | 2023-06-15 | **+25.4%** | [[link]](362944_synthetic_control.svg) |
| {{% game 281549 %}}Beast{{% /game %}} | 2023-06-09 | **-18.6%** | [[link]](281549_synthetic_control.svg) |
| {{% game 276086 %}}Hamlet{{% /game %}} | 2023-05-25 | **+66.8%** | [[link]](276086_synthetic_control.svg) |
| {{% game 267609 %}}Guards of Atlantis II{{% /game %}} | 2023-05-18 | **+52.7%** | [[link]](267609_synthetic_control.svg) |
| {{% game 295770 %}}Frosthaven{{% /game %}} | 2023-05-11 | **-30.4%** | [[link]](295770_synthetic_control.svg) |
| {{% game 350205 %}}Horseless Carriage{{% /game %}} | 2023-02-09 | **+35.2%** | [[link]](350205_synthetic_control.svg) |
| {{% game 811 %}}Rummikub{{% /game %}} | 2023-01-26 | **-6.1%** | [[link]](811_synthetic_control.svg) |
| {{% game 366013 %}}Heat: Pedal to the Metal{{% /game %}} | 2022-12-22 | **+19.1%** | [[link]](366013_synthetic_control.svg) |

Even more detailed results can be found [here](results.json).

<!-- TODO: Pick a couple of representative plots, e.g., unknown and boosted, known and moderate effect, no or negative effect. -->
<!-- TODO: Result table for all (?) videos, conclusion about typical SU&SD effect. -->

<!-- Note: cannot exclude the possibility of a different "intervention", e.g., KS opened or fulfilled, some other review or social media mention, etc. -->
<!-- Link to articles with further details and code with actual implementation -->

[^num_ratings]: We use the number of ratings as a coarse proxy for interest. It's far from perfect, but it has the advantage of representing both positive and negative attention – and it's readily available from [this repository](https://github.com/beefsack/bgg-ranking-historicals).
<!-- TODO: Explain actual data source (collection items) better. -->
