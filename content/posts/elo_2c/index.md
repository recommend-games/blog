---
title: "From the baize to the pitch: predicting the 2026 World Cup with Elo"
subtitle: "Elo, part 2c: one million simulations, 48 teams, three host nations"
slug: world-cup-2026
share_img: /posts/world-cup-2026/title_probabilities.png
author: Markus Shepherd
type: post
date: 2026-06-11T13:00:00-06:00
tags:
  - Elo rating
  - Football
  - World Cup
---

## From cue to cleats

The two snooker entries in this Elo series ([part 2]({{<ref "posts/elo_2/index.md">}}) and [part 2b]({{<ref "posts/elo_2b/index.md">}})) sent the same toolbox — Elo ratings, then a few million simulated tournaments — into the Crucible Theatre to predict the snooker World Championship. With the 2026 FIFA World Cup kicking off today at the Estadio Azteca in 🇲🇽 Mexico City, it seemed a shame not to point the same machinery at a much bigger draw.

A bigger draw in every dimension, really. Snooker's World Championship is a clean 32-player bracket on a single table in Sheffield. The 2026 World Cup is the first 48-team edition, played across three host nations, with twelve groups, an entirely new Round of 32, and a third-place qualification rule that is genuinely fiddly to write down. The Elo ratings on their own won't be enough this time; we'll have to wrap them in a goal-scoring model and a fairly serious bit of bracket bookkeeping before any of it answers the actual question.

That question, again: who lifts the trophy on July 19? And — for a reality check — does the wisdom of the betting market agree?

The short version: the model thinks 🇪🇸 Spain are huge, the bookmakers think 🇪🇸 Spain are merely good, and the gap between those two opinions is by some way the most interesting number in this article. The long version is what follows.


## The new format in one minute

Some of this still feels like it shouldn't be allowed. The 2026 tournament is the first since 1998 to change in size — from 32 teams to 48 — and the first ever co-hosted by three nations: the 🇺🇸 United States, 🇨🇦 Canada, and 🇲🇽 Mexico. The new layout is:

- **12 groups of 4 teams**, named A through L, each playing 3 matches — 72 group fixtures in total.
- **The top two from every group** automatically qualify for a brand-new **Round of 32**.
- **The 8 best third-placed teams** (across the 12 groups) also advance.
- From there it's a familiar single-elimination knockout: R32 → R16 → QF → SF → final. 31 knockout matches.

The "8 best of 12 thirds" rule is the one that quietly bends the bracket. Which third-placed teams qualify depends on the points totals from twelve different groups, and once they qualify, *where* they slot into the R32 depends on which set of group letters they came from. FIFA publishes a 495-row lookup table to nail this down — one row for every distinct subset of 8 groups out of 12 — and the simulator dutifully uses it. The upshot is that the knockout bracket isn't perfectly symmetric: two teams with similar Elo can end up with quite different draws depending on which third-placed peers turn up beside them.

Host advantage is the other format quirk worth flagging. There are three home countries, but they don't host the entire tournament evenly: each plays its own group-stage matches at home and then ventures into a neighbour's stadiums in the knockouts. The model applies a +100 Elo bonus only when a host plays *in* its own country, so 🇲🇽 Mexico's home boost vanishes the moment they step onto a 🇺🇸 US pitch.


## Building the model: Elo meets the pitch

To recap [our usual setup]({{<ref "posts/elo_1/index.md">}}) in one paragraph: each team has an Elo rating \\(r\\), and the expected score for team *A* against team *B* is

\\[ s_A = \frac{1}{1 + 10^{-(r_A - r_B) / 400}}. \\]

For the snooker articles, that number *is* the prediction — you toss a weighted coin and somebody advances. Football is messier: you need an actual scoreline, and a 90-minute draw is a real outcome (in the group stage) or a problem to resolve (in the knockouts).

### From expected score to scorelines

I've gone with a deliberately simple **fixed-total Poisson** model. The two teams' goals are independent Poisson random variables with rates \\(\lambda_A\\) and \\(\lambda_B\\), and those rates are chosen so that

