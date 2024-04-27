---
title: "Collaborative filtering: How does it work?"
subtitle: "A gentle introduction to the most popular recommendation algorithm"
slug: collaborative-filtering
author: Markus Shepherd
type: post
date: 2024-04-27T20:00:00+03:00
tags:
  - Collaborative filtering
  - Recommendations
  - BoardGameGeek
---

Collaborative filtering is the workhorse powering the recommendations by Recommend.Games. Over the years, I've been asked every now and then how it works. So, I thought it's high time I outlined the basic ideas behind our recommendation engine.

Let's first take a step back and talk about recommendations in general. What is it we're trying to achieve? The answer to this question is far from trivial, and it gets harder when you want to formalise its goals. Maybe a somewhat naïve approach would be to say that we want to recommend items that the user will like. But recommendations are as much about predicting what the user wants as what they didn't even know they wanted. Sometimes the most correct answer is also the least useful: maybe our #1 recommendation is {{% game 266192 %}}Wingspan{{% /game %}} and the user indeed would love to play it - but if they already knew about it, why recommend it in the first place?

To be honest, the solution that powers Recommend.Games pretty much ignores all those questions and asks a much simpler question: given the games a user has rated, can we predict how they would rate all the other games? We can then take the highest predicted ratings and use those to recommend games to the user.

Let's make this a little more concrete and assume we only have six users we'll call A through F. They've left the following ratings:

| Game                                                 |  A | B | C |  D | E | F |
|------------------------------------------------------|:--:|:-:|:-:|:--:|:-:|:-:|
| **{{% game 266192 %}}Wingspan{{% /game %}}**         | 10 | ? | 3 |  7 | ? | ? |
| **{{% game 13 %}}CATAN{{% /game %}}**                |  ? | 8 | 6 |  ? | 5 | 2 |
| **{{% game 174430 %}}Gloomhaven{{% /game %}}**       |  9 | ? | ? | 10 | ? | 8 |
| **{{% game 12333 %}}Twilight Struggle{{% /game %}}** |  ? | 7 | 5 |  ? | 6 | ? |

Our task is to find a model to fill in the blanks. How would we go about this? The basic idea behind collaborative filtering is to find users with similar tastes and use their ratings to predict the missing ones. Let's take a closer look at users C and E. They both seem to agree fairly well on their ratings for {{% game 13 %}}CATAN{{% /game %}} and {{% game 12333 %}}Twilight Struggle{{% /game %}}, so it's a fair guess that user E would rate {{% game 266192 %}}Wingspan{{% /game %}} similar to user C. But we can also make this argument "in the other direction": users seem to rate {{% game 13 %}}CATAN{{% /game %}} and {{% game 12333 %}}Twilight Struggle{{% /game %}} in general similarly, so one game's ratings should be a good predictor for the other's. So since users F seems to dislike {{% game 13 %}}CATAN{{% /game %}}, it's a fair assumption that they would also dislike {{% game 12333 %}}Twilight Struggle{{% /game %}}.


## Outline

- CF as linear regression "in two directions"
- CF as matrix factorization (filling in the blanks)
- CF as embeddings
- CF as a neural network
