---
title: The recommendation engine has a new heart
subtitle: "Turi Create is out, PyTorch is in – and the site should feel a lot steadier"
slug: pytorch-recommendation-engine
author: Markus Shepherd
type: post
date: 2026-09-21T20:00:00+03:00
tags:
  - Announcement
  - Recommend.Games
  - Internal
  - PyTorch
  - Machine learning
---

As of today, the recommendations at [Recommend.Games](https://recommend.games/#/) come out of an entirely new piece of machinery. [Turi Create](https://github.com/apple/turicreate), the toolkit that trained our model for years, is gone. The model is now trained with PyTorch, in code we wrote ourselves, in version 4 of our open source [board-game-recommender](https://gitlab.com/recommend.games/board-game-recommender).

If you read nothing else: this was a transplant, not a redesign. Same maths, new engine, much steadier site.

The [last]({{<ref "posts/new_domain/index.md">}}) [few]({{<ref "posts/hiatus_2/index.md">}}) times I wrote a post like this the news was rather more dramatic, so let me answer the obvious questions before anyone starts worrying.

*Will my recommendations change?* **Somewhat, yes.** Any retrain reshuffles things a little, and this is a retrain on a brand new trainer. Games will move around in your list, a few of them noticeably. Nothing has been deleted and no feature has gone away – the numbers underneath were simply computed afresh.

*Did the recommendations get better?* That honestly wasn't the goal, and I'd rather not claim it. The goal was to rebuild the same method on a trainer with a future.

*Then why bother at all?* Because the old toolkit had stopped moving, and it was holding everything else hostage. More on that below.

## What did not change

Everything I described in [part one of *Recommend.Games explained*]({{<ref "posts/rg_collaborative_filtering/index.md">}}) back in 2024 is still exactly how the engine works. Same collaborative filtering, same 32 latent factors, same objective it optimises, same arithmetic turning your ratings into predictions for games you haven't played. If you want to know how your recommendations are made, that article is still the answer.

What changed is who does the arithmetic, not what the arithmetic is.

## The site should feel steadier

This is the part you'll actually notice, and it has nothing to do with the model's taste in board games.

Recommend.Games runs on a small server, and for a long time the model simply didn't fit in it. If a page has ever hung on you, or died halfway through loading your recommendations, that was usually why. The new model is a much lighter houseguest.

Here's the moment it went out, just before 6 PM:

{{< img src="heroku_memory" alt="Heroku memory usage through the afternoon, running above the quota line all day and dropping below it right after the redeploy" >}}

That dashed red line is the limit we're meant to stay under. As of this evening, we finally are.

## What else went out with it

Turi Create was the reason the server sat on Python 3.8 for five years – nothing else could move while it was in the building. With it gone, the server has jumped to Python 3.14 and Django 6, shedding Spark, pipenv, pynt, black and pylint on the way out. None of that is visible from the outside, but it's the difference between a project that can be maintained and one that can only be nursed.

## Thank you

Since 18 September the new model has been in the hands of a handful of people from the [5G4D](https://5g4d.com/) Discord, who beta tested it before it went anywhere near the live site. Thank you.

## More to come

There is a lot more to say about how you re-implement a model from scratch and then prove it agrees with the thing it replaced: how the old artefacts were converted, how the training loop was rebuilt, how the memory diet was done and how we decided it was ready. Those are their own posts, and they'll land here over the coming weeks.

For now: the engine has a new heart, and it beats the same way. 🫀