\\[ \lambda_A + \lambda_B = 2.6 \quad\text{and}\quad \Pr(A\text{ wins}) + \tfrac{1}{2}\Pr(\text{draw}) = s_A. \\]

The first constraint pins the expected total goals to 2.6 — pretty close to the historical average for top-level international matches. The second says the lambdas have to be consistent with the Elo expected score. Each fixture turns into a small one-dimensional root-find for the right \\(\lambda_A\\), which `scipy.brentq` does in microseconds and the simulator caches by rounded Elo gap.[^poisson-choice]

One sharp edge: if the Elo gap gets large enough, the system has no valid solution with both lambdas above zero. **🇪🇸 Spain vs 🇨🇻 Cape Verde** is exactly that fixture — 🇪🇸 Spain's Elo is 579 points higher, which says 🇪🇸 Spain should expect roughly \\(2.6\\) goals while 🇨🇻 Cape Verde scores essentially none. The model would otherwise predict a literal "🇨🇻 Cape Verde cannot score" Poisson, which is both wrong (every team has *some* chance) and degenerate (the truncated grid stops being a proper distribution).

The fix is to pin 🇨🇻 Cape Verde's \\(\lambda\\) at a floor of 0.25, let 🇪🇸 Spain's rise above the 2.35 the budget would otherwise allow, and renormalise the truncated joint Poisson grid afterwards. The 🇪🇸 Spain vs 🇨🇻 Cape Verde fixture ends up at \\(\lambda_{\text{ES}} = 3.50\\), \\(\lambda_{\text{CV}} = 0.25\\), and the model's most likely scorelines are 3–0 (16.8%), 4–0 (14.7%), 2–0 (14.4%), 5–0 (10.3%), and 1–0 (8.2%). 🇪🇸 Spain are 94.1% to win the match, 🇨🇻 Cape Verde 1.0%.

### Group stage, tie-breaks, and the third-place puzzle

Inside each simulation, all 72 group fixtures are sampled in one vectorised numpy call, then the four teams in each group are ranked using FIFA's tie-break ladder: points, head-to-head points and goal difference and goals scored on the tied subset, then overall goal difference and goals scored, and finally a fallback on FIFA rank (the published November-2025 list).[^tiebreaks]

Once every group is ranked, the simulator picks the 8 best third-placed teams across all 12 groups and slots them into the Round of 32 via the 495-row lookup table. This is one of the places where football carries more bookkeeping than snooker: a clean draw doesn't exist, just a deterministic rule with a lot of cases.

### Knockouts and extra time

Knockout matches use the same Poisson scoreline model for 90 minutes. If they end level, the simulator advances a team by sampling from the same Elo expected score \\(s_A\\) — no separate extra-time goal process, no penalty shootout sub-model. It's a deliberately Elo-consistent choice: extra time and penalties are exactly the regime where the model would have to invent extra structure it doesn't have, so I let the rating do the talking.

