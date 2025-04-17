---
title: "Cue the maths: predicting snooker’s next champion with Elo"
subtitle: "Elo, part 2: How maths, models and millions of simulations might tell us who lifts the trophy"
slug: next-world-snooker-champion
author: Markus Shepherd
type: post
date: 2025-04-19T12:00:00+03:00
tags:
  - Elo rating
  - Snooker
---

# Outline

- Intro to snooker
  - Opening of the world championship
- Explain Elo ratings with examples
  - E.g., take a recent match and explain how points were exchanged
- Maybe some statistics, such as #1 rated player over time?
- Tournament simulation
  - Win probabilities
- Comparison to betting odds


# Welcome to the Crucible

- World Snooker Championship!
  - Few words about snooker in general
- Application of Elo
  - Concrete examples
  - Predict winner
  - Maybe make some money


# Building the model: Elo meets the baize

## Decades of data

So, let's break off and finally calculate some Elo ratings. For this, [snooker.org](https://www.snooker.org/index.asp) kindly provided data of 68,260 matches from 2,163 events contested by 4,212 players, ranging from 1975 till last Wednesday, via their [API](https://api.snooker.org/). I've included as many matches as I could find, regardless of tour, ranking status or eligible player group, as long as they weren't team matches nor had any kind of inconsistency. For Elo calculations, it's important to sequence matches correctly, and some matches in the database weren't correctly labelled, but I did my best to get as clear data as possible. Note that I did not take frame score into account, but only cared about win/loss: since the match is stopped after a player reached the winning score and dead frames aren't played out, that difference has very little relevance to the predictions.


## How Elo predicts the winners

