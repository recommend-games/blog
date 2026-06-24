<!--
TODO (before publish):
  * All numbers in this draft come from the PROVISIONAL 48-result conditional run
    (matchday 2 complete). Refresh every figure off the 72-result run once the
    group stage actually concludes, then delete this banner.
  * §"The bracket, for real this time" needs the filled-bracket chart. That
    generator does not exist yet — the conditional pipeline produces the title,
    group, draw-luck and market charts but no bracket visual. Build it, wire a
    plots/conditional/knockout_bracket.{svg,png}, add an asset-links.yaml entry,
    then replace the placeholder shortcode.
  * Set the real publish `date` and confirm `share_img` once the refreshed
    title_probabilities PNG is regenerated.
-->
---
title: "Who wins the 2026 World Cup? Not Spain, apparently."
subtitle: "Elo, part 2d: the group stage is done and the model has changed its mind"
slug: world-cup-2026-knockouts
share_img: /posts/world-cup-2026-knockouts/title_probabilities_share.png
author: Markus Shepherd
type: post
date: 2026-07-01T12:00:00+03:00 # TODO: real date once groups conclude
tags:
  - Elo rating
  - Football
  - World Cup
---

## Half-time team-talk

The group stage is over, the Round of 32 is set and ninety-six matches have quietly rearranged everything I told you three weeks ago. ⚽️

When I [ran the numbers before kickoff]({{<ref "posts/elo_2c/index.md">}}) the model had a bold, market-contrarian opinion: 🇪🇸 Spain to win it at 35.3%, 🇦🇷 Argentina second at 23.1% and both *dramatically* underpriced by the bookies — Spain's +19.3pp edge over Polymarket was the strongest disagreement between maths and money I'd ever put on this blog. I promised I'd come back on the other side of the trophy ceremony to find out whether the model deserved its confidence.

This is not that piece. Consider it the half-time team-talk: an unscheduled check-in I hadn't planned to write, prompted by the fact that two weeks of actual football have done something the ten million pre-tournament simulations didn't — they've made the model change its own mind. 🇪🇸 Spain are no longer the favourite. 🇦🇷 Argentina are. Before we get to *why*, let's do the honest thing and grade the homework.

## Where the model was right, and where it face-planted

Elo prices the long run. It does not price two good weeks or two bad ones, which is exactly what a World Cup group stage is — so the gap between what the model expected in June and what actually happened is where the story lives.

Some of the pre-tournament reads aged badly:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇹🇷 Turkey | 86.8% | Out |
| 🇪🇨 Ecuador | 98.4% | On the brink <!-- TODO: confirm final group-stage outcome --> |
| 🇺🇾 Uruguay | 95.0% | On the brink <!-- TODO: confirm --> |
| 🇨🇿 Czech Republic | 76.8% | Out |

And some aged rather well:

| Team | Pre-tournament qualify | Reality |
|:-----|----------------------:|:--------|
| 🇬🇭 Ghana | 7.9% | Through |
| 🇨🇻 Cape Verde | 24.3% | Through |
| 🇦🇺 Australia | 52.4% | Through |
| 🇸🇪 Sweden | 52.1% | Through |
| 🇪🇬 Egypt | 66.7% | Through |
| 🇺🇸 USA | 68.1% | Through |

There's no single lesson here beyond the obvious one the [snooker write-ups]({{<ref "posts/elo_2b/index.md">}}) kept circling: a rating integrated over years of competitive results is a statement about the long run, and a 48-team knockout that turns on three matches per side will always hand you a fistful of upsets the rating never saw coming. 🇬🇭 Ghana going from a 7.9% no-hoper to a certainty is not the model being wrong — it's the model being a prior, and the football being the evidence.

## The bracket, for real this time

Before the tournament I could only show you a probability *cloud* — the modal path through a knockout draw that didn't exist yet. Now it does. All 32 survivors are known, the Round of 32 pairings are fixed and for the first time the bracket is a real object rather than an average over ten million imagined ones.

<!-- TODO: replace with the real filled-bracket chart once the generator exists.
     {{< img src="knockout_bracket" alt="The 2026 World Cup knockout bracket from the Round of 32 to the final, annotated with each team's model win probability for every tie" >}} -->
> 🚧 **Bracket chart goes here.** *(Filled Round-of-32-to-final bracket with per-tie win probabilities — chart generator still to be built.)*

The shape matters more than it did pre-tournament, because position is now destiny. <!-- TODO: write this paragraph against the REAL bracket once groups conclude. Cover: who drew the kind path, which half each of Argentina/Spain/France landed in, whether the two favourites can now meet before the final (pre-tournament they could only collide IN the final), and how the host nations' brackets resolved. --> The headline question is whether 🇦🇷 Argentina and 🇪🇸 Spain are still kept apart until a possible final, or whether the group results have thrown them into the same half — because that single fact moves the title numbers below as much as any change in form.

## Ten million tournaments, conditioned this time

The engine is the one from [part 2c]({{<ref "posts/elo_2c/index.md">}}): Elo into a fixed-total Poisson, a full group stage under FIFA's tie-break ladder, the 495-row third-place lookup, then the knockouts. Two things are different now. First, the simulation is *conditioned* on reality — every played scoreline is pinned to what actually happened, so the ten million tournaments only branch from the Round of 32 onward.[^conditional] Second, the Elo ratings have been refreshed to absorb three weeks of results, so the inputs themselves have shifted under the model.

