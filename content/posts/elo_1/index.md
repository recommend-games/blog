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

- Explain formula, how to convert to probability and rating update
- Pot metaphor: players put $$p \cdot K$$ chits into the pot
- Discuss diffent choices of $$K$$
- Multi-player version?


## Logistic regression

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
