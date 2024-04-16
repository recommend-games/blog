---
title: "Board games as a reinforcement learning playground"
subtitle: "Reinforcement learning part 1: Introduction"
slug: board-games-reinforcement-learning-playground
author: Markus Shepherd
type: post
date: 2024-04-15T21:00:00+03:00
tags:
  - Reinforcement Learning
  - AlphaGo
---

I've been wanting to learn about reinforcement learning (RL), the area of machine learning behind the breakthrough that was [AlphaGo](https://en.wikipedia.org/wiki/AlphaGo), for a long time. It feels closer to actual "artificial intelligence" (AI) than any of the currently overhyped technologies because it's about smart decision making. I thought documenting my progress in learning about RL on this blog would be a natural fit.

Usually, one would start any series about RL by chewing through a whole bunch of definitions: Markov decision processes, states, actions, rewards, discount factors, returns, policies, value functions – that sort of stuff. A typical course on RL wants to provide you with a wide set of tools to solve a variety of different problems that fall under the RL framework. While this makes sense for a graduate course which wants to interest you in research in the field, it can be overwhelming and frustrating for someone who's just thinking: AlphaGo was such an impressive achievement, I would really like to understand how it works.

On the other end of the spectrum there are courses that promise you to train your first RL agents in 10 minutes, only to then import a bunch of libraries and call a bunch of algorithms that you can't possibly understand. This might be quite impressive, but you won't be able to apply what you've learned to new problems.

So, instead I'd like to go through some of the major RL algorithms and apply them to the most interesting examples one could imagine: board games. There's a couple of reasons why I think board games are a great playground for RL:

- *They're fun.* This is not a trivial matter: motivation is key to learning. The prospect of learning a great strategy for your favourite game is a much better motivator than making a robotic arm pick up machine parts – at least to me.
- *They're simple.* Many board games have only a handful of actions available at any given time, all of which have important ramifications. In RL parlace, they have a pretty small action space.
- *They're still challenging.* Even simple games can have a large number of possible board positions; for a game like Go that number exceeds \\(10^{170}\\). Those board positions are what we call the state space in RL.
- *They're finite.* Even a game like Monopoly, which can feel like it goes on forever, will eventually end. This means we're dealing with we call finite episodes, so we don't have to worry about infinite horizons.
- *They have a simple built-in reward: win or lose.* One of the strength of RL is that it can learn optimal long term behaviour from short term rewards. In order to formalise this, you usually need to sum up rewards from individual actions over time and discount them by an appropriate, which then leads to returns. In board games, there's really only one reward at the very end: win or lose. So that's your return for this episode (i.e., game): 1 if you win, 0 if you lose.
- *They're easy to simulate.* We can have our agent play as many imaginary games as we want, with little costs beyond computation time. (Training AlphaGo still cost millions of dollar, so don't underestimate that either.) Some RL problems need to learn from real world experience, e.g., robotics, which can be expensive and dangerous to collect, so there's a whole field of research on how to learn from simulated experience. We don't need to concern ourselves with that, so can pretty much skip all of what's called model based RL.
- *Their solutions are easy to interpret.* Much of RL is about learning value functions, which tell you the expected return from a given state. As mentioned, the return of a board game is simply 1 if you win, 0 if you lose. So the value function of a board game is simply the probability of winning from a given state. This is a very intuitive and easy to interpret quantity.
- Also: *they really are great fun!*

If you've never heard of those fundamental RL concepts I mentioned above, don't worry. You'll get used to them in due time, even if we don't formally define them all.

My hope is that by single-mindedly focusing on board games, we can get a good understanding of the major RL algorithms and how they work, without getting lost in dozens of different variations, all of which are important and have their relevance, but only for a certainly class of problems. By restricting that class to board games, we can cut a big chunk out of a typical RL course and still learn a lot of the basic principles.

Let's keep this reference at hand which explains some of the fundamental terms in the context of board games:

|Concept|Symbol|Explanation|
|---|---|---|
|State|\\(s\\)|The full description of the current state of the game. This could be the positions of the stones in Go, or the way the cards are distributed amongst the players in Poker, including the order of the cards in the draw pile.|
|Observation|\\(o\\)|The information the player has about the current state of the game. In a game of perfect information like Go, there really is no difference between state and observation, but in games with hidden information, like Poker, the observation is only a partial description of the state.|
|Action|\\(a\\)|The possible moves a player can make in the current state, e.g., the free (and legal) board positions in Go or *bet*, *call*, *fold* etc in Poker.|
|Reward|\\(r\\)|The reward the player receives for the move they made. In board games, we generally only care about winning or losing a game, so all rewards will be 0 except for the very last action of the game. In some games, there might be more direct rewards, e.g., victory points, from individual actions, but even in those cases, learning a strategy that maximises the probability of winning the game might still be stronger.|
|Return|\\(G\\)|The sum of rewards from the current state onwards. In board games, this is usually 1 if the player wins the game, 0 if they lose.|
|Episode||A single complete game. Note that I mentioned before board game episodes are always finite, but this might not actually be the case if players take random actions that do not advance the game, so some extra care might need to be taken for episodes to not grow indefinitely.|
|Agent||The player whose behaviour (determined by the policy \\(\pi\\)) we want to optimise.|
|Policy|\\(\pi(s)\\) or \\(\pi(a\|s)\\)|The strategy the agent uses to choose actions. This can be a deterministic policy, i.e., a function that maps every state to the action to be taken, or a stochastic policy, i.e., a probability distribution over actions for every state.|
|State value function|\\(V(s)\\)|The expected return from a given state. In board games, this is the probability of winning from a given state.|
|State-action value function|\\(Q(s, a)\\)|The expected return from taking action \\(a\\) in state \\(s\\) and then following the policy \\(\pi\\). In board games, this is the probability of winning from a given state and taking a given action.|
|Markov decision process (MDP)||A game is a series of interesting decisions, so a decision process is really just a game. The Markov property states that the future is independent of the past given the present. In board games, this is often violated in two ways: First, it's usually only true for *states*, not for *observations*, and many games have hidden information. Second, humans. While theory might tell that optimal play does not depend on how we arrived at the current state, humans do tend to hold grudges and might very much care about past behaviour.|
|Environment||In the classical RL framework, it's the environment that presents the agent with the current state and possible actions, as well as the reward for that action and the next state. So in our context, this is the game – and the other players, since their decisions will influence the state of the game until it's our turn again. RL that tries to learn the dynamics of the environment is called model based, and I've mentioned before that we generally don't have to worry about that, though one can try to model the opponent behaviour, but this often relies on assumptions about the opponent and hence might not generalise well.|

We'll start with the simplest possible game: Tic Tac Toe.


## TODO

Define some of the fundamental terms in board game context:

- State
- Action
- Reward / return
- Episode
- Agent
- Policy
- Value function
- Markov decision process (Markov property)

Mention Sutton & Barto as the standard textbook for RL.
