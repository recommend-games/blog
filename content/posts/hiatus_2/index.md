---
title: Recommend.Games is back!
subtitle: Request to have your collection added to the database now
slug: recommend-games-is-back
author: Markus Shepherd
type: post
date: 2023-09-18T21:00:00+03:00
tags:
  - Announcement
  - Hiatus
  - Recommend.Games
  - Internal
  - Collection
---

The [hiatus]({{<ref "posts/hiatus/index.md">}}) is over! Already since April 2023 the recommendation engine at Recommend.Games has been back online, albeit with reduced functionality. In order to cut down serving costs, I made the recommendation model much more lightweight (this deserves its own article) and removed rarely used features as well as a bunch of bloat from the database.

Most of the database was filled with users' collection items, i.e., games they rated, owned, have played etc. So all this information had to go. As a consequence, the recommendations would be cluttered with all those games the user is already familiar with, making them much less useful. That's the reason we didn't make a big announcement when we came back online in April.

But fear not! We've brought back collection items for users who really want to use Recommend.Games, thus providing a way to continue to serve the best recommendation experience possible, whilst still keeping hosting lean.

*How does it work?* When you request your recommendations from Recommend.Games as usual by typing your BoardGameGeek user name into the engine, but we don't find your collection in the database, you'll see a prompt that allows you to submit a request to have your collection added:

{{< img src="collection_request" alt="Prompt to submit a collection request" >}}
