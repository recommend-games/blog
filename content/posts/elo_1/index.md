---
title: Elo ratings explained
subtitle: How to measure players' skills in games
slug: elo-ratings-explained
author: Markus Shepherd
type: post
date: 2025-04-13T12:00:00+03:00
tags:
  - Elo rating
  - Snooker
---

## Introduction

> Chance in games is like seasoning in food — it's all about the right amount. Just imagine a life without chance, where everything could be planned out strategically. That would get boring over time. In a game, I want to have experiences — I want adventure. A good game is like a miniature life, one where I can make mistakes, enjoy a streak of bad or good luck, and still recover. But you shouldn't be at the mercy of randomness. There should be ways to compensate — like a friend of mine in CATAN, who always complains about his bad luck, prompting others to treat him more kindly and rarely target him with the robber. In the end, he often wins — to everyone's surprise. \
> — **Klaus Teuber** on the importance of randomness in games in [CATAN-News 1/2000](https://www.catan.de/sites/default/files/2021-11/dl_Catan-News-2000-1.pdf)

The balance between luck and skill in games can sometimes feel like a magic trick: the winner will attribute their victory to their great skills, whilst the losers can blame their misfortune on unlucky rolls of dice. Striking that balance right will have a major impact on the target audience of a game: if a game is totally random and offers no meaningful choices, it won't be interesting for anyone above a certain age (I'm still waiting for my kids to outgrow that phase 😅); if its learning curve is too steep, the upfront investment of navigating the strategic depths might put off many people who have an overflowing shelf of shame waiting to be played.

But how can we quantify luck and skills in games? It's a vast and deep topic – one about which I intend to write a small series. We'll start with a slightly simpler question: how can we measure *an individual player's skill* in a game? There's good reasons why one would want to do this (beyond writing articles about it):

- Tracking one's progress in learning the best strategies in a game: If I want to dive deep into a game, it's useful to understand how much I've advanced and what the road ahead might look like.
- Finding opponents which match one's skill level: If I were to play chess against Magnus Carlsen, I'd be crushed in no time and neither one of us would particularly enjoy the experience, nor would I learn anything from such a match. Many games are most fun if all players around the table are at a somewhat comparable level.
- Showing off one's skill level: People do love a good ranking – once we've put a number on players' skills, we can rank them and "objectively" determine who is the best. 🤓

Perhaps the best known and most widely adopted way to measure skills in games is the **Elo rating**, developed by and named[^no-acronym] after Arpad Elo, a Hungarian-American physics professor. As an avid chess player, Elo devised the system on behalf of the United States Chess Federation (USCF). The ideas behind it are very general though, and it has been adapted for other games, sports and online platforms such as [Board Game Arena](https://boardgamearena.com/). Reason enough for us to study and understand it.


## Key idea

First of all, the Elo rating system doesn't attempt to measure absolute, but relative skills. As such, it uses the difference in ratings between the two[^multi-player] players to try and predict the probability of one player winning or the other. So, the higher the rating difference between two players is, the more likely it is that the stronger player wins. As one might expect, players earn rating points through winning matches, but crucially, they earn more by winnining against stronger players and lose more by losing against weaker players. Elo ratings achieve this by compare the expected with the actual outcome. If you beat the odds and exceed expectations, your rating goes up; if you underperform, your rating goes down.

Consider this metaphor: imagine both players placing an ante of "skill chits" into the pot before the game begins. The higher your rating advantage over your opponent is, the higher your stake in the game. Conversely, if you're much lower rated, you don't have much too lose. The winner will take the whole pot, so if you can land an unexpected upset win, you're increasing your rating by a lot. A draw means splitting the pot, so you will still increase your rating in this case if you were expected to lose and hence put much less than 50% into the pot.


## Formula

Let's make this more concrete with formulae. Assume we have players *A* and *B* with some ratings \\(r_A\\) and \\(r_B\\). (I know it's a bit confusing to explain how to use the ratings before we explained how to calculate them, but just roll with it for a minute.) Then we can calculate \\(p_A\\), the probability that *A* will win the game, like this:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

If you've never seen a formula like this, it's probably a lot to digest, so let's take a minute to understand what's going on here. Whenever I encounter a formula like this, I like to first check that it makes any sense at all by plugging in some values. Notice how the important part about the ratings is just their difference \\(r_A-r_B\\), as mentioned before, so let's consider some case.

