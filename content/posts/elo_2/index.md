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

So, let's break off and finally calculate some Elo ratings. For this, [snooker.org](https://www.snooker.org/index.asp) kindly provided data of TODO matches from TODO events contested by TODO players, ranging from 1975 till last Wednesday, via their [API](https://api.snooker.org/). I've included as many matches as I could find, regardless of tour, ranking status or eligible player group, as long as they weren't team matches nor had any kind of inconsistency. For Elo calculations, it's important to sequence matches correctly, and some matches in the database weren't correctly labelled, but I did my best to get as clear data as possible. TODO: mention snooker is always win/loss; ignore frame count – since dead frames aren't played, those differences aren't meaningful.

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