That, plus a host bonus of +100 Elo whenever a host plays in its own country, is the whole machinery. The Monte Carlo loop runs 1,000,000 tournaments with a fixed seed (`20260611`, which is the tournament's opening date, because I am like that) so every published number is exactly reproducible.[^seed] A single laptop chews through it in about four minutes.


## Who's on top? Current Elo and the draw

Here is the snapshot we're starting from. All Elo ratings are from [eloratings.net](https://eloratings.net/) on 2026-06-09 — two days before the opener.[^elo-source]

| Rank | Team        | Group |   Elo | FIFA rank |
|-----:|:------------|:-----:|------:|----------:|
|    1 | 🇪🇸 Spain       |   H   |  2157 |         1 |
|    2 | 🇦🇷 Argentina   |   J   |  2114 |         2 |
|    3 | 🇫🇷 France      |   I   |  2063 |         3 |
|    4 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England     |   L   |  2021 |         4 |
|    5 | 🇧🇷 Brazil      |   C   |  1991 |         5 |
|    6 | 🇵🇹 Portugal    |   K   |  1986 |         6 |
|    7 | 🇨🇴 Colombia    |   K   |  1982 |        13 |
|    8 | 🇳🇱 Netherlands |   F   |  1948 |         7 |
|    9 | 🇪🇨 Ecuador     |   E   |  1938 |        23 |
|   10 | 🇩🇪 Germany     |   E   |  1932 |         9 |

A few things to notice before any tournament is simulated:

- **🇪🇸 Spain and 🇦🇷 Argentina are tier-one**. The gap from 🇦🇷 Argentina to 🇫🇷 France is roughly half the gap from 🇫🇷 France to 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England. The model treats this as two world-class sides plus the chasing pack.
- **Group K is brutal.** 🇵🇹 Portugal *and* 🇨🇴 Colombia, sixth and seventh by Elo, drew the same group. One of them is going home as a third-placed gamble at best.
- **Group E is also unfortunate**. 🇪🇨 Ecuador (9th by Elo) and 🇩🇪 Germany (10th) are sharing four-team housing with 🇨🇮 Ivory Coast and 🇨🇼 Curaçao. The model thinks 🇪🇨 Ecuador and 🇩🇪 Germany both qualify comfortably but won't run away with anything.
- **Group H, by contrast, is a 🇪🇸 Spain coronation.** With 🇺🇾 Uruguay, 🇨🇻 Cape Verde, and 🇸🇦 Saudi Arabia for company, 🇪🇸 Spain are 87.6% to win the group, and 99.9% to qualify.
- **🏴󠁧󠁢󠁥󠁮󠁧󠁿 England** picked up arguably the kindest top-half group of the lot: Group L with 🇭🇷 Croatia, 🇵🇦 Panama, and 🇬🇭 Ghana. 99.1% qualify, 66.7% to win the group.

The full picture of group qualification looks like this:

{{< img src="group_qualification_heatmap" alt="Heatmap of group-qualification probabilities for all 48 teams, arranged by group" >}}

Most groups have a familiar shape — two strong teams comfortably through, two weak ones mostly out. **Group B** stands out for being a coin-flip: 🇨🇭 Switzerland (98.4% to qualify) and 🇨🇦 Canada (98.3%) are essentially indistinguishable, both helped along by 🇨🇦 Canada's home boost. **Group D** is the closest thing to chaos: 🇹🇷 Turkey, 🇵🇾 Paraguay, the 🇺🇸 United States, and 🇦🇺 Australia are all between 53% and 86% to qualify, with 🇺🇸 USA's host bonus pulling them above where their raw Elo would put them.[^group-d]


## One million tournaments later

Now we let the bracket actually play. Here are the top fifteen teams by simulated title probability — the headline answer to "who wins the World Cup?":

{{< img src="title_probabilities" alt="Horizontal bar chart of the top 15 teams by simulated title probability, led by 🇪🇸 Spain at 35.4%" >}}

| Rank | Team        | Title probability | Implied odds |
|-----:|:------------|------------------:|-------------:|
|    1 | 🇪🇸 Spain       |             35.4% |         2.83 |
|    2 | 🇦🇷 Argentina   |             22.8% |         4.39 |
|    3 | 🇫🇷 France      |             12.7% |         7.88 |
|    4 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England     |              6.1% |        16.52 |
|    5 | 🇧🇷 Brazil      |              3.9% |        25.61 |
|    6 | 🇵🇹 Portugal    |              3.6% |        28.07 |
|    7 | 🇨🇴 Colombia    |              3.3% |        30.11 |
|    8 | 🇳🇱 Netherlands |              2.0% |        50.08 |
|    9 | 🇪🇨 Ecuador     |              1.5% |        65.34 |
|   10 | 🇩🇪 Germany     |              1.4% |        72.86 |
|   11 | 🇹🇷 Turkey      |              1.0% |       102.36 |
|   12 | 🇳🇴 Norway      |              0.9% |       108.25 |
|   13 | 🇯🇵 Japan       |              0.8% |       119.90 |
|   14 | 🇲🇽 Mexico      |              0.8% |       127.94 |
|   15 | 🇭🇷 Croatia     |              0.8% |       128.60 |

🇪🇸 Spain at **35.4%** is a startling number on first read — more than a third of a million simulated tournaments end with the trophy in Madrid. That isn't only the Elo lead; it's the Elo lead *plus* the kindest group in the bracket *plus* a knockout path that doesn't run into 🇦🇷 Argentina until the final at the earliest. 🇦🇷 Argentina at 22.8% picks up the same compounding benefit one bracket-half away. Between them they account for **more than half** of all simulated outcomes.

The same simulation produces some interesting near-misses lower down the table. Compare each team's Elo rank against its title-probability rank:

{{< img src="draw_luck" alt="Scatter plot of Elo rank against simulated title probability rank, with off-diagonal teams labelled" >}}

Most teams sit on the diagonal — the draw doesn't help or hurt them much. The visible movers, in roughly descending order of effect: **🇲🇽 Mexico** jumps four spots, from 18th by Elo to 14th by title probability, almost entirely on the back of the +100 host bonus and a friendly Group A. **🇹🇷 Turkey** and **🇯🇵 Japan** also climb a couple of places thanks to favourable bracket positions. On the other side, **🇭🇷 Croatia** drop three spots — they share Group L with 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England, so the favourite they'll likely meet in the knockouts is the strongest team in their half — and **🇧🇪 Belgium**, **🇦🇹 Austria**, and **🇺🇾 Uruguay** all give back a place or two by sharing a group with one of the tier-one sides.

A note on the long tail. Ten of the 48 teams won zero of the million simulated tournaments — among them 🇨🇻 Cape Verde, 🇸🇦 Saudi Arabia, 🇨🇼 Curaçao, 🇶🇦 Qatar, 🇿🇦 South Africa, 🇭🇹 Haiti, and a handful of others. The model isn't *literally* saying their chances are zero; it's saying that with this Elo, this draw, and a million-tournament resolution, no simulation happened to produce a title run. The true probability is genuinely tiny — somewhere between "lottery ticket" and "asteroid".

### Hosts, briefly

What does the +100 host bonus actually buy you? Less than you might hope, for the 🇺🇸 United States and 🇨🇦 Canada. Both reach the knockouts comfortably (🇺🇸 USA 68.1%, 🇨🇦 Canada 98.3% to qualify), and both ride to a respectable group-winner share at home (🇺🇸 USA 21.2% in a genuinely tricky Group D, 🇨🇦 Canada a heady 47.6% in their coin-flip Group B). But their title probabilities are 0.12% and 0.10%: the boost is enough to get them into the bracket, not enough to navigate four knockout rounds against a who's-who of European Elo. 🇲🇽 Mexico fare best of the three at **0.78%**, top of Group A with 75.5% probability and a 38.2% chance of reaching the quarter-finals, but their road runs through 🇪🇸 Spain's half. The home crowds will make for excellent television; the trophy, almost certainly, will not.


## Bookies vs model: where the market disagrees

> **Disclaimer**: This section discusses betting odds for the purpose of statistical comparison and analysis. It is not intended to promote gambling or serve as betting advice. Please gamble responsibly and be aware of your local laws and age restrictions.

I'm still not the gambling kind. But betting markets are too useful as a sanity check to ignore — when real money is on the line, the consensus probability is a serious forecast in its own right.

For this one I've pulled prices from [Polymarket's "World Cup Winner" market](https://polymarket.com/event/world-cup-winner-2026): a crypto-prediction market that runs a separate yes/no contract per team and prices each one continuously. It has the considerable advantage over traditional bookmakers of being machine-readable and only carrying about a 3% overround (compared to 5–8% at a sportsbook), so the de-vigging is quick and clean. The numbers below are from the snapshot taken at 2026-06-09 18:37 UTC.[^market-snap]

To turn a probability into decimal odds, take the reciprocal: a model probability of 35.4% becomes \\(1/0.354 \approx 2.83\\), i.e., a fair-value bet pays €2.83 per €1 staked. The same conversion applies the other way around: market odds of 6.49 imply a market probability of \\(1/6.49 \approx 15.4\%\\).[^vig-and-odds]

Here is the comparison for the top twelve teams. "Edge (pp)" is `model − market` in percentage points; positive means the model thinks the team is undervalued.

| Team        | Model | Market |    Edge | Model odds | Market odds |
|:------------|------:|-------:|--------:|-----------:|------------:|
| 🇪🇸 Spain       | 35.4% |  15.4% | +19.9pp |       2.83 |        6.49 |
| 🇦🇷 Argentina   | 22.8% |   8.5% | +14.3pp |       4.39 |       11.82 |
| 🇫🇷 France      | 12.7% |  15.6% |  −2.9pp |       7.88 |        6.41 |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England     |  6.1% |  10.6% |  −4.5pp |      16.52 |        9.45 |
| 🇧🇷 Brazil      |  3.9% |   8.2% |  −4.3pp |      25.61 |       12.24 |
| 🇵🇹 Portugal    |  3.6% |  10.3% |  −6.7pp |      28.07 |        9.71 |
| 🇨🇴 Colombia    |  3.3% |   1.9% |  +1.4pp |      30.11 |       53.05 |
| 🇳🇱 Netherlands |  2.0% |   3.8% |  −1.8pp |      50.08 |       26.19 |
| 🇪🇨 Ecuador     |  1.5% |   0.8% |  +0.7pp |      65.34 |      121.71 |
| 🇩🇪 Germany     |  1.4% |   5.2% |  −3.8pp |      72.86 |       19.34 |
| 🇹🇷 Turkey      |  1.0% |   1.2% |  −0.2pp |     102.36 |       82.76 |
| 🇳🇴 Norway      |  0.9% |   2.5% |  −1.5pp |     108.25 |       40.57 |

And the picture, plotted log-log so the disagreements are easier to see:

{{< img src="market_vs_model" alt="Log-log scatter of model versus Polymarket title probabilities, with the diagonal marked and the biggest disagreements labelled" >}}

The headline disagreement is enormous. **The market has 🇫🇷 France as the favourite at 15.6%, 🇪🇸 Spain just behind at 15.4%, and 🇦🇷 Argentina sixth at 8.5%.** The model has 🇪🇸 Spain at 35.4% and 🇦🇷 Argentina at 22.8% — both more than double what Polymarket is paying. If the model is right, those are by some distance the two best-value bets in the tournament. If the market is right, the model has badly overestimated two specific sides.

Why might the model be right? Three factors stack up the same way. 🇪🇸 Spain's Elo is genuinely 43 points clear of 🇦🇷 Argentina and almost 100 clear of 🇫🇷 France — the rating system, integrated over years of competitive results, is not subtle about who it likes. Group H is the weakest of the twelve. And the bracket places 🇪🇸 Spain and 🇦🇷 Argentina in opposite halves, so the only way to lose to each other is in the final. Compounding advantages compound.

Why might the market be right? A few real things the Elo rating doesn't see. 🇪🇸 Spain's stretch of major-tournament knockouts has been more disappointing than the rating suggests. 🇦🇷 Argentina's defence of the title comes after two quieter years of friendlies and a moderate Copa run, and the rating still reflects the 2022 peak. And — the pattern we [flagged for Ronnie O'Sullivan]({{<ref "posts/elo_2b/index.md">}}) in the snooker write-up — sometimes the market is paying for something the rating system *can't* quantify: the ineffable "knows how to win a tournament" premium that betting markets price into established names. 🇫🇷 France have it. 🇧🇷 Brazil have it. 🇪🇸 Spain, despite the trophies and the rating, somehow don't.

