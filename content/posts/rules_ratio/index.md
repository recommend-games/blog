---
title: TODO
subtitle: TODO
slug: rules-ratio
author: Markus Shepherd
type: post
date: 2026-03-08T12:00:00+02:00
tags:
  - Rules ratio
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.2.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.8.2.min.js" ></script>

[W. Eric Martin](https://www.wericmartin.com), known for having run the BoardGameGeek (BGG) [news section](https://boardgamegeek.com/blog/1/boardgamegeek-news) for over a decade, recently launched his own outlet called [Board Game Beat](https://www.boardgamebeat.com).[^fediverse] In between his signature game release updates, he writes entertaining and insightful analyses of the broader hobby. In one of his [recent articles](https://www.wericmartin.com/the-rules-ratio-a-new-stat-to-geek-out-about/), he proposed the **Rules Ratio**. In his title, he invites us to geek out about it, so geek out we shall! 🤓


# What is the Rules Ratio?

TODO: Definition, intention, smoothing


# RR in the wild

TODO: Examples / top / bottom lists, plot

{{% bokeh "rules_ratio_vs_complexity.json" %}}


# RR vs complexity: the Residual Rules Ratio

TODO: RRW is right instinct (a higher complexity budget prices in more rules questions), but BGG complexity is not multiplicative. Instead: Regression model, residuals, more lists, plot. Unit: wem.

{{% bokeh "residual_rules_ratio_vs_complexity.json" %}}


# Summary / conclusion

Does it mean anything? I really hope it never will be taken serious enough just so the same people who do 1/10 rating bombs will create rules questions with the sole purpose of messing with games' RRs/RRRs.


# Appendix: Methodology

TODO: data etc.


[^fediverse]: [No tracking](https://www.wericmartin.com/board-game-beat-policies/). [Fediverse first](https://www.wericmartin.com/federated-social-media-video/).
