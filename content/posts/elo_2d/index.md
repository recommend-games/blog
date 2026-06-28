---
title: "Who wins the 2026 World Cup? Not Spain, apparently."
subtitle: "Elo, part 2d — extra time: the group stage is done and the model has changed its mind"
slug: world-cup-2026-knockouts
share_img: /posts/world-cup-2026-knockouts/title_probabilities_share.png
author: Markus Shepherd
type: post
date: 2026-06-28T12:00:00+03:00 # tomorrow, noon Helsinki
tags:
  - Elo rating
  - Football
  - World Cup
---

The group stage is over, the Round of 32 is set — and the model has changed its mind. ⚽️

When I [ran the numbers before kickoff]({{<ref "posts/elo_2c/index.md">}}) the model had a bold, market-contrarian opinion: 🇪🇸 Spain to win it at 35.3%, 🇦🇷 Argentina second at 23.0% and both *dramatically* underpriced by the bookies — Spain's +19.3pp edge over Polymarket was the strongest disagreement between maths and money I'd ever put on this blog. I promised I'd come back on the other side of the trophy ceremony to find out whether the model deserved its confidence.

This is not that piece. Consider it extra time: an unscheduled period I hadn't planned to write, called because seventy-two matches of actual football have done what ten million simulations couldn't. 🇪🇸 Spain are no longer the favourite. 🇦🇷 Argentina are. Before we get to *why*, let's do the honest thing and grade the homework.

## Where the model was right, and where it face-planted

Elo prices the long run. It does not price two good weeks or two bad ones, which is exactly what a World Cup group stage is — so the gap between what the model expected in June and what actually happened is where the story lives.

And it lives loudest in the exact fixture I built the goal model around. Back in [part 2c]({{<ref "posts/elo_2c/index.md">}}) my worked example was 🇪🇸 Spain vs 🇨🇻 Cape Verde — a 579-point Elo gap so lopsided the Poisson had to be *floored* just to give 🇨🇻 Cape Verde a pulse. The model gave 🇪🇸 Spain **94.1%** to win, 🇨🇻 Cape Verde **1.0%**, and a most-likely scoreline of 3–0. The actual result: **0–0.** 🇨🇻 Cape Verde held the biggest paper favourite of the entire group stage to a goalless draw, qualified from Group H anyway, and turned my tidy little example into the biggest upset of the tournament so far. That floor of 0.25 expected goals I spent a whole paragraph justifying? It earned its keep.

Some of the pre-tournament reads aged badly:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇺🇾 Uruguay | 95.0% | Out |
| 🇹🇷 Turkey | 86.8% | Out |
| 🇨🇿 Czech Republic | 76.8% | Out |

Group H produced two of the tournament's headline inversions at once: 🇺🇾 Uruguay out and 🇨🇻 Cape Verde in — a near-perfect reversal of what the ratings expected from 🇪🇸 Spain's group.

And some aged rather well:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇬🇭 Ghana | 7.9% | Through |
| 🇨🇻 Cape Verde | 24.3% | Through |
| 🇨🇩 DR Congo | 25.4% | Through |

There's no single lesson here beyond the obvious one the [snooker write-ups]({{<ref "posts/elo_2b/index.md">}}) kept circling: a rating integrated over years of competitive results is a statement about the long run, and a 48-team knockout that turns on three matches per side will always hand you a fistful of upsets the rating never saw coming. 🇬🇭 Ghana going from a 7.9% no-hoper to a certainty is not the model being wrong — it's the model being a prior, and the football being the evidence.

## The bracket, for real this time

The group stage is done, so instead of simulating 72 matches and then the knockouts, the engine only needs to simulate forward from the Round of 32 — much like the [snooker simulations]({{<ref "posts/elo_2b/index.md">}}) that always started from a fixed draw.

{{< video src="bracket_and_counter" alt="Animation of the simulated brackets freezing into the predicted average while the title-win counter fills in" >}}

Here is the left-hand panel of that animation, frozen for inspection:

{{< img src="knockout_bracket" alt="The 2026 World Cup knockout bracket from the Round of 32 to the final; each slot shows the team most likely to fill it and how often it does across ten million simulations" >}}

And the shape is unkind to 🇪🇸 Spain. 🇦🇷 Argentina and 🇪🇸 Spain are still in opposite halves — they cannot meet before the final — but 🇫🇷 France, a market co-favourite all along whose form the group stage duly confirmed, have landed in 🇪🇸 Spain's half. The top half is now a two-heavyweight pile-up: 🇪🇸 Spain reach the final from there about 40% of the time and 🇫🇷 France about 38%, which means one of them most likely knocks the other out in the semis. 🇦🇷 Argentina, by contrast, has the run of a far softer bottom half — 55% to reach the final, with 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England next at 14%.

