---
title: "Who wins the 2026 World Cup? Not Spain, apparently."
subtitle: "Elo, part 2d: the group stage is done and the model has changed its mind"
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

<!--
TODO (final pass before tomorrow's noon-Helsinki publish, after the 72-result run):
  * Numbers below are the 66-result conditional run — Groups J, K and L still
    have their last matchday. Once they finish, run the full conditional update
    and refresh: the title table, the market table, the bracket image + animation
    and any number quoted in prose (each table is flagged inline).
  * Face-plant / hit tables: add the J/K/L outcomes; the rest are locked.
  * Bracket-shape paragraph: re-confirm the halves once J/K/L resolve.
  * State the exact Elo snapshot timestamp in the elo-source footnote.
-->

## Half-time team-talk

The group stage is over, the Round of 32 is set and seventy-two matches have quietly rearranged everything I told you three weeks ago. ⚽️

When I [ran the numbers before kickoff]({{<ref "posts/elo_2c/index.md">}}) the model had a bold, market-contrarian opinion: 🇪🇸 Spain to win it at 35.3%, 🇦🇷 Argentina second at 23.0% and both *dramatically* underpriced by the bookies — Spain's +19.3pp edge over Polymarket was the strongest disagreement between maths and money I'd ever put on this blog. I promised I'd come back on the other side of the trophy ceremony to find out whether the model deserved its confidence.

This is not that piece. Consider it the half-time team-talk: an unscheduled check-in I hadn't planned to write, prompted by the fact that two weeks of actual football have done something the ten million pre-tournament simulations didn't — they've made the model change its own mind. 🇪🇸 Spain are no longer the favourite. 🇦🇷 Argentina are. Before we get to *why*, let's do the honest thing and grade the homework.

## Where the model was right, and where it face-planted

Elo prices the long run. It does not price two good weeks or two bad ones, which is exactly what a World Cup group stage is — so the gap between what the model expected in June and what actually happened is where the story lives.

And it lives loudest in the exact fixture I built the goal model around. Back in [part 2c]({{<ref "posts/elo_2c/index.md">}}) my worked example was 🇪🇸 Spain vs 🇨🇻 Cape Verde — a 579-point Elo gap so lopsided the Poisson had to be *floored* just to give 🇨🇻 Cape Verde a pulse. The model gave 🇪🇸 Spain **94.1%** to win, 🇨🇻 Cape Verde **1.0%**, and a most-likely scoreline of 3–0. The actual result, in Spain's own group: **0–0.** 🇨🇻 Cape Verde held the biggest paper favourite of the entire group stage to a goalless draw, qualified from Group H on their own merits, and turned my tidy little example into the biggest upset of the tournament so far. That floor of 0.25 expected goals I spent a whole paragraph justifying? It earned its keep.

Some of the pre-tournament reads aged badly:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇺🇾 Uruguay | 95.0% | Out |
| 🇹🇷 Turkey | 86.8% | Out |
| 🇨🇿 Czech Republic | 76.8% | Out |
| 🇵🇦 Panama | 65.3% | Out |
<!-- TODO: add any J/K/L casualties once those groups finish -->

Group H produced two of the tournament's headline inversions at once: 🇺🇾 Uruguay out and 🇨🇻 Cape Verde in — a near-perfect reversal of what the ratings expected from 🇪🇸 Spain's group.

And some aged rather well:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇬🇭 Ghana | 7.9% | Through |
| 🇨🇻 Cape Verde | 24.3% | Through |
| 🇦🇺 Australia | 52.4% | Through |
| 🇸🇪 Sweden | 52.1% | Through |
| 🇪🇬 Egypt | 66.7% | Through |
| 🇺🇸 USA | 68.1% | Through |
<!-- TODO: add any J/K/L overperformers once those groups finish -->

There's no single lesson here beyond the obvious one the [snooker write-ups]({{<ref "posts/elo_2b/index.md">}}) kept circling: a rating integrated over years of competitive results is a statement about the long run, and a 48-team knockout that turns on three matches per side will always hand you a fistful of upsets the rating never saw coming. 🇬🇭 Ghana going from a 7.9% no-hoper to a certainty is not the model being wrong — it's the model being a prior, and the football being the evidence.

## The bracket, for real this time

In [part 2c]({{<ref "posts/elo_2c/index.md">}}) you watched ten million *imagined* brackets blur into an average — a probability cloud hovering over a knockout draw that didn't exist yet. Now the draw is real: the group winners and runners-up are settled, the eight best third-placed teams slot in, and the same animation runs again — except this time the entrants are fact rather than forecast, and only the knockout rounds are still being simulated.

{{< video src="bracket_and_counter" alt="Animation of the simulated brackets freezing into the predicted average while the title-win counter fills in" >}}

Here is the left-hand panel of that animation, frozen for inspection:

{{< img src="knockout_bracket" alt="The 2026 World Cup knockout bracket from the Round of 32 to the final; each slot shows the team most likely to fill it and how often it does across ten million simulations" >}}

And the shape is unkind to 🇪🇸 Spain. 🇦🇷 Argentina and 🇪🇸 Spain are still in opposite halves — they cannot meet before the final — but 🇫🇷 France, a market co-favourite all along whose form the group stage duly confirmed, have landed in 🇪🇸 Spain's half. The top half is now a two-heavyweight pile-up: 🇪🇸 Spain reach the final from there about 40% of the time and 🇫🇷 France about 38%, which means one of them most likely knocks the other out in the semis. 🇦🇷 Argentina, by contrast, has the run of a far softer bottom half — 57% to reach the final, with 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England a distant next at 10%. That single asymmetry — France stacked on top of Spain, Argentina with daylight — is most of why the model now makes 🇦🇷 Argentina the favourite. <!-- TODO: re-confirm the halves and these reach-final percentages once Groups J/K/L finish -->

## The format is a disgrace, and now I can prove it

Allow me a paragraph of editorial — I think I've earned it. We just played **seventy-two** group matches to send **sixteen** teams home, and bar 🇨🇻 Cape Verde's opening-night ambush almost all of it went to script. Two genuine surprises in three weeks — 🇺🇾 Uruguay and 🇹🇷 Turkey, both odds-on to qualify, both out — and everyone else who was meant to advance, advanced. Three weeks of football to confirm what the ratings already knew in June.

It was also *less competitive* than a World Cup should be, and for once I can put a number on the grumble. A **blow-out** — a win by three goals or more — landed in better than a quarter of this group stage's matches. Across the seven tournaments of the 32-team era, 1998 to 2022, that rate averaged **14.6%** and never once cleared 21%:

| Edition | Group-stage blow-outs (≥3 GD) |
|:--------|------------------------------:|
| 1998 | 16.7% |
| 2002 | 12.5% |
| 2006 | 14.6% |
| 2010 | 10.4% |
| 2014 | 20.8% |
| 2018 | 16.7% |
| 2022 | 10.4% |
| **2026** | **27.3%** |

Nearly **double** the historical norm and clear of every previous edition by a street. Invite sixteen more teams who have no business on the same pitch as the elite, and the scoreboards say exactly that.[^blowout-data] <!-- TODO: re-pull the 2026 figure off the final 72-match group stage -->

The tie-break ladder did its own damage, turning a slab of the last round of group games into dead rubbers — or worse, into invitations to collude. As I write this, 🇩🇿 Algeria vs 🇦🇹 Austria is about to kick off in a situation that was arithmetically clear before a ball was kicked — because they play last, with perfect information on every other group. Any draw sends *both* of them through: with four points each, they are guaranteed to be among the eight best third-place teams regardless of how Groups K and L finish. A 2026 restaging of the [Disgrace of Gijón](https://en.wikipedia.org/wiki/Disgrace_of_Gij%C3%B3n), 🇩🇪 West Germany and 🇦🇹 Austria's infamous 1982 non-aggression pact — and deeply unfair on whoever finished their own group two days earlier without that arithmetic in hand.

But the bracket makes the incentives even more perverse than in 1982. The group runner-up in J draws 🇪🇸 Spain in the Round of 32 — tournament favourites, Elo 2157 — while a third-place finish routes you to 🇧🇪 Belgium or 🇨🇭 Switzerland. **Algeria has no incentive to win.** A win makes them runner-up and hands them Spain; a draw makes them third and sends them to a vastly easier R32 opponent, while still guaranteeing qualification. Austria faces Spain either way if they draw (they finish second on goal difference), but — and here is where the game design truly eats itself — depending on what happened in Groups K and L, Austria may be *guaranteed* through even as third after a narrow loss. Specifically, if Group K ended in a draw between 🇨🇩 Congo and 🇺🇿 Uzbekistan — leaving the third-place slot there with just two points — Austria with three points and a one-goal deficit is still mathematically locked into the top eight third-place teams regardless of how Group L finished. In that scenario Austria's rational play is to *lose* — offloading Spain onto Algeria, who would rather not have them. Both teams arrive knowing all of this. The 1982 Disgrace involved two teams quietly agreeing to a convenient win; the 2026 edition may involve two teams quietly agreeing on who gets to lose.<!-- TODO: update tomorrow — did they draw, did one side win, did Austria take the dive to avoid Spain? -->

And the bracket it spat out — the one up above — is a lottery. A seeded draw exists to keep the best sides apart until the business end; this one does the reverse. **Five of the eight likely Round-of-16 ties pit two top-twelve Elo teams against each other** — 🇪🇸 Spain vs 🇵🇹 Portugal, 🇫🇷 France vs 🇩🇪 Germany, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England vs 🇲🇽 Mexico, 🇧🇷 Brazil vs 🇳🇴 Norway, 🇨🇴 Colombia vs 🇨🇭 Switzerland — fixtures a sane bracket saves for the quarter-finals at the earliest. One round sooner still, 🇳🇱 Netherlands draw 🇲🇦 Morocco, a 2022 semi-finalist, in the Round of 32: a last-eight tie demoted to a first-knockout-round coin toss. Half the heavyweights are slated to knock each other out before the thing even feels like it has started. <!-- TODO: re-confirm these ties once Groups J/K/L finish -->

So after three weeks and seventy-two matches, the tournament finally *starts in earnest* — with the strongest thirty-two teams, single elimination. Which is to say it starts exactly where snooker's World Championship and every other event I've ever pointed this model at *began*. We took the scenic route.

For the record: I loathe FIFA's greed and I think 48 teams is a format only an accountant could love. But — and it costs me something to admit it — the bloat does make the *simulation* more fun: more teams, more bracket chaos, more for the model to get spectacularly wrong. A small mercy. I am already, grimly, looking forward to the inevitable 64-team edition.

## Ten million tournaments, conditioned this time

The engine is the one from [part 2c]({{<ref "posts/elo_2c/index.md">}}): Elo into a fixed-total Poisson, a full group stage under FIFA's tie-break ladder, the 495-row third-place lookup, then the knockouts. Two things are different now. First, the simulation is *conditioned* on reality — every played scoreline is pinned to what actually happened, so the ten million tournaments only branch from the Round of 32 onward.[^conditional] Second, the Elo ratings have been refreshed to absorb three weeks of results, so the inputs themselves have shifted under the model.

The effect on the title race is dramatic:

| Team | Pre-tournament | Now |
|:-----|---------------:|----:|
| 🇦🇷 Argentina | 23.0% | **33.0%** |
| 🇪🇸 Spain | 35.3% | **24.6%** |
| 🇫🇷 France | 12.7% | **22.1%** |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 6.0% | 4.3% |
| 🇨🇴 Colombia | 3.3% | 3.5% |
| 🇧🇷 Brazil | 3.9% | 3.5% |
| 🇵🇹 Portugal | 3.5% | 2.3% |

<!-- TODO: refresh this whole table off the 72-result run. -->

That counter piling up on the right of the animation settles, after all ten million runs, into the model's current pecking order:

{{< img src="title_probabilities" alt="Horizontal bar chart of the top 15 teams by conditional title probability, led by Argentina with Spain and France close behind" >}}

The favourite swap is only half the story now. 🇦🇷 Argentina overtaking 🇪🇸 Spain at the top was already the headline at the last check-in; what's new is 🇫🇷 France. Pre-tournament France were a distant third at 12.7%; they've since rocketed to **22.1%**, close enough to breathe on 🇪🇸 Spain's 24.6% for second place. So the podium has gone from "Spain, daylight, Argentina, daylight, the chasing pack" to a genuine three-horse race — 🇦🇷 Argentina out front around a third, then 🇪🇸 Spain and 🇫🇷 France all but level behind. Spain didn't so much collapse as get caught: the serene, group-of-death-free procession the rating projected in June has met both some real on-pitch resistance and, as the bracket just showed, 🇫🇷 France parked squarely in its half.

## Model vs market, take two

The spine of part 2c was a number: 🇪🇸 Spain's +19.3pp edge over Polymarket, the model screaming *value* where the market shrugged. The obvious question for a follow-up is whether that disagreement resolved — and if so, who blinked.

Both did. They're converging.

| Team | Model now | Market now | Edge now | *(Edge pre-tournament)* |
|:-----|----------:|-----------:|---------:|------------------------:|
| 🇦🇷 Argentina | 33.0% | 17.6% | **+15.4pp** | *(+14.7pp)* |
| 🇪🇸 Spain | 24.6% | 12.2% | **+12.4pp** | *(+19.3pp)* |
| 🇫🇷 France | 22.1% | 21.1% | +1.0pp | *(−2.9pp)* |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 4.3% | 10.0% | −5.7pp | *(−4.5pp)* |
| 🇨🇴 Colombia | 3.5% | 1.4% | +2.0pp | *(+1.5pp)* |
| 🇧🇷 Brazil | 3.5% | 5.5% | −2.0pp | *(−4.4pp)* |

<!-- TODO: refresh off the 72-result run; consider restoring the decimal-odds
     columns used in parts 2b/2c (model_decimal_odds, market_decimal_odds). -->

> **Disclaimer**: This section discusses betting odds for the purpose of statistical comparison and analysis. It is not intended to promote gambling or serve as betting advice. Please gamble responsibly and be aware of your local laws and age restrictions.

And the same picture plotted log-log, so the disagreements stand out:

{{< img src="market_vs_model" alt="Log-log scatter of conditional model versus Polymarket title probabilities, with the diagonal marked and the biggest disagreements labelled" >}}

Look at 🇪🇸 Spain. The famous +19.3pp edge has shrunk to +12.4pp — and it shrank from *both ends*: the model cooled on Spain (35.3% → 24.6%) and so did the market (16.0% → 12.2%), meeting partway. That's the healthiest possible outcome for a disagreement: not one side capitulating, but two independent forecasters watching the same football and drifting toward each other.

🇦🇷 Argentina is the opposite kind of story — a disagreement that *held its ground*. The market more than doubled their implied chance, from 8.3% to 17.6%, almost keeping pace with the model's own climb from 23% to 33% — so Argentina's edge has barely moved, +14.7pp in June and +15.4pp now. Argentina is simply the value bet 🇪🇸 Spain was before kickoff, for the same structural reasons (a kind set of group results, a strong Elo and now the soft half of the bracket) the model liked Spain in the first place.

And 🇫🇷 France are the cleanest convergence of the lot. Pre-tournament the model sat *below* the market on France (12.7% against 15.6%, a −2.9pp edge); both have since surged France into the low twenties — model 22.1%, market 21.1% — landing almost exactly on top of each other at +1.0pp. When two forecasters who began a tournament disagreeing end it agreeing, the football has usually spoken loudly enough for both.

Further down, the pattern from the snooker pieces survives intact: 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, 🇧🇷 Brazil and 🇩🇪 Germany all still carry a market premium the rating won't pay — the established-name, *knows-how-to-win-a-tournament* tax that betting crowds price into famous shirts and Elo simply can't see. We [flagged exactly this for Ronnie O'Sullivan]({{<ref "posts/elo_2b/index.md">}}); it turns out international football has its Ronnies too.

## Final whistle, reprise ⚽

So the model has eaten its own headline — and then some. 🇪🇸 Spain were *probably* going to win this thing; now it's 🇦🇷 Argentina out front, 🇫🇷 France gatecrashing the podium, and the market — for once — shuffled most of the way toward agreeing. The +19.3pp argument I picked with the bookies in June is half-settled, amicably, with both sides having moved toward the middle.

I said in part 2c I'd be back on the other side of the trophy ceremony to find out whether the model deserved its confidence. That piece is still coming on July 19. Treat this as the half-time talk: the favourite has changed, 🇨🇻 Cape Verde have already made a mockery of my neatest prediction, the bracket is finally real and there are sixteen knockout ties between here and the only result that actually grades the homework.

*All the code, data snapshots and figures for this article live on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/world_cup_2026).*

[^conditional]: The simulator's `--conditional` mode pins every played group scoreline to its real result and refreshes the Elo snapshot, then simulates only the still-undecided matches. It writes to a parallel set of files so the frozen pre-tournament forecast from part 2c stays reproducible — the baseline never gets quietly overwritten by mid-tournament data.
[^elo-source]: As before, ratings come from [eloratings.net](https://eloratings.net/), the established World Football Elo Ratings, refreshed after every international. <!-- TODO: state the exact refreshed snapshot timestamp used for the final run. -->
[^vig-and-odds]: Decimal odds quote the total return per unit stake including the stake, so fair odds for probability \\(p\\) are exactly \\(1/p\\). Summed across all 48 contracts the market-implied probabilities exceed 100% — the overround is the house's cut. Polymarket's is about 3%; a typical sportsbook is closer to 5–8%. The house always wins.
[^blowout-data]: Blow-out rates are computed from the [martj42 international-results dataset](https://github.com/martj42/international_results), taking each 32-team World Cup's group stage to be its first 48 matches (8 groups of 4). The 2026 figure is over the 66 group matches played at the time of writing, with the final six still to come in Groups J, K and L.
