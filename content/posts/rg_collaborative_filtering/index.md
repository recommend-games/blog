---
title: A brief introduction to Collaborative Filtering
subtitle: "Recommend.Games explained, part 1: how we recommend games to you"
slug: collaborative-filtering
author: Markus Shepherd
type: post
date: 2024-05-09T21:47:57+03:00
tags:
  - Recommend.Games explained
  - Collaborative filtering
  - Recommendations
  - Recommendation engine
  - Machine learning
  - Matrix factorisation
  - Embeddings
  - Latent factors
  - Cosine similarity
  - Alternating least squares
  - Linear regression
  - BoardGameGeek
---

## What is a good recommendation?

Collaborative filtering is the workhorse powering the recommendations by Recommend.Games. Over the years, I've been asked every now and then how it works. So, I thought it's high time I outlined the basic ideas behind our recommendation engine.

Let's first take a step back and talk about recommendations in general. What is it we're trying to achieve? The answer to this question is far from trivial, and it gets harder when you want to formalise its goals. Maybe a somewhat naïve approach would be to say that we want to recommend items that the user will like. But recommendations are as much about predicting what the user wants as what they didn't even know they wanted. Sometimes the most "correct" answer is also the least useful: maybe our #1 recommendation is {{% game 266192 %}}Wingspan{{% /game %}} and the user indeed would love to play it - but if they already knew about it, why recommend it in the first place?

To be honest, the solution that powers Recommend.Games pretty much ignores all those questions and asks a much simpler question: given the games a user has rated, can we predict how they would rate all the other games? We can then take the highest predicted ratings and use those to recommend games to the user.


## The intuition behind collaborative filtering

Let's make this a little more concrete and assume we only have six users we'll call A through F. They've left the following ratings:

| Game                                                 |    A   |   B   |   C   |    D   |   E   |   F   |
|------------------------------------------------------|:------:|:-----:|:-----:|:------:|:-----:|:-----:|
| **{{% game 266192 %}}Wingspan{{% /game %}}**         | **10** |   *?* | **3** |  **7** |   *?* |   *?* |
| **{{% game 13 %}}CATAN{{% /game %}}**                |    *?* | **8** | **6** |    *?* | **5** | **2** |
| **{{% game 174430 %}}Gloomhaven{{% /game %}}**       |  **9** |   *?* |   *?* | **10** |   *?* | **8** |
| **{{% game 12333 %}}Twilight Struggle{{% /game %}}** |    *?* | **7** | **5** |    *?* | **6** |   *?* |

Our task is to find a model to fill in the blanks. How would we go about this? The basic idea behind collaborative filtering is to find users with similar tastes and use their ratings to predict the missing ones. Let's take a closer look at users **C** and **E**. They both seem to agree fairly well on their ratings for {{% game 13 %}}CATAN{{% /game %}} and {{% game 12333 %}}Twilight Struggle{{% /game %}}, so it's a fair guess that user **E** would rate {{% game 266192 %}}Wingspan{{% /game %}} similar to user **C**. But we can also make this argument "in the other direction": users seem to rate {{% game 13 %}}CATAN{{% /game %}} and {{% game 12333 %}}Twilight Struggle{{% /game %}} in general similarly, so one game's ratings should be a good predictor for the other's. So since users **F** seems to dislike {{% game 13 %}}CATAN{{% /game %}}, it's a fair assumption that they would also dislike {{% game 12333 %}}Twilight Struggle{{% /game %}}.


## Matrix factorisation via alternating least squares

That's the high level idea behind collaborative filtering – but how do we actually implement it? If you know your Machine Learning 101, you might be familiar with linear regression, which tries to find a "line of best fit" for a set of given data points. We can think of collaborative filtering as linear regression in two directions: if we fix the games and try to predict the users' ratings, we're doing linear regression in the user space. If we fix the users and try to predict the games' ratings, we're doing linear regression in the game space. Collaborative filtering tries to do both at the same time – by alternating between the two, which is why this method is known as *alternating least squares* (ALS, "least squares" referring to minimising the squared error).

After running the algorithm, we end up with one vector for each user and one for each game. Taking the inner product (sometimes referred to as dot product) of those vectors yields a single number, the predicted rating. If we stack all the vectors for the users into a matrix \\(U\\) and the vectors for the games into a matrix \\(G\\), we can multiply those two matrices to get a matrix \\(R\\) of predicted ratings:

\\[
    R = U^\top \cdot G.
\\]

In other words: we've taken the matrix of ratings from the table above and factored it into two matrices. So another way of thinking about collaborative filtering is as a matrix factorisation problem: we're trying to find two matrices that, when multiplied together, approximate the original matrix as closely as possible.


## Latent factors and embeddings

Those user and game vectors are also known as *latent factors*. That's because they take the high-dimensional space of users and games and project it into a lower-dimensional space. While those latent dimensions don't carry any particular human interpretable meaning, they capture the essence of what makes a user like a game. For example, one latent factor might capture how much a user likes games with a lot of player interaction, while another might capture how much they like games with a lot of strategic depth. Note that we can freely choose the number of latent factors, which is an important hyperparameter of the model. The more latent factors we use, the more expressive the model can be – but it also becomes more prone to overfitting. Recommend.Games uses 32 latent dimensions, which is a decent default choice for many recommendation problems.[^size]

The latent factors also have some interesting properties. For example, there's a meaningful distance between them: if two users are close together in the latent space, they have similar tastes. The distance in question is the cosine similarity, which measures the angle between two vectors. Think of it this way: if the vectors for two users point in the same direction (cosine similarity close to 1), they have similar tastes. If they point in opposite directions (cosine similarity close to -1), they have opposite tastes. If they're orthogonal (cosine similarity close to 0), they have no correlation.

The same goes for the game vectors: we can calculate the cosine similarity between two games to see if they appeal to the same users. Every game page on Recommend.Games has a "You might also like" section at the bottom. Those are the games with the highest cosine similarity to the game in question.

Vector representations with some measure of distance are called *embeddings*. So this is yet another way of thinking about collaborative filtering: we're embedding users and games into a latent space where we can measure their similarity.

So, this was a pretty lengthy and technical article, but I hope it provides some intuition of how the recommendation engine behind Recommend.Games works. Obviously, there are a lot more details to it, but those are the most important ideas. One of the reasons why I wanted to talk about this topic is that we can have more fun with those latent factors, so stay tuned for more articles on this topic!

[^size]: The number of latent dimensions also affects the size of the model. As mentioned, we have one latent vector for every user and every game, each with 32 entries. Currently, we have over 500 thousand users and over 90 thousand games, so the matrix \\(U\\) has over \\(500\\,000 \cdot 32 = 16\\,000\\,000\\) entries and the matrix \\(G\\) has over \\(90\\,000 \cdot 32 = 2\\,880\\,000\\) entries. Each entry is a 64-bit (8 bytes) floating point number, so the total size of the model is around \\((16\\,000\\,000 + 2\\,880\\,000) \cdot 8\\,\text{B} \approx 150\\,\text{MB}\\). It's not a negligible size to load into the memory of a cheap server (which is what we're using), but in the modern age of deep neural networks with gazillions of parameters, it feels almost tiny.