First: what if both players have the same skill level, i.e., that difference is 0? In this case, we'd have \\(p_A=\frac{1}{1+10^0}=\frac{1}{1+1}=0.5\\), i.e., both players having equal chances of winning, which checks out. Next, what if player *A* is so much higher rated that the difference tends towards infinity? The exponent contains a minus sign, and the exponential function tends to 0 for negative infinity, so we'd have \\(p_A=\frac{1}{1+10^{-\infty}}=\frac{1}{1+0}=1\\), i.e., player *A* would be all but guaranteed to win. Conversely, if the "infinite advantage" was on player *B*'s side, we'd have an exponential function that goes to infinity in the denominator, and hence the whole expression goint to 0, i.e., \\(p_A=0\\). (Note that we can get the probability of *B* winning simply by calculating \\(p_B=1-p_A\\), and all the formulae work analoguous, so we're not going to spend much attention to it.)

I hope this convinces you that this expression produces sensible probability values, if nothing else. To recap, this calculation would happen pre-match and give you a predicted probability that player *A* will win the match. (If you're the gambling kind, this might be how you determine your bet on *A*.) Once the match is over, we need to compare this prediction with the actual outcome or score \\(s_A\\), where \\(s_A = 1\\) if *A* won the game, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a draw. We then update *A*'s rating by

\\[ r_A \leftarrow r_A + K \cdot (s_A - p_A), \\]

where \\(K>0\\) is a factor we can freely choose. (More on this in a bit.)

Again, let's check if this makes sense. If *A* won, we have \\(s_A = 1\\), and so \\(s_A - p_A\\) will be positive. If player *A* was highly rated and so the win was expected, that difference will be very small and *A* will have their rating increased by only very few points, if the win was unexpected, i.e., \\(p_A\\) was low, then difference between predicted and actual outcome will be large and *A*'s rating will be increased by up to \\(K\\) points. If *A* lost, then \\(s_A = 0\\) and the difference will be negative, i.e., *A*'s rating will be decreased in the same way (and now *B* would receive those points).

Let's go back to our "skill chits pot" metaphor. In that view, player *A* would put \\(K \cdot p_A\\) chits into the ante, with player *B* contributing \\(K \cdot p_B = K \cdot (1-p_A)\\). The pot now holds \\(K\\) chits in total as reward for the winner. Because they paid \\(K \cdot p\\) chits as buy-in for the game, they've now gained \\(K \cdot (1 - p)\\) chits in total, which is exactly our update rule (remember that \\(s=1\\) for the winner).

This is really all there is to the Elo rating system. It's quite simple and interpretable, and players could easily keep track of their ratings with pen and paper back in the 1960s when the system was invented, well before computers and apps would rule the world.

I still owe you the details on some of the hyperparameters you can choose. First off, you might have noticed that 400 in the denominator of the exponent. This really could be any positive number – 400 is just a common choice, so I'm keeping with the convention here. I also didn't mention how to initialise the ratings, i.e., what rating to assign to new players before their first match. That's because it doesn't matter: the probability calculation only cares about the difference between the two ratings, so we could add any constant to both ratings, and they would just cancel out. The maths would work out easiest if we initialise new players with a rating of 0. This would have the charming side effect that it's immediately obvious if a player was an above or below average player depending if their rating was positive or negative. But I guess people don't like the feeling of having negative skills, so typically a value like 1300 or 1500 is added to the Elo ratings. Lastly, choosing that update factor \\(K\\) is very important if you want to have a meaningful ranking: Too low and ratings will take a very long time to converge and recent improvements in skills will take a long time to be reflected in the ratings. Too high and individual games will have too large an influence on the rating and the whole system will become too volatile. If you want to get a feeling of how to choose \\(K\\), I'll invite you to dive even deeper into the mathematics with me… 🤓


## Logistic regression

The most basic, but perhaps still most powerful tool at a machine learning practitioner's disposal is linear regression. We've encountered it already numerous times on this blog, e.g., in the context of understanding the [BoardGameGeek ranking]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}), explaining [collaborative filtering]({{<ref "posts/rg_collaborative_filtering/index.md">}}) and [debiasing the BGG ranking]({{<ref "posts/debiased_rankings/index.md">}}). In its basic form, it just describes a way of finding the "line of best fit" given some data points (e.g., observations). This works great if you want to predict a continous variable, i.e., values which can take a wide (potentially infinite) range. If you want to predict a binary outcome (e.g., *win* or *loss*) or a probability (e.g., the probability of one player winning), you usually use the *logistic function* (hence the name *logistic regression*) to squeeze the values of your predictions between 0 and 1:

\\[ f(x) = \frac{1}{1 + e^{-\beta x}}, \\]

Where \\(\beta>0\\). For \\(\beta=1\\), this function is better known as a *sigmoid* and looks like this:

**TODO: Plot of sigmoid**

If you plug in \\(x=r_A-r_B\\) and \\(\beta=\ln 10 / 400\\), we recover our update rule from above, so in a way, we're using logistic regression to predict player *A*'s win probability from the rating difference.

- Interpret Elo rating as logistic regression
- Derive update from stochastic gradient descent


## Strengths & weaknesses

- Positive:
  - It's pretty simple and fairly interpretable
  - It has a descent performance at predicting outcomes of, e.g., chess matches
- Caveats to using Elo:
  - Only meaningful in relative terms
  - Group needs to be sufficiently connected
  - Very sensitive to $$K$$ (tie back to logistic regression and the difficulty of picking a good learning rate)


## Example / application: Snooker

**Best factor this out into a separate article. Publish the general Elo article on 2025-04-13, and the Snooker article on 2025-04-19, in time for the opening of the World Snooker Championship.**

- World Championship opening today
- How does it apply to Snooker
- Sample calculations
- Winner prediction / simulation?
  - Use Elo ratings we just calculated to predict matches
  - Simulate tournaments where each match is decided according to Elo probability predictions
  - Who is going to be the next champion?


## Conclusion / outlook

- Summary
- What's next?
- Tease / outline the other articles

[^no-acronym]: Please note that Elo is a proper name and not an acronym, so please never ever spell it in all caps – it's disrespectful to the person who invented the rating system.
[^multi-player]: Since the Elo system was developed for chess, it's been originally formulated for two player zero-sum games only. For simplicity, we stick with that case for this article. There are various ways to generalise to multi-player settings and we shall examine those in future articles.