🇪🇸 Spain's modal path to the final: 🇩🇿 Algeria (1780), 🇵🇹 Portugal (1990), 🇧🇪 Belgium (1884), 🇫🇷 France (2123). 🇦🇷 Argentina's: 🇨🇻 Cape Verde (1622), 🇦🇺 Australia (1800), 🇨🇴 Colombia (2004), 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (2038). Both enter the knockouts at an identical Elo of 2144 — the bracket alone turns that into **31.8%** for 🇦🇷 Argentina and **24.7%** for 🇪🇸 Spain.

The effect on the full title race:

| Team | Pre-tournament | Now | Δ |
|:-----|---------------:|----:|--:|
| 🇦🇷 Argentina | 23.0% | **31.8%** | +8.8pp |
| 🇪🇸 Spain | 35.3% | **24.7%** | −10.6pp |
| 🇫🇷 France | 12.7% | **22.2%** | +9.5pp |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 6.0% | 5.7% | −0.3pp |
| 🇨🇴 Colombia | 3.3% | 3.9% | +0.6pp |
| 🇧🇷 Brazil | 3.9% | 3.3% | −0.6pp |
| 🇵🇹 Portugal | 3.5% | 1.8% | −1.7pp |
| 🇳🇱 Netherlands | 2.0% | 2.5% | +0.5pp |

The non-obvious move: 🇫🇷 France, a distant third at 12.7% before kickoff, have surged to **22.2%** — close enough to 🇪🇸 Spain's 24.7% that second place is a genuine coin flip.

## Model vs market, take two

The spine of part 2c was a number: 🇪🇸 Spain's +19.3pp edge over Polymarket, the model screaming *value* where the market shrugged. The obvious question for a follow-up is whether that disagreement resolved — and if so, who blinked.

Both did. They're converging.

| Team | Model now | Market now | Edge now | *(Edge pre-tournament)* |
|:-----|----------:|-----------:|---------:|------------------------:|
| 🇦🇷 Argentina | 31.8% | 22.0% | **+9.8pp** | *(+14.7pp)* |
| 🇪🇸 Spain | 24.7% | 10.5% | **+14.2pp** | *(+19.3pp)* |
| 🇫🇷 France | 22.2% | 22.9% | −0.7pp | *(−2.9pp)* |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 5.7% | 10.4% | −4.7pp | *(−4.5pp)* |
| 🇨🇴 Colombia | 3.9% | 2.4% | +1.5pp | *(+1.5pp)* |
| 🇧🇷 Brazil | 3.3% | 5.6% | −2.4pp | *(−4.4pp)* |

> **Disclaimer**: This section discusses betting odds for the purpose of statistical comparison and analysis. It is not intended to promote gambling or serve as betting advice. Please gamble responsibly and be aware of your local laws and age restrictions.

And the same picture plotted log-log, so the disagreements stand out:

{{< img src="market_vs_model" alt="Log-log scatter of conditional model versus Polymarket title probabilities, with the diagonal marked and the biggest disagreements labelled" >}}

Look at 🇪🇸 Spain. The famous +19.3pp edge has shrunk to +14.2pp — the model cooled on Spain (35.3% → 24.7%) and the market went even further (16.0% → 10.5%). Two independent forecasters watching the same football, drifting toward each other from opposite ends.

🇦🇷 Argentina is a different kind of story — a disagreement that narrowed as the market caught up. The market nearly tripled their implied chance, from 8.3% to 22.0%, outpacing the model's own climb from 23% to 32% — so Argentina's edge has come down, +14.7pp in June and +9.8pp now. Argentina is still the value bet 🇪🇸 Spain was before kickoff, for the same structural reasons (a kind set of group results, a strong Elo and now the soft half of the bracket) the model liked Spain in the first place — just less dramatically so.

And 🇫🇷 France are the cleanest convergence of the lot. Pre-tournament the model sat *below* the market on France (12.7% against 15.6%, a −2.9pp edge); both have since surged France into the low twenties — model 22.2%, market 22.9% — landing almost exactly on top of each other at −0.7pp. When two forecasters who began a tournament disagreeing end it agreeing, the football has usually spoken loudly enough for both.

