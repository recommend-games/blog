---
title: "Measuring the Shut Up & Sit Down effect"
slug: susd-effect
author: Markus Shepherd
type: post
date: 2024-02-03T20:00:00+02:00
tags:
  - Shut Up & Sit Down
  - SU&SD
  - Synthetic Control
---

* Introduce SU&SD
* Mention the effect they have on board game sales
* Mention previous attempts at quantifying the effect
* John Company video
* Plot number of ratings before and after the video
* Can we attribute the increase to the video?
  * After all, it was pre-Xmas time, maybe people were just buying more games
* Enter Synthetic Control
* Explain briefly what it is and how it works
* Link to articles
* Synthetic Control with convex combination
* Print the weights
* Plot the results, both absolute and relative
* Is it significant? Fisher's exact test
* Other games absolute plot – maybe some with Ridge regression
* Conclusion

[Shut Up & Sit Down](https://www.shutupandsitdown.com/) (SU&SD) is arguably the largest (at over 400k subscribers) and most influential [YouTube channel](https://www.youtube.com/@shutupandsitdown) in board gaming. A video with a glowing recommendation by them can lead to a game sell out overnight. Or at least that's how the anecdotes go. There's been [previous attempts](https://www.reddit.com/r/boardgames/comments/ngqoow/i_tried_to_quantify_the_shut_up_sit_down_effect/) at quantifying the effect, but over here at Recommend.Games is where board games and data science meet, so obviously, we have to dig a little deeper.

Their recent review of {{% game 332686 %}}John Company{{% /game %}} is an interesting case study:

{{< youtube id="ykrqCX2_mhU" >}}

The game was by no means a hidden gem before: designer Cole Wehrle has two games in the BoardGameGeek (BGG) top 50 with {{% game 237182 %}}Root{{% /game %}} and {{% game 256960 %}}Pax Pamir{{% /game %}}, the latter being released by his own publishing house Wehrlegig Games as well. So it's fair to say that {{% game 332686 %}}John Company{{% /game %}} already had a lot of eyes on it. Still, when we look at the number of ratings on BGG, it's hard to deny the apparent increase in the slope after the video was released:

<!-- TODO: Plot number of ratings before and after the video -->
