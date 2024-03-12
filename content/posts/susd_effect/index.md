---
title: "Measuring the Shut Up & Sit Down effect"
slug: susd-effect
author: Markus Shepherd
type: post
date: 2024-03-01T20:00:00+02:00
tags:
  - Shut Up & Sit Down
  - SU&SD
  - Synthetic Control
---

[Shut Up & Sit Down](https://www.shutupandsitdown.com/) (SU&SD) is arguably the largest (at over 400k subscribers) and most influential [YouTube channel](https://www.youtube.com/@shutupandsitdown) in board gaming. A video with a glowing recommendation by them can lead to a game sell out overnight. Or at least that's how the anecdotes go. There's been [previous attempts](https://www.reddit.com/r/boardgames/comments/ngqoow/i_tried_to_quantify_the_shut_up_sit_down_effect/) at quantifying the effect, but over here at Recommend.Games is where board games and data science meet, so obviously, we have to dig a little deeper.

Their recent review of {{% game 332686 %}}John Company{{% /game %}} is an interesting case study:

{{< youtube id="ykrqCX2_mhU" >}}

The game was by no means a hidden gem before: designer Cole Wehrle has two games in the BoardGameGeek (BGG) top 50 with {{% game 237182 %}}Root{{% /game %}} and {{% game 256960 %}}Pax Pamir{{% /game %}}, the latter being released by his own publishing house Wehrlegig Games as well. So it's fair to say that {{% game 332686 %}}John Company{{% /game %}} already had a lot of eyes on it. Still, when we look at the number of ratings[^num_ratings] on BGG, it's hard to deny the apparent increase in the slope after the video was released:

{{< img src="332686_ratings" alt="Number of ratings of John Company before and after the SU&SD review" >}}

One might simply draw a line through the number of ratings before the video and extrapolate it to the present, then call the difference to the actual number of ratings the "Shut Up & Sit Down effect". But if you're reading this blog, your mind is probably of the kind that immediately goes: "Hang on, how do we know the increase is actually because of SU&SD and not because of some other unrelated reason?" The problem is that we don't have a "control world": one that has never been exposed to the video, but is otherwise identical to ours. These kinds of counterfactual questions are what keeps business analysts up at night (luckily that's not me, so writing blog posts like this one keeps me up instead 😅).

So how can we know that it really was the SU&SD video that drew the extra attention to the game and not, for instance, just the fact that we approached Christmas and people were just buying, playing and rating more games? 🤔

Enter [synthetic control](https://en.wikipedia.org/wiki/Synthetic_control_method). As said, we don't have a control world that wasn't exposed to the video – so instead we synthesise one! At first, this might sound more like alchemy than science, but the basic idea is really quite simple: we look at the number of ratings up to the day of the video and compare those to other, similar games over the time period. Because {{% game 332686 %}}John Company{{% /game %}} got the SU&SD treatment, but the other games didn't, we can reason that the same weighting of the other games' ratings should give us a good estimate of what would have happened to {{% game 332686 %}}John Company{{% /game %}} if it hadn't been for the video.

Line A  
Line B
Line C

* A
* B
* C

<!-- Explain the convex combination and print resulting weights -->
<!-- Plot synthetic control, both absolute and relative -->
<!-- Note: cannot exclude the possibility of a different "intervention", e.g., KS opened or fulfilled, some other review or social media mention, etc. -->
<!-- Is it significant? Fisher's exact test -->
<!-- Link to articles with further details and code with actual implementation -->
<!-- Other games, maybe include ridge regression too -->

[^num_ratings]: We use the number of ratings as a coarse proxy for interest. It's far from perfect, but it has the advantage of representing both positive and negative attention – and it's readily available from [this repository](https://github.com/beefsack/bgg-ranking-historicals).

<!-- Redo analysis with other source? Maybe number of collection items based on RatingItem.updated_at? -->