Lower down the table the agreements and disagreements are easier reading. **🇵🇹 Portugal** at 3.6% model vs 10.3% market is the most overvalued top team by the market's lights — a Cristiano Ronaldo lifetime-achievement premium, perhaps. **🇩🇪 Germany** at 1.4% vs 5.2% reads similarly; the model isn't yet convinced the post-Nagelsmann rebuild has produced an Elo-class side. On the other side, **🇨🇴 Colombia** and **🇪🇨 Ecuador** are the only teams besides 🇪🇸 Spain and 🇦🇷 Argentina that the model fancies more than the market does, both modestly: 🇨🇴 Colombia at +1.4pp, 🇪🇨 Ecuador at +0.7pp. The market consistently prices Conmebol's mid-table sides shorter than the Elo says, and the model consistently looks for value there.

If you forced me to summarise the table in one sentence: the model and the market disagree most violently on the *favourites*, and almost not at all on the long shots. Where the two forecasters do disagree at the top, the resolution will arrive on July 19.


## Final whistle ⚽

We've got 🇪🇸 Spain at 35%, 🇦🇷 Argentina at 23%, and a market that thinks both are dramatically overpriced. We've got a 48-team bracket with twelve groups, a brand-new Round of 32, a 495-row third-place lookup, and a host advantage that helps 🇲🇽 Mexico more than it helps the other two. And we've got one number — 🇪🇸 Spain's +19.9pp edge over Polymarket — that is, by some margin, the strongest disagreement between a rating-driven model and a money-driven crowd I've ever published on this blog.

