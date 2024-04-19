---
title: "Collaborative filtering: How does it work?"
subtitle: "A gentle introduction to the most popular recommendation algorithm"
slug: collaborative-filtering
author: Markus Shepherd
type: post
date: 2024-04-19T13:00:00+03:00
tags:
  - Collaborative filtering
---

Collaborative filtering is the workhorse powering the recommendations by Recommend.Games. Over the year, I've been asked every now and then how it works. So, I thought it's high time I wrote outlining the basic ideas behind our recommendation engine.

## Outline

- CF as linear regression "in two directions"
- CF as matrix factorization (filling in the blanks)
- CF as embeddings
- CF as a neural network
