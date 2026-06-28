---
title: "Who wins the 2026 World Cup? Not Spain, apparently."
subtitle: "Elo, part 2d — extra time: the group stage is done and the model has changed its mind"
slug: world-cup-2026-knockouts
share_img: /posts/world-cup-2026-knockouts/knockout_bracket_share.png
author: Markus Shepherd
type: post
date: 2026-06-28T15:45:11+03:00
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
| 🇺🇾 Uruguay | 94.8% | Out |
| 🇹🇷 Turkey | 86.4% | Out |
| 🇮🇷 Iran | 83.9% | Out |
| 🇰🇷 South Korea | 80.7% | Out |

Group H produced two of the tournament's headline inversions at once: 🇺🇾 Uruguay out and 🇨🇻 Cape Verde in — a near-perfect reversal of what the ratings expected from 🇪🇸 Spain's group. Group A pulled the same trick: 🇰🇷 South Korea out, 🇿🇦 South Africa through.

And some aged rather well:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇬🇭 Ghana | 8.3% | Through |
| 🇿🇦 South Africa | 14.0% | Through |
| 🇨🇻 Cape Verde | 24.8% | Through |
| 🇨🇩 DR Congo | 25.4% | Through |

There's no single lesson here beyond the obvious one the [snooker write-ups]({{<ref "posts/elo_2b/index.md">}}) kept circling: a rating integrated over years of competitive results is a statement about the long run, and a 48-team knockout that turns on three matches per side will always hand you a fistful of upsets the rating never saw coming. 🇬🇭 Ghana going from an 8.3% no-hoper to a certainty is not the model being wrong — it's the model being a prior, and the football being the evidence.

## The bracket, for real this time

The group stage is done, so instead of simulating 72 matches and then the knockouts, the engine only needs to simulate forward from the Round of 32 — much like the [snooker simulations]({{<ref "posts/elo_2b/index.md">}}) that always started from a fixed draw.

{{< video src="bracket_and_counter" alt="Animation of the simulated brackets freezing into the predicted average while the title-win counter fills in" >}}

Here is the left-hand panel of that animation, frozen for inspection:

{{< img src="knockout_bracket" alt="The 2026 World Cup knockout bracket from the Round of 32 to the final; each slot shows the team most likely to fill it and how often it does across ten million simulations" >}}

And the shape is unkind to 🇪🇸 Spain. 🇦🇷 Argentina and 🇪🇸 Spain are still in opposite halves — they cannot meet before the final — but 🇫🇷 France, a market co-favourite all along whose form the group stage duly confirmed, have landed in 🇪🇸 Spain's half. The top half is now a two-heavyweight pile-up: 🇪🇸 Spain reach the final from there about 40% of the time and 🇫🇷 France about 38%, which means one of them most likely knocks the other out in the semis. 🇦🇷 Argentina, by contrast, has the run of a far softer bottom half — 55% to reach the final, with 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England next at 14%.

🇪🇸 Spain's modal path to the final: 🇩🇿 Algeria (1780), 🇵🇹 Portugal (1990), 🇧🇪 Belgium (1884), 🇫🇷 France (2123). 🇦🇷 Argentina's: 🇨🇻 Cape Verde (1622), 🇦🇺 Australia (1800), 🇨🇴 Colombia (2004), 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (2038). Both enter the knockouts at an identical Elo of 2144[^elo-source] — the bracket alone turns that into **31.8%** for 🇦🇷 Argentina and **24.7%** for 🇪🇸 Spain.

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

> **Disclaimer**: This section discusses betting odds for the purpose of statistical comparison and analysis. It is not intended to promote gambling or serve as betting advice. Please gamble responsibly and be aware of your local laws and age restrictions.

The spine of part 2c was a number: 🇪🇸 Spain's +19.3pp edge over Polymarket, the model screaming *value* where the market shrugged. The obvious question for a follow-up is whether that disagreement resolved — and if so, who blinked.

Both did. They're converging.[^vig-and-odds]