The tournament starts on June 11 and the final is on July 19. We'll know then whether the model deserves its confidence — or whether one more season of football has done what a million simulated tournaments couldn't, and quietly told us the rating wasn't quite the answer after all.

If the model holds up I'll come back in seven weeks for a *did we get it right?* follow-up, exactly like [last year's snooker rerun]({{<ref "posts/elo_2b/index.md">}}). If it falls flat on its face, I'll come back to admit it. Either way, I'll see you on the other side of the trophy ceremony.

*All the code, data snapshots, and figures for this article live in [`experiments/world_cup_2026/`](https://gitlab.com/recommend.games/blog/-/tree/master/experiments/world_cup_2026) on GitLab.*


[^poisson-choice]: A more sophisticated model would let the two lambdas vary independently (a so-called bivariate Poisson, or a Dixon-Coles correction for the empirically thin draw shoulders). I've deliberately kept v1 honest about its limits — one tunable parameter, one Elo input, and no team-specific attack/defence ratings.
[^tiebreaks]: FIFA's full procedure also includes a fair-play / conduct score before falling back to FIFA rank, which the simulator deliberately doesn't model — yellow- and red-card counts aren't an Elo-derivable quantity.
[^seed]: 20,260,611 — the 20-million-and-change reading of the tournament's opening date. Determinism is a wonderful thing.
[^elo-source]: [eloratings.net](https://eloratings.net/) maintains the established World Football Elo Ratings, updated after every international match. The simulator freezes the snapshot at 2026-06-09 18:08 UTC so that results from inside the tournament can't quietly feed back into the forecast mid-run.
[^group-d]: Group D is also the group where the model's biggest *home* effect lives: without the +100 Elo bonus, the 🇺🇸 United States would be a long way behind 🇹🇷 Turkey and 🇵🇾 Paraguay for qualification rather than essentially tied. The bonus doesn't carry into the knockouts, though — so even a 🇺🇸 USA win in Group D leaves them up against 🇪🇸 Spain's half of the bracket with a vanilla 1726 Elo.
[^market-snap]: Polymarket prices change minute by minute; the comparison is a single snapshot taken just before the tournament started. By the time you read this, the numbers will already have drifted — 🇪🇸 Spain in particular will be priced very differently after match one, regardless of what happens in it.
[^vig-and-odds]: Decimal odds quote the total return per unit stake including the stake, so fair odds for probability \\(p\\) are exactly \\(1/p\\). If you sum the market-implied probabilities across all 48 contracts, you'll get slightly more than 100% — the overround is how the market makes a living. Polymarket's overround on this market is about 3%; a typical sportsbook is closer to 5–8%. Either way: the house always wins.