The effect on the title race is dramatic:

| Team | Pre-tournament | Now |
|:-----|---------------:|----:|
| 🇦🇷 Argentina | 23.1% | **34.4%** |
| 🇪🇸 Spain | 35.3% | **24.8%** |
| 🇫🇷 France | 12.7% | 16.0% |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 6.0% | 5.3% |
| 🇨🇴 Colombia | 3.3% | 3.9% |
| 🇵🇹 Portugal | 3.5% | 3.0% |
| 🇧🇷 Brazil | 3.8% | 2.3% |

<!-- TODO: refresh this whole table off the 72-result run. -->

The favourite swap is the entire story. Pre-tournament 🇪🇸 Spain led 🇦🇷 Argentina by more than twelve points; that lead has not just narrowed, it has *inverted*, with Argentina now roughly ten points clear. Spain didn't collapse — a ~25% title chance is still a strong second favourite — but the serene, group-of-death-free procession the rating projected in June has met some actual resistance, and the rating has updated accordingly. 🇫🇷 France are the quiet beneficiaries, edging up into a clear third.

## Model vs market, take two

The spine of part 2c was a number: 🇪🇸 Spain's +19.3pp edge over Polymarket, the model screaming *value* where the market shrugged. The obvious question for a follow-up is whether that disagreement resolved — and if so, who blinked.

Both did. They're converging.

| Team | Model now | Market now | Edge now | *(Edge pre-tournament)* |
|:-----|----------:|-----------:|---------:|------------------------:|
| 🇦🇷 Argentina | 34.4% | 14.1% | **+20.3pp** | *(+14.8pp)* |
| 🇪🇸 Spain | 24.8% | 13.8% | **+11.0pp** | *(+19.3pp)* |
| 🇫🇷 France | 16.0% | 18.7% | −2.7pp | *(−2.9pp)* |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | 5.3% | 10.7% | −5.4pp | *(−4.5pp)* |
| 🇵🇹 Portugal | 3.0% | 7.9% | −4.9pp | *(−6.7pp)* |
| 🇨🇴 Colombia | 3.9% | 1.5% | +2.3pp | *(+1.5pp)* |

<!-- TODO: refresh off the 72-result run; consider restoring the decimal-odds
     columns used in parts 2b/2c (model_decimal_odds, market_decimal_odds). -->

> **Disclaimer**: This section discusses betting odds for the purpose of statistical comparison and analysis. It is not intended to promote gambling or serve as betting advice. Please gamble responsibly and be aware of your local laws and age restrictions.

Look at 🇪🇸 Spain. The famous +19.3pp edge has shrunk to +11.0pp — and it shrank from *both ends*: the model cooled on Spain (35.3% → 24.8%) and so did the market (16.0% → 13.8%), meeting somewhere in the middle. That's the healthiest possible outcome for a disagreement: not one side capitulating, but two independent forecasters watching the same football and drifting toward each other.

🇦🇷 Argentina went the other way. The model and the market *both* warmed to them — the market nearly doubled their price-implied chance from 8.3% to 14.1% — but the model warmed faster, so the edge actually widened to +20.3pp. Argentina is now the value bet that Spain was in June, for the same structural reasons (a kind set of group results, a strong Elo) the model liked Spain before the ball was kicked.

Further down, the pattern from the snooker pieces survives intact: 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, 🇵🇹 Portugal, 🇧🇷 Brazil and 🇩🇪 Germany all carry a market premium the rating won't pay — the established-name, *knows-how-to-win-a-tournament* tax that betting crowds price into famous shirts and Elo simply can't see. We [flagged exactly this for Ronnie O'Sullivan]({{<ref "posts/elo_2b/index.md">}}); it turns out international football has its Ronnies too.

## Final whistle, reprise ⚽

So the model has eaten its own headline. 🇪🇸 Spain were *probably* going to win this thing; now it's 🇦🇷 Argentina, and the market — for once — has shuffled most of the way toward agreeing. The +19.3pp argument I picked with the bookies in June is half-settled, amicably, with both sides having moved.

I said in part 2c I'd be back on the other side of the trophy ceremony to find out whether the model deserved its confidence. That piece is still coming on July 19. Treat this as the half-time talk: the favourite has changed, the bracket is finally real and there are sixteen knockout ties between here and the only result that actually grades the homework.

*All the code, data snapshots and figures for this article live on [GitLab](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/world_cup_2026).*

[^conditional]: The simulator's `--conditional` mode pins every played group scoreline to its real result and refreshes the Elo snapshot, then simulates only the still-undecided matches. It writes to a parallel set of files so the frozen pre-tournament forecast from part 2c stays reproducible — the baseline never gets quietly overwritten by mid-tournament data.
[^elo-source]: As before, ratings come from [eloratings.net](https://eloratings.net/), the established World Football Elo Ratings, refreshed after every international. <!-- TODO: state the exact refreshed snapshot timestamp used for the final run. -->
[^vig-and-odds]: Decimal odds quote the total return per unit stake including the stake, so fair odds for probability \\(p\\) are exactly \\(1/p\\). Summed across all 48 contracts the market-implied probabilities exceed 100% — the overround is the house's cut. Polymarket's is about 3%; a typical sportsbook is closer to 5–8%. The house always wins.