| Team | Model now | Market now | Edge now | *(Edge pre-tournament)* |
|:-----|----------:|-----------:|---------:|------------------------:|
| 🇦🇷 Argentina | 31.8% | 22.0% | **+9.8pp** | *(+14.7pp)* |
| 🇪🇸 Spain | 24.7% | 10.5% | **+14.2pp** | *(+19.3pp)* |
| 🇫🇷 France | 22.2% | 22.9% | −0.7pp | *(−2.9pp)* |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 5.7% | 10.4% | −4.7pp | *(−4.5pp)* |
| 🇨🇴 Colombia | 3.9% | 2.4% | +1.5pp | *(+1.5pp)* |
| 🇧🇷 Brazil | 3.3% | 5.6% | −2.4pp | *(−4.4pp)* |
| 🇳🇱 Netherlands | 2.5% | 4.2% | −1.7pp | *(−1.9pp)* |
| 🇵🇹 Portugal | 1.8% | 4.9% | −3.1pp | *(−6.7pp)* |

And the same picture plotted log-log, so the disagreements stand out:

{{< img src="market_vs_model" alt="Log-log scatter of conditional model versus Polymarket title probabilities, with the diagonal marked and the biggest disagreements labelled" >}}

The most famous edge — 🇪🇸 Spain's +19.3pp — has shrunk to +14.2pp. Not because the model held firm while the market caught up: both moved. The model cooled on 🇪🇸 Spain (35.3% → 24.7%); the market went further still (16.0% → 10.5%). 🇦🇷 Argentina is the mirror: here the market did the catching up. Polymarket nearly tripled their implied chance from 8.3% to 22.0% while the model climbed more modestly (23.0% → 31.8%), narrowing the gap from +14.7pp to +9.8pp — but leaving 🇦🇷 Argentina as the clearest model-vs-market disagreement that remains.

Further down, the pattern from the [snooker pieces]({{<ref "posts/elo_2b/index.md">}}) survives intact: 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, 🇧🇷 Brazil and 🇵🇹 Portugal all carry a market premium the rating won't pay — the established-name, *knows-how-to-win-a-tournament* tax that betting crowds price into famous shirts and Elo simply can't see. International football has its Ronnies too.

## The format is a disgrace, and now I can prove it

Allow me a paragraph of editorial — I think I've earned it. We just played **seventy-two** group matches to send **sixteen** teams home, and bar 🇨🇻 Cape Verde's opening-match ambush almost all of it went to script. Four teams the model rated above 80% to advance — 🇺🇾 Uruguay, 🇹🇷 Turkey, 🇮🇷 Iran and 🇰🇷 South Korea — all went home; everyone else who was meant to advance, advanced. Two weeks of football to confirm what the ratings already knew in June.

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

More than double the 2022 rate of 10.4%, and clear of every previous edition by a street. Invite sixteen more teams who have no business on the same pitch as the elite, and the scoreboards say exactly that.[^blowout-data]

