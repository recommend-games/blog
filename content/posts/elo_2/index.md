---
title: Who will be the next World Snooker Champion?
subtitle: "Elo, part 2: TODO"
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


# Intro

- World Snooker Championship!
  - Few words about snooker in general
- Application of Elo
  - Concrete examples
  - Predict winner
  - Maybe make some money


# Snooker Elo ratings

## The data

So, let's break off and finally calculate some Elo ratings. For this, [snooker.org](https://www.snooker.org/index.asp) kindly provided data of TODO matches from TODO events contested by TODO players, ranging from 1975 till last Wednesday, via their [API](https://api.snooker.org/). I've included as many matches as I could find, regardless of tour, ranking status or eligible player group, as long as they weren't team matches nor had any kind of inconsistency. For Elo calculations, it's important to sequence matches correctly, and some matches in the database weren't correctly labelled, but I did my best to get as clear data as possible. Note that I did not take frame score into account, but only cared about win/loss: since the match is stopped after a player reached the winning score and dead frames aren't played out, that difference has very little relevance to the predictions.


## Elo's formula

To recap the actual calculations: all players start at an Elo rating of 0. (As mentioned before, it really could be any value, but we'll stick with the simplest one.) Using the ratings \\(r_A\\) and \\(r_b\\) before the match, we can predict *A*'s win probability \\(p_A\\) like this:

\\[ p_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

As usual, we can calculate *B*'s chances via \\(p_B=1-p_A\\), so we won't need to worry much about that. Once the match is done, we can compare that prediction with the actual outcome \\(s_A\\), where we score a win as 1 and a loss as 0. We then update *A*'s rating:

\\[ r_A \leftarrow r_A + K (s_A - p_A), \\]

where \\(K\\) is the update factor I've set to TODO for the purpose of this exercise since it's the value that yields the most accurate predictions. (*Much* more on this in the next article.)


## Examples

Let's look at some examples. Before the very first match in the database, TODO vs TODO on TODO, we didn't know anything about any player, so they all had the initial rating of 0 and, if you plug a rating difference of 0 into the formula, you'll see that we predict even chances of winning for both players (which makes perfect sense). TODO won that match, so we updated

\\[ r_{TODO} \leftarrow 0 + K_{TODO} (1 - 0.5) = TODO. \\]

His opponent got his rating reduced by the same amount[^zero-sum]: \\(r_{TODO}\leftarrow TODO\\). I wrote a simple [Python script](TODO) to carry out these calculations for all TODO matches that followed. Let's take a look at one more match: the final of the most recent tournament, the 2025 Tour Championship, played between snooker legends John Higgins and Mark Selby, both with four world titles to their name. They went into the match with Elo ratings of TODO and TODO, respectively. This means we would've predicted TODO's win probability to be TODO. The match was eventually won by John Higgins, who gained \\( K_{TODO} \cdot (1 - TODO)\\) points, whilst Mark Selby lost the same amount, for a new (and current [TODO: verify]) rating of TODO and TODO, respectively.


## The ranking

As mentioned, my code diligently carried out the Elo predictions and updates for every single match from 1975 till the 2025 World Championship Qualifiers, which ended on Wednesday. These are the ten currently highest rated player:

TODO: Table

TODO: notes on present and absent players. Maybe some sample probabilities about chosen pairings?


## Elo ratings over time

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

TODO: comment

An interesting measure of dominance is the question of what player has spent the most time as highest rated. Here's the top 10:

TODO: table (include first and last as columns)

Finally, who had the highest rating ever? TODO. Maybe: what was the highest rated match?

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


# Predict outcome of 2025 World Championship

- Explain simulation
- Result table
- How does this compare to Elo ranking – why are players in different order?


## Compare to betting odds

- Disclaimer
- Present some odds from https://www.oddschecker.com/snooker/world-championship/winner
  - Explain how to read / convert odds
- Convert our winning probabilities to odds
  - Where could you make money?
  - Disclaimer!
  - Mention Ronnie again


# Conclusion

- Summary
- Outlook


[^zero-sum]: Because we applied Elo's formula in its simplest form, all updates will be zero-sum, and the overall average Elo rating will stay fixed at 0.