To recap the actual calculations: all players start at an Elo rating of 0. (As mentioned before, it really could be any value, but we'll stick with the simplest one.) Using the ratings \\(r_A\\) and \\(r_b\\) before the match, we can predict *A*'s win probability \\(p_A\\) like this:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

As usual, we can calculate *B*'s chances via \\(p_B=1-p_A\\), so we won't need to worry much about that. Once the match is done, we can compare that prediction with the actual outcome \\(s_A\\), where we score a win as 1 and a loss as 0. We then update *A*'s rating:

\\[ r_A \leftarrow r_A + K (s_A - p_A), \\]

where \\(K\\) is the update factor I've set to 42 for the purpose of this exercise since it's the value that yields the most accurate predictions.[^42] (*Much* more on this in the next article.)


## Match by match: how ratings shift

Let's look at some examples. Before the very first match in the database, Ray Reardon vs John Spencer on 1975-01-17, we didn't know anything about any player, so they all had the initial rating of 0 and, if you plug a rating difference of 0 into the formula, you'll see that we predict even chances of winning for both players (which makes perfect sense). John Spencer won that match, so we updated

\\[ r_{\text{JS}} \leftarrow 0 + 42 \cdot (1 - 0.5) = 21. \\]

His opponent got his rating reduced by the same amount[^zero-sum]: \\(r_{\text{RR}}\leftarrow-21\\). I wrote a simple [Python script](https://gitlab.com/recommend.games/blog/-/blob/master/experiments/elo/Snooker%20data.py) to carry out these calculations for all 68,259 matches that followed. Let's take a look at one more match: the final of the most recent tournament, the 2025 Tour Championship, played between snooker legends John Higgins and Mark Selby, both with four world titles to their name. They went into the match with Elo ratings of 718.3 and 714.5, respectively. This means we would've predicted Higgins' win probability to be 50.5%. The match was indeed won by John Higgins, who gained \\(42\cdot(1-0.505)=20.8\\) points, whilst Mark Selby lost the same amount, for a new (and current) rating of 739.1 and 693.7, respectively.


## Who's on top? Elo's current kings

As mentioned, my code diligently carried out the Elo predictions and updates for every single match from 1975 till the 2025 World Championship Qualifiers, which ended on Wednesday. These are the ten currently highest rated player:

TODO: Table

TODO: notes on present and absent players. Maybe some sample probabilities about chosen pairings? Link to download full results.


## Rising stars and fading legends

It's fun to look back in time and check how players' ratings evolved over time: Who was the highest rated player of his time? When did his ratings rise and fall? Let's take a look across the decades:

TODO: Plot 70's

TODO: comment

TODO: Plot 80's

TODO: comment

TODO: Plot 90's

TODO: comment

TODO: Plot 00's

TODO: comment

TODO: Plot 10's

TODO: comment

TODO: Plot 20's

TODO: comment; link to full results; discuss why it's hard to choose constant K: the current value was picked mostly to work well with the current calendar, but back then very few tournaments were played. Reminder: Elo is strongest amongst an active community, but not directly comparable across time, games, and different implementations. Compare to snooker-predictions.org?

An interesting measure of dominance is the question of what player has spent the most time as highest rated. Here's the top 10:

TODO: table (include first and last as columns)

TODO: Link to full results. Finally, who had the highest rating ever? TODO. Maybe: what was the highest rated match? Biggest upset?


- Mention data source (https://api.snooker.org/, make sure to get attribution right)
  - Problems with availability, dates, all matches treated equal
- Mention choice of K (tease details for next article)
- Current top 10
  - Example of point exchange, e.g., during last final
  - Compare to https://snooker-predictions.com/rankings.html
  - Mention retired players
- Plot point evolution over time of Class of '92
  - Mention problem with rating Ronnie O'Sullivan right
- Alternative: Plot top three players (by max score) for each decade?
- Highest rated player over time
  - Maybe early year and recent changes in leaders
  - Mention how K (there it is again!) is geared towards modern event calender
- Who has spent most time as highest rated player?
- Highest ever rating


# 10 Million Tournaments Later…

I thought it would be a fun application to use those Elo ratings we calculated to predict who will win the current World Championship. For this, I've run a bunch of simulated tournaments. The idea is quite simple: for each of the first round pairings in the draw, I compare the current Elo ratings of those two players, convert them into a win probability as described above, and toss a virtual coin in order to determine who proceeds to the second round. We apply the same principal to that and all the following rounds, until the final coin for the final is tossed and the winner of that simulation run is determined. I've run a total of 10 million simulated tournaments and counted how often each player won a simulation. Here are the results:

TODO: table of WC predictions. Add Elo and/or world ranking? Mention Ronnie here or above?

Unsurprisingly, the order strongly correlated with the Elo ranking we've seen above, but it's not quite the same. E.g., TODO: example of players higher or lower ranked. Explain with harder and easier paths to the final. Should we include the pairings here?

- Explain simulation
- Result table
- How does this compare to Elo ranking – why are players in different order?


## How does the market compare? Bookies vs model

> Disclaimer: gambling is bad. TODO

I'm personally not the gambling kind and wouldn't advice you to pick up that addictive habit either. But sport bets are an undeniably interesting data source for predictions, as you really need to put your money where your mouth is. That's why you often see betting odds discussed ahead of big sporting events: there's few models with comparable predictive accuracy. So I thought it's an interesting reality check for those simulations to compare those results to what gamblers are willing to bet on the snooker stars.

First, we need briefly discuss how to convert those probabilities to odds. Let's say I offer you the following gamble: you pay me €1, then I toss a (fair) coin. Heads: I pay you back €2; tails: I keep your money. You probably intuitively know that the expected payout is €1, so you can take or leave the bet and wouldn't be better or worse off for it. Had I offered you a potential win of €2.10, you actually should take the bet; for a €1.90 stake you should definitely pass.

The same basic idea applies to the odds quoted[^odds-quotes] in sport betting: The broker will quote odds like 5, meaning I could win €5 if I bet €1 (for a potential gain of €4). If I believe the event will occur with a 20% probability, my expected payout is exactly 1 – I should only take the bet if my believe in that event is higher (if you must take the bet at all). In other words: in order to convert between probabilities and odds, you just take the reciprocal. E.g., the win probability of TODO for TODO corresponds to odds of TODO, i.e., I'd expect to make money if someone offered longer odds and might be inclined to take the bet.

So, I've taken a look at [oddschecker.com](https://www.oddschecker.com/snooker/world-championship/winner) to see what odds different brokers offer for different players to win the World Championship. These are the odds[^max-and-vig] as offered and how they compare to the odds implied by our simulations:

TODO: Table. Include comparision. Discuss Ronnie again?

I'd say, by and large those match quite well. Clearly, "the market" believes more in some players than our model, but the ballpark is right – with the exception of Ronnie O'Sullivan. He truely is a wildcard this year. TODO: is he playing?

- Disclaimer
- Present some odds from https://www.oddschecker.com/snooker/world-championship/winner
  - Explain how to read / convert odds
- Convert our winning probabilities to odds
  - Where could you make money?
  - Disclaimer!
  - Mention Ronnie again


# Final frame 🎱

- Summary
- Outlook


[^42]: Seriously, it's not a Douglas Adams reference. The maths just worked out that way.
[^zero-sum]: Because we applied Elo's formula in its simplest form, all updates will be zero-sum, and the overall average Elo rating will stay fixed at 0.
[^odds-quotes]: TODO: British and other styles.
[^max-and-vig]: Note that I've only used the highest odds offered by any broker. If you were to place a bet, you'd always want to go with the provider who offers you the highest payout, so that number is the most relevant. It's also worth pointing out that when you sum up the probabilities implied by the odds, they will usually exceed 100%. That's because the odds are slightly shorter than they should be because the brooker wants their cut (also know as vigorish) too. Remember: the house always wins.
