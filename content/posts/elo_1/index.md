---
title: Elo ratings explained
subtitle: How to measure players' skills in games
slug: elo-ratings-explained
author: Markus Shepherd
type: post
date: 2025-04-14T23:07:10+03:00
tags:
  - Elo rating
  - Snooker
---

> Chance in games is like seasoning in food — it's all about the right amount. Just imagine a life without chance, where everything could be planned out strategically. That would get boring over time. In a game, I want to have experiences — I want adventure. A good game is like a miniature life, one where I can make mistakes, enjoy a streak of bad or good luck, and still recover. But you shouldn't be at the mercy of randomness. There should be ways to compensate — like a friend of mine in CATAN, who always complains about his bad luck, prompting others to treat him more kindly and rarely target him with the robber. In the end, he often wins — to everyone's surprise. \
> — **Klaus Teuber** on the importance of randomness in games in [CATAN-News 1/2000](https://www.catan.de/sites/default/files/2021-11/dl_Catan-News-2000-1.pdf)

The balance between luck and skill in games can sometimes feel like a magic trick: as the winner, you might attribute your victory to your great skills, whilst as the loser, you can blame your misfortune on unlucky dice rolls. Striking that balance right will have a major impact on the target audience of a game: if a game is totally random and offers no meaningful choices, it won't be interesting for anyone above a certain age (I'm still waiting for my kids to outgrow that phase 😅); if its learning curve is too steep, the upfront investment of navigating the strategic depths might put off many people who have an overflowing shelf of shame waiting to be played.

But how can we quantify luck and skills in games? It's a vast and deep topic – one which I want to explore in a small series. We'll start with a slightly simpler question: how can you measure *your skill* in a game? There are good reasons why you would want to do this (beyond writing articles about it):

- Tracking your progress in learning the best strategies in a game: If you want to dive deep into a game, it's useful to understand how much you've advanced and what the road ahead might look like.
- Finding opponents who match your skill level: If you were to play chess against Magnus Carlsen, you'd be crushed in no time and neither one of you would particularly enjoy the experience, nor would you learn anything from such a match. Many games are most fun if all players around the table are at a somewhat comparable level.
- Showing off your skill level: People do love a good ranking – once we've put a number on your skills, we can rank them and "objectively" determine who is the best. 🤓

Perhaps the best known and most widely adopted way to measure skills in games is the **Elo rating**, developed by and named[^no-acronym] after Arpad Elo, a Hungarian-American physics professor. As an avid chess player, Elo devised the system on behalf of the United States Chess Federation (USCF). The ideas behind it are very general though, and it has been adapted for other games, sports and online platforms such as [Board Game Arena](https://boardgamearena.com/). Reason enough for us to study and understand it.


## How Elo turns match results into skill ratings

First of all, the Elo rating system doesn't attempt to measure absolute, but relative skills. As such, it uses the difference in ratings between the two[^multi-player] players to try and predict the probability of one player winning or the other. So, the higher the rating difference between two players is, the more likely it is that the stronger player wins. As you might expect, you earn rating points by winning matches, but crucially, you earn more by winning against stronger players and lose more by losing against weaker players. Elo ratings achieve this by comparing the expected with the actual outcome. If you beat the odds and exceed expectations, your rating goes up; if you underperform, your rating goes down.

Consider this metaphor: imagine both players placing an ante of "skill chits" into the pot before the game begins. The higher your rating advantage over your opponent is, the higher your stake in the game. Conversely, if you're much lower rated, you don't have much to lose. The winner will take the whole pot, so if you can land an unexpected upset win, you're increasing your rating by a lot. A draw means splitting the pot, so you will still increase your rating in this case if you were expected to lose and hence put much less than 50% into the pot.


## The maths behind the magic: Elo's core formula

Let's make this more concrete with formulae. Assume we have players *A* and *B* with some ratings \\(r_A\\) and \\(r_B\\). (I know it's a bit confusing to explain how to use the ratings before we explained how to calculate them, but just roll with it for a minute.) Then we can calculate \\(p_A\\), the probability that *A* will win the game, like this:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

If you've never seen a formula like this, it's probably a lot to digest. Notice how the important part about the ratings is just their difference \\(r_A-r_B\\), so we can consider that rating difference as the single input variable. As the saying goes, a picture is worth a thousand words, so here's the plot of that function:

{{< img src="elo_probabilities" alt="A plot of the win probabilities depending on the rating differences" >}}

It's also instructive to get a feeling of how rating differences translate into winning probabilities by plugging in some values into the formula:

