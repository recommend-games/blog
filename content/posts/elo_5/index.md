---
title: TODO
subtitle: "Elo, part 5: TODO"
slug: elo-part-5-todo
author: Markus Shepherd
type: post
date: 2025-12-19T12:00:00+02:00
tags:
  - Elo rating
  - board games
  - luck vs skill
---

<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.8.1.min.js" ></script>
<script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-api-3.8.1.min.js" ></script>

# Notes

## Criterion for games included in the analysis

- Enough regular players (100)
- Corresponding BGG entry (drop BGA games which map to the same BGG entry — mostly traditional)
- Competitive (let's remove: BGA rank locked AND coop on BGG)

## Notes on the method and the "skill fraction" / "p-deterministic" metric

- Take it with tons of salt
- Highly depends on player population
  - Some games might attract "try and click around" players
  - Some players might not be as competitive as on other platforms
  - Others might be so competitive that they are willing to cheat (BGA locked down chess ranking because people clearly used bots)
  - BGA has the concept of friendly / unranked match where no Elo will be updated; I used them for Elo calculations anyways
- Remember that we benchmark against p-deterministic, which isn't the same as "skill fraction"
- Also the subtlety about random generators in game (card, dice etc) vs random (unpredictable) outcome
  - Reminder: Tic Tac Toe is fully deterministic (no random elements or hidden information), but amongst an adult population will have 0 skill spread since it will always end in a draw
  - Likewise, a group of chess grandmasters just drawing all the time would look similarly noisy, even though chess is obv highly skill based
- Most importantly: luck vs skill isn't really one-dimensional, and it certainly doesn't mean "better or worse"

{{% bokeh "skill_vs_complexity.json" %}}


# Outline from Gippty

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