The tie-break ladder did its own damage. 🇩🇿 Algeria and 🇦🇹 Austria met in their final group match knowing any result would qualify them both — they played last, with perfect information on everything that mattered. Before a ball was kicked, the potential *Disgrace of Kansas City* was already being written about — an echo of the [Disgrace of Gijón](https://en.wikipedia.org/wiki/Disgrace_of_Gij%C3%B3n), in which 🇩🇪 West Germany and 🇦🇹 Austria quietly played out the result that suited them both. But 2026's version was worse: **🇩🇿 Algeria had no incentive to win.** A win promoted them to Group J runners-up and a Round-of-32 tie against 🇪🇸 Spain; a draw kept them third and facing 🇨🇭 Switzerland instead. Winning was actively harmful.

The match ended 3–3 in stoppage time: Mahrez struck in the 90+3 to make it 3-2 before Sasa Kalajdzic equalised in the 90+5 with the last kick of the game. If it was staged, it was staged perfectly — nobody can claim collusion after a finish that dramatic. But from the 60th minute, played at 2–2, both teams were comfortable: the crowd whistled, Laimer was spotted doing stretches, neither side showed any urgency to find a third. You cannot distinguish honest fatigue from rational quiet when the format has already made both look identical.[^austria-incentive]

The teams are not to blame. If the rules reward not trying to win, rational competitors will not try to win — that is what competing means. The fault is FIFA's for designing rules that punish the very instinct they are supposed to reward. Good game design makes the rational move the exciting one; here it made restraint the winning strategy. 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland and 🇰🇷 South Korea paid the price — playing out their fate three days before 🇩🇿 Algeria kicked off, with no idea how many points would be enough or which R32 match they were competing for, while 🇩🇿 Algeria stepped onto the pitch knowing every other group's outcome and exactly what a draw meant for their bracket path. That is not a level playing field. I do not know what you call a governing body that designs a system this broken forty-four years after showing the world what broken looks like, but I know it is not incompetence.

And the bracket it spat out is a lottery. A seeded draw exists to keep the best sides apart until the business end; this one does the reverse. 🇳🇱 Netherlands won Group F; 🇲🇦 Morocco came through Group C — 🇧🇷 Brazil's group — to qualify. Their Round-of-32 reward is each other. 🇵🇹 Portugal vs 🇭🇷 Croatia in the same round is a tie most tournaments would call a quarter-final. The likely Round of 16 brings 🇪🇸 Spain vs 🇵🇹 Portugal and 🇫🇷 France vs 🇩🇪 Germany — fixtures a sane draw saves for the semi-finals.

So after two weeks and seventy-two matches, the tournament finally *starts in earnest* — with the strongest thirty-two teams, single elimination.

For the record: I loathe FIFA's greed and I think 48 teams is a format only an accountant could love. But — and it costs me something to admit it — the bloat does make the *simulation* more fun: more teams, more bracket chaos, more for the model to get spectacularly wrong. Some consolation for this data geek. I am already, grimly, looking forward to the inevitable 64-team edition.

## Final whistle ⚽

The model has eaten its own headline — and then some. 🇪🇸 Spain were *probably* going to win this thing; now it's 🇦🇷 Argentina out front, 🇫🇷 France gatecrashing the podium, and the market — for once — shuffled most of the way toward agreeing. The +19.3pp argument I picked with the bookies in June is half-settled, amicably, with both sides having moved toward the middle.

The bracket has a sense of humour. 🇨🇻 Cape Verde — the team I used in [part 2c]({{<ref "posts/elo_2c/index.md">}}) to illustrate the goal floor, so lightly rated the Poisson needed a minimum just to give them a credible expected-goal figure — held 🇪🇸 Spain to 0-0, qualified from Group H, and drew 🇦🇷 Argentina in the Round of 32. The model has done its sums. *Wichtig is' auf'm Platz*, 🇨🇻 Cape Verde.

Extra time is up. I said in [part 2c]({{<ref "posts/elo_2c/index.md">}}) I'd be back on the other side of the trophy ceremony to find out whether the model deserved its confidence — that piece arrives on 19 July, the penalty shootout. Thirty-one matches stand between here and the only result that actually grades the homework.

*All the code, data snapshots and figures for this article live on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/world_cup_2026).*

[^austria-incentive]: 🇩🇿 Algeria's incentive was simply to avoid winning — a draw was perfectly optimal. 🇦🇹 Austria's position was potentially even more perverse. Had 🇺🇿 Uzbekistan and 🇨🇩 Congo drawn in Group K, that group's third-placed team would have finished with just two points; 🇦🇹 Austria's three pre-match points would then have guaranteed them a top-eight finish among all third-placed teams even after a one-goal defeat — lose by two and they might have been out. In that scenario, losing by a single goal was 🇦🇹 Austria's rational play: hand 🇩🇿 Algeria the runner-up slot (and 🇪🇸 Spain), and collect 🇨🇭 Switzerland instead. A competition worth billions had written rules under which conceding goals on purpose was the winning strategy — good game design makes sure such scenarios cannot arise.
[^elo-source]: As before, ratings come from [eloratings.net](https://eloratings.net/), the established World Football Elo Ratings, refreshed after every international. The snapshot used for this article was taken at 2026-06-28T05:00:05Z.
[^vig-and-odds]: Decimal odds quote the total return per unit stake including the stake, so fair odds for probability \\(p\\) are exactly \\(1/p\\). Summed across all 48 contracts the market-implied probabilities exceed 100% — the overround is the house's cut. Polymarket's is about 3%; a typical sportsbook is closer to 5–8%. The house always wins.
[^blowout-data]: Blow-out rates are computed from the [martj42 international-results dataset](https://github.com/martj42/international_results), taking each 32-team World Cup's group stage to be its first 48 matches (8 groups of 4). The 2026 figure is over all 72 group matches.