| Rating difference \\(r_A-r_B\\) | Win probability \\(p_A\\) |
|------:|-------:|
|    ±0 |  50.0% |
|  +100 |  64.0% |
|  +200 |  76.0% |
|  +300 |  84.9% |
|  +400 |  90.9% |
|  +800 |  99.0% |
|  \\(+\infty\\) | 100.0% |

Note that we can get the probability of *B* winning simply by calculating \\(p_B=1-p_A\\), and all the formulae work analogous, so we're just going to focus on player *A*'s perspective.

To recap, this calculation would happen pre-match and give you a predicted probability that player *A* will win the match. (If you're the gambling kind, this might be how you determine your bet on *A*.) Once the match is over, we need to compare this prediction with the actual outcome or score \\(s_A\\), where \\(s_A = 1\\) if *A* won the game, \\(s_A = 0\\) if they lost and \\(s_A = 0.5\\) in case of a draw. We then update *A*'s rating by

\\[ r_A \leftarrow r_A + K (s_A - p_A), \\]

where \\(K>0\\) is a factor we can freely choose. (*Much* more on this soon.)

Again, let's check if this makes sense. If *A* won, we have \\(s_A = 1\\), and so \\(s_A - p_A\\) will be positive. If player *A* was highly rated and so the win was expected, that difference will be very small and *A* will have their rating increased by only very few points, if the win was unexpected, i.e., \\(p_A\\) was low, then difference between predicted and actual outcome will be large and *A*'s rating will be increased by up to \\(K\\) points. If *A* lost, then \\(s_A = 0\\) and the difference will be negative, i.e., *A*'s rating will be decreased in the same way (and now *B* would receive those points).

Let's go back to our "skill chits pot" metaphor. In that view, player *A* would put \\(K p_A\\) chits into the ante, with player *B* contributing \\(K p_B = K (1-p_A)\\). The pot now holds \\(K\\) chits in total as reward for the winner. Because they paid \\(K p\\) chits as buy-in for the game, they've now gained \\(K (1 - p)\\) chits in total, which is exactly our update rule (remember that \\(s=1\\) for the winner).

This is really all there is to the Elo rating system. It's quite simple and interpretable, and you could easily keep track of your ratings with pen and paper back in the 1960s when the system was invented, well before computers and apps would rule the world.


### Setting the dials: scaling, initial ratings and update factor

I still owe you the details on some of the hyperparameters we can choose.

- *Rating scale*: You might have noticed that 400 in the denominator of the exponent. This really could be any positive number – 400 is just a common choice, so I'm keeping with the convention here.
- *Initial rating*: I also glossed over the question of how to initialise the ratings, i.e., what rating to assign to new players before their first match. That's because it doesn't matter: the probability calculation only cares about the difference between the two ratings, so you could add any constant to both ratings, and they would just cancel out. The maths works out easiest if you initialise new players with a rating of 0 (and we shall stick with that), but in real world application a value like 1300 or 1500 is typically added to the Elo ratings. I guess people don't like the feeling of having negative skills.
- *Update factor \\(K\\)*: Finally, choosing that update factor \\(K\\) is very important if you want to have a meaningful ranking: Too low and ratings will take a very long time to converge and recent improvements in skills will take a long time to be reflected in the ratings. Too high and individual games will have too large an influence on the rating and the whole system will become too volatile.

If you want develop an intuition about the importance of \\(K\\), I'll invite you to dive even deeper into the mathematics with me… 🤓 (Feel free to skip the next section if the thought of calculating partial derivatives of the formulae so far sounds like horror to you.)


## Elo as logistic regression: a machine learning perspective

The most basic, but perhaps still most powerful tool at a machine learning practitioner's disposal is linear regression. We've encountered it already numerous times on this blog, e.g., in the context of understanding the [BoardGameGeek ranking]({{<ref "posts/reverse_engineer_bgg_2/index.md">}}), explaining [collaborative filtering]({{<ref "posts/rg_collaborative_filtering/index.md">}}) and [debiasing the BGG ranking]({{<ref "posts/debiased_rankings/index.md">}}). In its basic form, it just describes a way of finding the "line of best fit" given some data points (e.g., observations). This works great if you want to predict a continuous variable, i.e., values which can take a wide (potentially infinite) range. If you want to predict a binary outcome (e.g., *win* or *loss*) or a probability (e.g., the probability of one player winning), you usually use the *logistic function* (hence the name *logistic regression*) to squeeze the values of your predictions between 0 and 1:

\\[ \sigma_\lambda(x) = \frac{1}{1 + e^{-\lambda x}}, \\]

where \\(\lambda>0\\). For \\(\lambda=1\\), this function is better known as a *sigmoid* and looks like this:

{{< img src="sigmoid" alt="A plot of the sigmoid function" >}}

That plot should look familiar to you from the Elo probabilities. That's because you'll recover our formula for \\(p_A\\) from above if you plug in \\(x=r_A-r_B\\) and \\(\lambda=\ln 10 / 400\\), so in a way, we're using logistic regression to predict player *A*'s win probability from the rating difference.

The sigmoid has a particularly nice derivative:

\\[ \sigma'_1(x) = \sigma_1(x) (1 - \sigma_1(x)). \\]

Using standard calculus, you can easily find the derivative for the general logistic function from this:

\\[ \sigma'_ \lambda(x) = \lambda \sigma_\lambda(x) (1 - \sigma_\lambda(x)). \\]

Remember: what we're really trying to achieve is calculate the win probability \\(p_A\\) from the rating difference such that it predicts the actual outcome \\(s_A\\) (which will be 1 if *A* wins and 0 if they lose) as closely as possible. This is a classic case for a *maximum likelihood estimation*: we want to select a parameter (in this case the rating \\(r_A\\)) such that the observed data (the actual outcome \\(s_A\\) of the game) is most probable. If you want to prove just how fancy you are, you say a random variable \\(X\\) with a binary outcome follows a *Bernoulli distribution* with parameter \\(p\in[0,1]\\) (the probability of a success). Its probability mass function is then given by

\\[ P(X = s) = p^s (1 - p)^{1-s}, \\]

where \\(s\in\\{0,1\\}\\) is the outcome. As usual, let's check what's going on here: for \\(s=1\\), the second factor will be \\((1 - p)^0=1\\) and hence the whole expression will be \\(p\\). Conversely, for \\(s=0\\), the first factor will be \\(p^0=1\\), so we have \\(1-p\\) overall, as desired. We can use this formula to write down the likelihood function

\\[ L(r_A) = p_A^{s_A} (1 - p_A)^{1-s_A}, \\]

keeping in mind that \\(p_A\\), our estimate for the probability that *A* will win, depends on their rating \\(r_A\\) via the formula we established a couple of hundred words ago. So, we want to choose \\(r_A\\) such that \\(L(r_A)\\) will be maximised for the given observation of game outcomes. If you remember your calculus 101, you'll know that the easiest way to maximise a function is by taking its derivative. For this purpose, it's often convenient to turn products into sums by applying logarithms. When searching for optimal points, that's OK since logarithms are monotonic. We hence arrive at the log-likelihood function:

\\[ \ell(r_A) = \ln L(r_A) = s_A \ln p_A + (1 - s_A) \ln (1 - p_A). \\]

In our case, we just receive a single observation (the outcome of a game), and immediately want to update \\(r_A\\) afterwards, which makes it a good candidate for *stochastic gradient ascent*[^descent]. This means we'll update \\(r_A\\) after each game by taking a step of size \\(\alpha>0\\) towards the gradient of \\(\ell\\) with respect to \\(r_A\\):

\\[ r_A \leftarrow r_A + \alpha \frac{\partial\ell}{\partial r_A}. \\]

So, let's roll up our sleeves and calculate said derivative. Using \\(\frac{\partial}{\partial x}\ln f(x)=\frac{f'(x)}{f(x)}\\), we have:

\\[ \frac{\partial\ell}{\partial r_A} = s_A \frac{p'_ A}{p_A} + (1 - s_A) \frac{-p'_ A}{1-p_A}. \\]

Remember now that \\(p_A=\sigma_\lambda(r_A-r_B)\\) and the derivative of the logistic function

\\[ \sigma'_ \lambda(x) = \lambda \sigma_\lambda(x) (1 - \sigma_\lambda(x)), \\]

hence

\\[ p'_ A = \lambda p_A (1 - p_A). \\]

Plugging this in yields:

\\[ \frac{\partial\ell}{\partial r_A} = s_A \frac{\lambda p_A (1 - p_A)}{p_A} - (1 - s_A) \frac{\lambda p_A (1 - p_A)}{1-p_A} \\\\
= \lambda s_A (1 - p_A) - \lambda (1 - s_A) p_A \\\\
= \lambda s_A - \lambda s_A p_A - \lambda p_A + \lambda s_A p_A \\\\
= \lambda (s_A - p_A). \\]

Using this in the stochastic gradient ascent update rule, we finally obtain

\\[ r_A \leftarrow r_A + \alpha \lambda (s_A - p_A), \\]

which is exactly the Elo update if we choose \\(K=\alpha\lambda\\). Remember that \\(\lambda=\ln 10 / 400\\) if we go with the standard Elo scale, so it's really just a constant for all intents and purposes. The step size \\(\alpha\\) on the other hand comes from gradient ascent, and anybody working in machine learning will tell you that choosing a good step size is a science and an art in and of itself. Too small, and your model will take a long time to converge; too large and it might diverge – that's why one can think of \\(K\\) as the step size in the Elo rating update. (See? I wasn't lying when I told you we'd dive *deep* into the maths to understand the importance of getting \\(K\\) right. 🤓)


## What Elo gets right — and where it falls short

I've already spent over 2500 words on describing how the Elo rating works, but haven't even discussed yet if it's any good. 😅 As I've already mentioned, the Elo rating system definitely has its relative simplicity going for itself. The previous section might have managed to conceal the fact that the calculations and applications are pretty straightforward and interpretable. For a system which is meant to communicate the abstract notion of "skill" to humans, this is no small feat.

Arguably the most important success criterion for the Elo ratings is their predictive power. After all, if they can somewhat reliably tell us who is going to win a match, very little else matters. And indeed, it appears that empirically Elo ratings do a decent job at that. Other systems have been devised which show greater success, and if you're in the business of calculating the right odds for your next gamble, you're probably interested in those, but no system is as simple and widely adopted as the Elo ratings.

Let's look at some of its downsides though. As with any model, it's a simplification which is only as good as the assumptions that go into it. Maybe the biggest caveat of this system is that it's only meaningful within a given population of players. Remember that Elo measures the relative strengths of players, which should also hold transitively, i.e., it's not necessary for every player to play against all other players. But if two groups of players are not at all or insufficiently connected, the ratings between those groups won't be comparable. In general, Elo ratings can only measure the distribution of skills amongst active participants. If it was only chess grandmasters playing each other, some of their ratings would suffer and look very low in absolute terms, even though they'd easily defeat almost any other chess player on this planet.

It's also worth mentioning that the system as presented does not require or encourage active participation. Elo rating points are earned or lost only after matches, so if you stop playing, your rating would just be frozen. You might choose to do something like this if you have reached a particularly high (potentially top) rating and do not want to risk deteriorating it. This is an example of the classic moniker: *once a metric becomes a target, it ceases to be a good metric*. Elo ratings want to measure skill, but once earning a high rating becomes the primary motivation, they stop being good predictors.

Finally, and you might have picked up on that by now, it's really important but difficult to choose a good update factor \\(K\\). What exactly constitutes "good" very much depends on the size and activity of the community, the nature of the game, but also what you want to use the ratings for. For instance, it's common to use a larger \\(K\\) for new players so they reach a rating faster which is more meaningful than the initial value. In general, the volatility a larger \\(K\\) brings to a ranking might be desirable if that dynamic is more important to the community than perfect predictions from rating differences.


## Wrapping up — and what comes next

Wow, I intended for this article to just be a brief introduction to the topic of Elo ratings, mostly motivated by future articles I want to write in this series. But Elo ratings are super interesting in their own right and I hope you understand them better now. I think I've done a good job if you take away from this article that Elo ratings measure the relative skills between players and can be used to predict the win probabilities before the match. Afterwards, ratings will be updated depending on if a player exceeded expectations or fell short. If you were able to follow through all of my little logistic regression detour, you will also understand that the update factor \\(K\\) can be thought of as the step size in the gradient ascent step.

You might have noticed and already complained that I didn't give a single concrete example of Elo ratings in this whole long article. I hope to follow up with an article entirely dedicated to that, so stay tuned.

I also want to shift the view back from players' individual strengths to the overall distribution of ratings in order to answer the initial question of how we can quantify luck and skills in games in general. That's going to get even more scientific, so hold on tight! 🧑‍🔬


[^no-acronym]: Please note that Elo is a proper name and not an acronym, so please never ever spell it in all caps – it's disrespectful to the person who invented the rating system.
[^multi-player]: Since the Elo system was developed for chess, it's been originally formulated for two player zero-sum games only. For simplicity, we stick with that case for this article. There are various ways to generalise to multi-player settings and we shall examine those in future articles.
[^descent]: You'll find a lot more references for gradient *descent*. That's just the same method but for minimising a function and hence with the sign flipped.
