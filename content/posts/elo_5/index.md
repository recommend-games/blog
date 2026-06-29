---
title: TODO
subtitle: "Elo, part 5: TODO"
slug: elo-part-5-todo
share_img: /posts/elo-part-5-todo/skill_vs_complexity.png
author: Markus Shepherd
type: post
date: 2026-03-31T12:00:00+03:00
draft: true
tags:
  - Elo rating
  - board games
  - luck vs skill
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.8.1.min.js" ></script>

TODO: Intro + Hook


## Method: what we're trying to measure (and what not)

First, we need to take a closer look into what exactly we're trying measure and how. I'll try to keep it fairly high level here, but if even a hint of theory is too much for you, feel free to skip straight to the results.


### The story so far

This is part 5 of our series on Elo and measuring "skills" in games, so I'll lay out the overall methodology here in the form of a brief recap.

The data basis are matches from Board Game Arena, or more precisely: the outcomes (final rankings) of matches. We use the Elo system to turn those match results into ratings. Elo gives every player a *relative* rating: a number that moves up when they beat expectations and down when they don’t. (If you want the full “how does Elo do that?” story, that’s [part 1]({{<ref "posts/elo_1/index.md">}}). If you want to see Elo on real data before we touch board games, that’s [part 2]({{<ref "posts/elo_2/index.md">}}).) Important caveat: Classic Elo only handles two-player games. But board games aren’t all chess, and most matches aren’t 1‑vs‑1. So I use the multiplayer Elo generalisation from [part 4]({{<ref "posts/elo_4/index.md">}}), which models the whole finishing order.

Either way, Elo uses one important dial: the update factor \\(K\\) which controls how much ratings move after each match. Following Dürsch/Lambrecht/Oechssler (DLO), I calibrate \\(K*\\) per game by minimising prediction error on that game’s match log (Brier loss). That’s the core trick we borrowed in [part 3]({{<ref "posts/elo_3/index.md">}}). Using this calibrated updated factor, we can calculate the Elo ratings of all players per game.

The basic idea of "measuring skill" is that games which allow some form of "mastery" (like chess) should have a strong separation between players and hence a wide spread of players' Elo ratings. On the other hand, predominantly luck based games (like TODO) won't have much of a difference in players' skills and hence a very narrow spread. The mathematical measure of this spread, the standard deviation \\(\sigma\\) of Elo ratings, is our primary measure of "skill", our "skill‑o‑meter" from [part 3]({{<ref "posts/elo_3/index.md">}}).

We then take one extra step: The raw \\(\sigma\\) is hard to interpret. This is why I map it onto the benchmark “toy universes” from [part 3]({{<ref "posts/elo_3/index.md">}}) and [part 4]({{<ref "posts/elo_4/index.md">}}): **\\(p\\)‑deterministic games**, where outcomes behave like “the better player wins with probability \\(p\\)”.

**That gives a single headline number per game: *skill sensitivity* \\(p\\) (higher \\(p\\) ≈ results behave more like “better player wins”; lower \\(p\\) ≈ results are more swingy).**


### Some more details: assumptions, simplifications, known limitations

TODO: What is skill in a game? Fundamental assumption going into Elo. What it measures and what it doesn't.

TODO: Describe exactly what we're measuring, define skill sensitivity.

TODO: Source of data: BGA. Only consider competitive games with enough regulars etc.

TODO: We only look at outcomes, the games themselves remain blackboxes (no action spaces or decision trees etc). Do people even care to win? Magic circle, Knizia quote etc.

## Results

### Skill sensitivity vs complexity

{{% bokeh "skill_vs_complexity.json" %}}

TODO: Complexity has its own issues. Many 'geeks rate a game heavy based on its depth rather than rules overhead (cf go).

### Most skill sensitive games

TODO: Table

#### Games that punch above their weight

TODO: Most skill sensitive games within complexity band. (Quantiles?)

### Least skill sensitive games

TODO: Table

## Notes

### Criterion for games included in the analysis

