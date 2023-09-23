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

Click on the link and follow the instructions. This will submit a request to add collection items for one or more users to the database. Once this is approved, your collection will be added to the database the next time it is updated (this might take up to a week or more), so please be a little patient. After that, you can enjoy the full Recommend.Games experience! 🤩

*Why do you ask for money?* Recommend.Games is 100% open source and developed, improved and maintained by volunteers as a hobby project. It's not meant to make money, but it does *cost* money to run, mostly from hosting. That's why we kindly ask those users who find value in what we do and who can afford it to contribute about 1€ per month towards those costs. If you'd rather put your money to make the world a better place, please consider donating to a charity of your choice, as long as it promotes a more inclusive, sustainable and loving world. And finally, if your financial situation doesn't allow for a donation, don't worry, you can still submit your request without a bad conscience – Recommend.Games is open for anyone. 🤗

We're excited to be back and hope to introduce more cool features in the future. The internet is a very lonely place and sometimes releasing anything into the void can be a draining experience since it tends to be a one way conversation. We don't track our users in any way, so can't even watch the numbers go up, which is usually the only source of endorphin on the internet. Even more so we really appreciate every single donation, every single request, every single share on social media, every single kind word. 🥰