Further down, the pattern from the snooker pieces survives intact: 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, 🇧🇷 Brazil and 🇩🇪 Germany all still carry a market premium the rating won't pay — the established-name, *knows-how-to-win-a-tournament* tax that betting crowds price into famous shirts and Elo simply can't see. We [flagged exactly this for Ronnie O'Sullivan]({{<ref "posts/elo_2b/index.md">}}); it turns out international football has its Ronnies too.

## The format is a disgrace, and now I can prove it

Allow me a paragraph of editorial — I think I've earned it. We just played **seventy-two** group matches to send **sixteen** teams home, and bar 🇨🇻 Cape Verde's opening-match ambush almost all of it went to script. Two genuine surprises in two weeks — 🇺🇾 Uruguay and 🇹🇷 Turkey, both odds-on to qualify, both out — and everyone else who was meant to advance, advanced. Two weeks of football to confirm what the ratings already knew in June.

It was also *less competitive* than a World Cup should be, and for once I can put a number on the grumble. A **blow-out** — a win by three goals or more — landed in exactly a quarter of this group stage's matches. Across the seven tournaments of the 32-team era, 1998 to 2022, that rate averaged **14.6%** and never once cleared 21%:

| Edition | Group-stage blow-outs (≥3 GD) |
|:--------|------------------------------:|
| 1998 | 16.7% |
| 2002 | 12.5% |
| 2006 | 14.6% |
| 2010 | 10.4% |
| 2014 | 20.8% |
| 2018 | 16.7% |
| 2022 | 10.4% |
| **2026** | **25.0%** |

Nearly **double** the historical norm and clear of every previous edition by a street. Invite sixteen more teams who have no business on the same pitch as the elite, and the scoreboards say exactly that.[^blowout-data]

The tie-break ladder did its own damage, turning a slab of the last round of group games into dead rubbers — or worse, into invitations to collude. 🇩🇿 Algeria and 🇦🇹 Austria faced each other in a situation that was arithmetically clear before a ball was kicked — because they played last, with perfect information on every other group. Any draw would send *both* of them through: with four points each, they were guaranteed to be among the eight best third-place teams regardless of how Groups K and L finished. A 2026 restaging of the [Disgrace of Gijón](https://en.wikipedia.org/wiki/Disgrace_of_Gij%C3%B3n), 🇩🇪 West Germany and 🇦🇹 Austria's infamous 1982 non-aggression pact — and deeply unfair on whoever finished their own group two days earlier without that arithmetic in hand.

But the bracket makes the incentives even more perverse than in 1982. The group runner-up in J draws 🇪🇸 Spain in the Round of 32 — tournament favourites, Elo 2144 — while a third-place finish routes you to 🇧🇪 Belgium or 🇨🇭 Switzerland. **Algeria has no incentive to win.** A win makes them runner-up and hands them Spain; a draw makes them third and sends them to a vastly easier R32 opponent, while still guaranteeing qualification. Austria faces Spain either way if they draw (they finish second on goal difference), but — and here is where the game design truly eats itself — depending on what happened in Groups K and L, Austria may be *guaranteed* through even as third after a narrow loss. Specifically, if Group K ended in a draw between 🇨🇩 Congo and 🇺🇿 Uzbekistan — leaving the third-place slot there with just two points — Austria with three points and a one-goal deficit is still mathematically locked into the top eight third-place teams regardless of how Group L finished. In that scenario Austria's rational play is to *lose* — offloading Spain onto Algeria, who would rather not have them. Both teams arrive knowing all of this. The 1982 Disgrace involved two teams quietly agreeing to a convenient win; the 2026 edition set up the same script — and then finished 3–3. Both qualified as the arithmetic demanded: 🇦🇹 Austria as runners-up facing 🇪🇸 Spain in the Round of 32, 🇩🇿 Algeria as third placed facing 🇨🇭 Switzerland.

<!-- TODO: this whole game-design paragraph is a rough first-draft placeholder — rewrite before publishing -->
This blog is ostensibly about games and their design, so let me name what this is in that language: a **dominant strategy failure**. The rules have produced a situation where the rational play — the strategy that maximises a team's expected outcome — is to *not try to win*. That is the single most fundamental thing a competition can get wrong. It is the first thing you learn to check for when designing a game, the failure mode that any competent designer spots in playtesting before the thing ships, and FIFA managed to bake it into the biggest sporting event on the planet.

I want to be clear: I place exactly zero blame on the players. If you hand rational competitors a set of incentives, they will follow them — that is not cynicism, it is arithmetic. The fault is FIFA's, entirely and obviously. This failure was not unforeseeable; it was *fully predictable* the moment the format was announced.

And the mechanism at fault is not the match schedule — within each group, the final round is already played simultaneously, as it has been since the 1982 outrage. The culprit is that [495-row third-place lookup table]({{<ref "posts/elo_2c/index.md">}}). By routing third-place qualification and bracket placement through a cross-group ranking, FIFA created a system where the *order* in which groups finish determines how much information a third-place team has when it plays its decisive match. 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland and 🇰🇷 South Korea — both locked into third place three days before 🇩🇿 Algeria and 🇦🇹 Austria kicked off, with no idea how many points would be enough or which Round-of-32 match they were playing for — both missed the cut when 🇸🇳 Senegal's +2 goal difference edged 🇮🇷 Iran — also on three points — to the eighth and final qualifying spot. 🇩🇿 Algeria steps onto the pitch knowing every other group's outcome, the exact third-place standings across all sixteen groups, and precisely what a draw versus a loss means for their bracket path. That is not a level playing field. It is a structurally guaranteed information asymmetry that FIFA baked into the format and could trivially have avoided — and the perverse "agree who gets to lose to avoid Spain" incentive is its direct consequence. I do not know what you call a governing body that designs a system this broken forty-four years after showing the world what broken looks like, but I know it is not incompetence.

And the bracket it spat out is a lottery. A seeded draw exists to keep the best sides apart until the business end; this one does the reverse. **Five of the eight likely Round-of-16 ties pit two top-twelve Elo teams against each other** — 🇪🇸 Spain vs 🇵🇹 Portugal, 🇫🇷 France vs 🇩🇪 Germany, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England vs 🇲🇽 Mexico, 🇧🇷 Brazil vs 🇳🇴 Norway, 🇨🇴 Colombia vs 🇨🇭 Switzerland — fixtures a sane bracket saves for the quarter-finals at the earliest. One round sooner still, 🇳🇱 Netherlands draw 🇲🇦 Morocco, a 2022 semi-finalist, in the Round of 32: a last-eight tie demoted to a first-knockout-round coin toss. Half the heavyweights are slated to knock each other out before the thing even feels like it has started.

So after two weeks and seventy-two matches, the tournament finally *starts in earnest* — with the strongest thirty-two teams, single elimination. Which is to say it starts exactly where snooker's World Championship and every other event I've ever pointed this model at *began*. We took the scenic route.

For the record: I loathe FIFA's greed and I think 48 teams is a format only an accountant could love. But — and it costs me something to admit it — the bloat does make the *simulation* more fun: more teams, more bracket chaos, more for the model to get spectacularly wrong. A small mercy. I am already, grimly, looking forward to the inevitable 64-team edition.

## Final whistle ⚽

The model has eaten its own headline — and then some. 🇪🇸 Spain were *probably* going to win this thing; now it's 🇦🇷 Argentina out front, 🇫🇷 France gatecrashing the podium, and the market — for once — shuffled most of the way toward agreeing. The +19.3pp argument I picked with the bookies in June is half-settled, amicably, with both sides having moved toward the middle.

I said in part 2c I'd be back on the other side of the trophy ceremony to find out whether the model deserved its confidence. That piece is still coming on July 19 — the penalty shootout, where the final result decides whether the model held its nerve. Extra time is up: the favourite has changed, 🇨🇻 Cape Verde have already made a mockery of my neatest prediction, the bracket is finally real and there are sixteen knockout ties between here and the only result that actually grades the homework.

*All the code, data snapshots and figures for this article live on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/world_cup_2026).*

[^elo-source]: As before, ratings come from [eloratings.net](https://eloratings.net/), the established World Football Elo Ratings, refreshed after every international. The snapshot used for this article was taken at 2026-06-28T05:00:05Z.
[^vig-and-odds]: Decimal odds quote the total return per unit stake including the stake, so fair odds for probability \\(p\\) are exactly \\(1/p\\). Summed across all 48 contracts the market-implied probabilities exceed 100% — the overround is the house's cut. Polymarket's is about 3%; a typical sportsbook is closer to 5–8%. The house always wins.
[^blowout-data]: Blow-out rates are computed from the [martj42 international-results dataset](https://github.com/martj42/international_results), taking each 32-team World Cup's group stage to be its first 48 matches (8 groups of 4). The 2026 figure is over all 72 group matches.