- Enough regular players (100)
- Corresponding BGG entry (drop BGA games which map to the same BGG entry — mostly traditional)
- Competitive (let's remove: BGA rank locked AND coop on BGG)

### Notes on the method and the "skill sensitivity" / "p-deterministic" metric

- Take it with tons of salt
- Highly depends on player population
  - Some games might attract "try and click around" players
  - Some players might not be as competitive as on other platforms
  - Others might be so competitive that they are willing to cheat (BGA locked down chess ranking because people clearly used bots)
  - BGA has the concept of friendly / unranked match where no Elo will be updated; I used them for Elo calculations anyways
- Remember that we benchmark against p-deterministic, which isn't the same as "skill fraction" (hence "skill sensitivity" — p is a benchmark, not a literal fraction of skill)
- Also the subtlety about random generators in game (card, dice etc) vs random (unpredictable) outcome
  - Reminder: Tic Tac Toe is fully deterministic (no random elements or hidden information), but amongst an adult population will have 0 skill spread since it will always end in a draw
  - Likewise, a group of chess grandmasters just drawing all the time would look similarly noisy, even though chess is obv highly skill based
- Most importantly: luck vs skill isn't really one-dimensional, and it certainly doesn't mean "better or worse"



## Narrative notes

### The central question

Not "how much luck is in this game?" — that framing is unwinnable and invites endless objections. Instead: **"When you get better at a game, do you start winning more?"** That's what BGA match data actually answers. Empirically grounded, hard to dispute as a question, sidesteps the design-intent fight entirely. We're reporting what happens when real people play, not reverse-engineering the designer's intentions.

### The headline finding

The scatter shows a positive but weak, noisy correlation between complexity and skill sensitivity. That *is* the story: BGG complexity doesn't predict competitive differentiation well. Some rule-heavy games produce surprisingly equal outcomes; some simple games produce brutal competitive hierarchies. The gap between "what BGG weight implies" and "what BGA outcomes show" is what the article is about.

### The hook

**Spot It.** A children's card game where the better player wins as reliably as in Terraforming Mars. Lead with that specific, counterintuitive claim. It does two things: grabs attention, and immediately demonstrates that the metric measures *competitive differentiation*, not strategic depth — which inoculates against the "luck vs skill" criticism before it can land.

### Proposed structure

1. **Hook** — Spot It vs Terraforming Mars. Create the tension before explaining anything.
2. **The question** — two paragraphs reframing the measurement. Not luck vs skill (a property of the rules). Instead: does a competitive hierarchy form in practice? Front-load the key caveat *once*, with confidence: this reflects the BGA population, not abstract game truth. Then move on.
3. **Compact method recap** — four or five sentences. Elo spread, calibrated K*, p-benchmark. Link-heavy for those who want the derivations.
4. **The main plot** — skill sensitivity vs complexity. Describe the overall shape honestly: correlation exists but is loose. Three or four specific game callouts.
5. **The two outlier stories** — the section that gets shared:
   - *Simple but brutal*: Spot It, Panic Lab, Abalone — consistent winners emerge despite minimal rules overhead
   - *Complex but swingy*: Skat, Pax Pamir — games celebrated for depth where the competitive hierarchy is surprisingly flat
6. **Top/bottom tables** — compact, 5–8 games each. High reader value, low word count.
7. **Caveats woven into outro** — not a separate section, not apologetics. Population-dependent, BGA-specific, "do players even care to win?" (magic circle), Tic-tac-toe paradox. Close with what the measure *does* tell you.

### Specific narrative beats

- **CATAN at ~35%** — most argued-about data point. Generates productive debate.
- **Pax Pamir** — designer famous for systems mastery, yet swingy as hell on BGA. One of the best labels, generates discussion on its own.
- **Skat** — high complexity (~3.2), low skill (~20%). Famously technical German card game that looks nearly random on BGA. Demands an explanation.
- **Chess vs Gaia Project** — Chess sits alongside Caylus in skill sensitivity despite Gaia Project being "heavier" by BGG. Makes the BGG weight problem concrete and visual.
- **Tic-tac-toe paradox** — use proactively to define what the metric measures. Among adults it looks random even though it's deterministic. Mirror: a field of grandmasters drawing chess games would look noisy. Inoculates against the "but chess is obviously skill" objection.
- **Dot size** — mention in prose: "dot size scales with number of matches on BGA."

### Scope decisions

- **Cut**: upset rates analysis, player count curves, personal fingerprint, error bars plot — need new data or duplicate what's already there. Personal fingerprint could be a "part 5b."
- **Keep**: scatter plot, top/bottom tables, two outlier narrative sections, compact caveats in outro.
- **Target length**: roughly parts 3 and 4 (~150 lines of markdown), slightly longer as the payoff article.

### Voice

Rigorous but playful. Confident — this article has earned it after four parts of setup. Caveats as *interpretive insight*, not apologies.


## Appendix: assumptions, caveats and considerations from DLO and the methodology

### Core Elo assumptions

- **Logistic win probability.** The probability that player A beats player B is a logistic function of their rating difference. This is a parametric choice — other functional forms (Gaussian, linear) would give different results.
- **Zero-sum updates.** What one player gains, others lose exactly. Total rating mass is conserved.
- **Skill is scalar and transitive.** Each player has a single number representing their strength. If A usually beats B and B usually beats C, A usually beats C. Games where matchup-specific strategies matter (rock-paper-scissors dynamics between playstyles) violate this.
- **Skill is stationary within the rating run.** Elo doesn't structurally distinguish a player who was strong two years ago from one who is strong now. It adapts, but only through the same update mechanism.

### Multiplayer extension (DLO / Plackett-Luce)

- **The Plackett-Luce ranking model.** The probability of a full finishing order is computed as a product of softmax steps: "who wins among those remaining?" This assumes that conditioned on who finishes first, the remaining players' relative probabilities are unaffected. This is a strong independence assumption that real board games may violate (king-of-the-hill dynamics, catch-up mechanics, etc.).
- **Only ordinal outcomes matter.** A narrow first place and a runaway victory are treated identically. Margin of victory, point totals and game-specific scores are discarded.
- **Fixed linear payoff structure.** First place gets n−1, second gets n−2, ..., last gets 0. This is a specific choice; others are possible.

### K\* calibration

- **Brier loss as the optimization criterion.** K\* minimizes mean squared prediction error. Log-loss or other proper scoring rules would be defensible alternatives and might give different values.
- **One K for all players in a game.** A single update factor applies regardless of a player's experience level or how long ago they started.
- **K\* is constant across the entire match log.** As player pools grow or shift over time, the "optimal" K could drift; the model assumes it's stable.

### The p-deterministic benchmark

- **The benchmark game is a mixture of two extremes.** Real games are compared to a toy model where each match is either "pure skill" (fixed ranking decides) or "pure random" (uniform lottery). Real randomness in games — dice rolls, card draws — doesn't work like this at all.
- **"Pure skill" means a fixed underlying ranking.** Players are ranked once at the start and never change rank. In reality skill evolves, declines and has variance game-to-game.
- **p is treated as a property of the game.** But it's really a property of the game played by a specific population of players.
- **The σ→p mapping is player-count-invariant.** Verified empirically in simulation for up to 15 players, but rests on the same Plackett-Luce model assumptions used throughout.
- **This is the harder benchmark.** DLO offer two benchmarks: "50%-chess" (mixing real chess outcomes with coin flips, σ≈45) and "50%-deterministic" (the fully synthetic toy universe, σ≈123). The blog series uses p-deterministic, which is equivalent to DLO's more extreme second benchmark. A game that DLO would classify as "above 50%-chess" (skill-dominant) can still appear moderate in our framing. This choice should be stated explicitly when comparing to other work.

### Data and scope

- **BGA-only data.** The player population is self-selected: online, competitive-minded, predominantly tech-savvy, skewed toward certain regions. This population may differ substantially from the "typical" player group for a given game.
- **Friendly/unranked games are included.** BGA allows matches to be played "for fun" with no official Elo update. These are included in the analysis anyway — players in such games may not be trying to win.
- **Only outcomes are observed, not game states.** The model is a complete black box on the game. Strategies, hidden information structures, the nature of the randomness (one bad dice roll vs many) — none of this enters the calculation.
- **Competitive games only (filter).** Games are filtered to ≥100 regular players, with a BGG entry, and excluding those that are locked BGA-rank or cooperative on BGG. This filter is a deliberate choice that affects which games appear and which don't.
- **Players are assumed to be trying to win.** The entire machinery breaks down if players are learning, playing socially, or not engaged competitively. The model has no way to detect this.
- **Minimum-games cutoff.** The standard deviation of the rating distribution rises substantially as the minimum-games threshold increases, because players with few games have ratings stuck near their initial value of 0, artificially compressing the distribution. DLO use 25 games as their "regulars" threshold and show σ continues to rise up to ~100 games before stabilising. Whatever cutoff is used in the BGA analysis, it is a methodological choice with material impact on the numbers.
- **Dataset connectivity.** DLO remove "isolated players" — those not connected to the main player pool via any chain of shared opponents. Without at least occasional cross-group play, Elo's transitivity cannot propagate, and isolated clusters generate internally-consistent but mutually-incomparable ratings. If BGA's matchmaking keeps players in narrow Elo bands, this matters.
- **Stratification.** If a platform's matchmaking produces very homogeneous groups (strong players only against strong, weak only against weak), the overall rating distribution compresses even in a highly skill-based game. Conversely, if strong players systematically seek out weak opponents (as in online poker), the method detects more skill than average. BGA's matchmaking rules are therefore directly relevant to the numbers.

### Interpretation

- **Competitive differentiation ≠ "fraction of luck in the rules".** p measures whether consistent winners emerge in practice, not how much randomness the game designer put in. A population of equally-skilled players will produce p≈0 even in chess (Tic-tac-toe paradox). The metric is population-relative by construction.
- **Every game shows statistically significant skill.** DLO run a simple OLS regression (past average performance predicting current match outcome) across all games and find the coefficient is significant at p<0.001 for every game, including poker and Crazy 8s. "Predominantly chance" in their framework means the σ falls below the benchmark threshold, not that there is no skill. A game appearing in the "swingy" section still has measurable, real skill effects.
- **The "repetitions" framing.** DLO compute for each game how many matches a player who is one standard deviation better than their opponent needs in order to be reliably ahead more than half the time (at 75% confidence). For chess it is 3 games; for poker ~100; for Crazy 8s 12,637. This gives a concrete, intuitive expression of the same information as p and may be a more relatable way to communicate it to readers than an abstract percentage.

---

## Outline from Gippty

0. Title + framing

Something like:

Title: Which Board Games Are Really About Skill?
Subtitle: Elo, part 5: Putting our skill-o-meter to work on real games

Promise right up front: “We’ve built all this machinery in parts 1–4; now we’re going to use it to rank actual games, show plots, and maybe hurt some feelings.”

⸻

1. Hook & recap: “We built a skill-o-meter. Now we’re pointing it at your favourite games.”

Goal: 3–5 short paragraphs, no maths, strong narrative.
	•	Recall the two big ingredients:
	•	Elo as a skill rating (part 1 & 2).
	•	Elo spread → “skill fraction” via the toy universes (part 3).
	•	Multiplayer Elo & the evidence that σ↔p works for 3–5 players too (part 4).
	•	One teaser example: “Turns out some ‘serious’ games are almost as swingy as party games; some simple fillers are surprisingly brutal.”

No plots yet. Just lay the stakes.

⸻

2. Data & method in one page: “How we measured skill in practice”

Goal: reassure the nerds + not bore everyone else.

Very high-level:
	•	What data you used:
	•	BGA logs (which games, basic filters: minimum players, minimum matches).
	•	BGG metadata (ratings, “weight”, categories).
	•	What you computed for each game:
	•	Multiplayer Elo using the method from part 4.
	•	Optimal K^\* for predictive accuracy.
	•	Elo standard deviation σ and corresponding “skill fraction” p via the p-deterministic benchmark.

Visual:
A simple flow diagram:

BGA matches → multiplayer Elo → σ → match σ to p-curve → skill fraction
+ BGG weight / rating / categories

Just enough so readers trust that this isn’t hand-wavy.

⸻

3. Hero visual: “The skill map of BGA”

This is your main payoff plot.

Plot:
Big scatter:
	•	x-axis: estimated skill fraction p (0–1).
	•	y-axis: BGG weight (complexity).
	•	Point size: BGA popularity (number of plays or players).
	•	Colour: broad category (e.g. “abstract”, “party”, “euro”, “card game”).

Narrative:
	•	Describe the overall cloud: is it a diagonal (more complex → more skill)? Or noisy?
	•	Call out a few labelled games:
	•	One light but high-skill game (“simple rules, sharp teeth”).
	•	One heavy but low-skill game (“lots of rules, not much control”).
	•	One classic that lands exactly where people expect.

Tiny table sidebar:
	•	“Top 5 most skill-based games (by p, popular-only)”
	•	“Top 5 most luck-based games (by p, popular-only)”

This section alone already rewards the reader.

⸻

4. Expectations vs reality: “Heavy but swingy, light but ruthless”

Now you zoom in on mismatches between perception (BGG weight) and measured skill.

4.1. Heavy but swingy

Table: “Heavy rules, loose grip”

Columns:
	•	Game
	•	BGG weight
	•	Skill fraction p
	•	BGG rating

Pick ~5–7 “weight > 3.0 but low p” games.

Narrative: short riffs like:
	•	“On paper this is a deep engine-builder; in practice the stronger player gets ambushed by randomness quite often.”

4.2. Light but ruthless

Table: “Easy to learn, hard to win”

Same columns, but “weight ≤ 2, high p”.

Narrative:
	•	“Teach in five minutes, spend fifty games trying to get good at it.”

You can reuse games already mentioned in the big scatter to keep continuity.

⸻

5. Upsets & predictability: “Do stronger players actually win?”

This section is less about p and more about how it feels to play.

Metrics per game (behind the scenes):
	•	Upset rate: % of games where the lower-rated player (or team) wins.
	•	Average predicted win probability of the eventual winner (from Elo).

Visual:
Bar chart or dot plot with 10–12 games:
	•	x-axis: “upset rate” or “favourite wins %”.
	•	Games sorted from “upset city” to “grim ladder where the strong farm the weak”.

Narrative:
	•	Tie to intuition: “In game X, the better player wins ~80% of the time; in game Y, even strong players get dunked on a lot.”
	•	Point out a couple where upset rate doesn’t match players’ gut feeling.

This section grounds the abstract p-number in something people intuitively understand.

⸻

6. Player count twist (one or two flagship games)

You don’t want to drown people in multi-plot grids, but one clean example really sells the “multiplayer wasn’t just for show”.

Pick 1–2 games with multiple player counts and lots of data (e.g. CATAN, Terraforming Mars, Wingspan).

Plot:
For each chosen game:
	•	x-axis: player count (2, 3, 4…)
	•	y-axis: skill fraction p
	•	Simple line with markers.

Narrative:
	•	“At 3 players, CATAN behaves like a ~70% skill world; at 4, that drops closer to 60%.”
	•	Or the surprising version if the data says otherwise.

Clarify that the benchmark σ↔p curve is stable, but the actual game can move along that axis as the table grows.

Keep this short and visual, so it doesn’t turn into a new theory article.

⸻

7. Personal angle: “My own skill fingerprint”

This is the “fun human” bit that makes the whole series feel personal rather than abstract.

Metric:
	•	For each game you’ve played on BGA:
	•	Your Elo under your system.
	•	Population median Elo (or percentile).
	•	The game’s skill fraction p.

Plot:
Scatter:
	•	x-axis: skill fraction p.
	•	y-axis: your “performance” (e.g. your percentile rank in that game).
	•	Highlight a handful of titles:
	•	“Games I’m surprisingly good at.”
	•	“Games that consistently expose me.”

Narrative:
	•	“Apparently I’m above average in [X] even though it’s pretty luck-driven.”
	•	“This very skill-heavy game keeps reminding me I’m not as clever as I thought.”

This section is optional in a paper, but gold in a blog post.

⸻

8. Caveats, dragons, and open data

Short, punchy reality check:
	•	Estimates have uncertainty:
	•	Games with few plays → noisy p.
	•	BGA player base ≠ entire player population.
	•	Multiplayer Elo is still a model with assumptions; if you model different payoff structures, you’ll get slightly different answers.

Maybe a micro-visual:
	•	A tiny plot or example showing wide error bars for some small game vs tight ones for classics.

End with:
	•	Link to:
	•	Summary CSV / notebook.
	•	Code repo from earlier parts.

This section helps you maintain the “rigorous but playful” vibe instead of “this is The Final Truth”.

⸻

9. Outro: “What this actually tells us about games”

Wrap up with a broader reflection rather than more stats:
	•	Some games are popular because they’re forgiving, noisy, and social.
	•	Others are popular because they are punishingly skill-based.
	•	Your skill-o-meter doesn’t tell people which games they should play; it keeps everyone honest about what’s really happening when they sit down at the table.

And a final nod back to the series:
	•	Part 1: how Elo works.
	•	Part 2: snooker prediction as a concrete case.
	•	Part 3: p-deterministic toy universes and σ as a skill measure.
	•	Part 4: making the thing work for real multiplayer games.
	•	Part 5: pointing the calibrated machine at actual board games and reading off the messy, delightful truth.

⸻

That outline should give you:
	•	3–4 big plots (global skill map, upsets, player-count curve, your fingerprint),
	•	2–3 compact tables (top skill / luck, expectation vs reality),
	•	A clean narrative arc from “we built this thing” → “here’s what it says about real games and about us”.

Enough rigour for the nerds, enough stories and pictures for everyone else.
