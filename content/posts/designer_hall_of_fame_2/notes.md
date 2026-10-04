# Scratch notes: Designer Hall of Fame, part 2

Working notes for rewriting `index.md`. Not for publication.

## Status

- `index.md` is a first draft, written by copying large parts of part 1 (`../designer_hall_of_fame/index.md`) word for word. **That draft is rejected.** The article needs to be written fresh, not patched. Don't reuse sentences from part 1.
- The numbers in the draft were checked independently and are correct, with the exceptions listed under "Fixes" below.
- All the stats below are produced by `experiments/sdj_designers/SdJ winning designers.py` (jupytext; the paired `.ipynb` is gitignored). Run it from that directory with `uv run jupytext --sync "SdJ winning designers.py"`, then `uv run jupyter nbconvert --to notebook --execute --inplace "SdJ winning designers.ipynb"`. (`jupytext --update --execute` has kept stale cell outputs.) Outputs: `designers_2026.csv`, `games_2026.csv`, `table_2026.md`.
- Data covers the awards up to and including 2026. BGG game 464279 (a 2026 Kinderspiel recommendation) is still missing from the BGG scrape, so the designer stats are based on 896 of the 897 listed games (see the TODO in `index.md`). Re-run once the scrape has it.

## The hook

Reiner Knizia's Kennerspiel 2026 win (*Rebirth*) makes him the first designer to win all three categories. Lead with this and with the Knizia stories below.

## Decisions already made (don't relitigate)

- **Wins count for more than nominations.** The ranking (wins → special awards → nominations → recommendations) stays as it is.
- **No adjusting for era.** List sizes changed over the decades (e.g. 3–5 games on the Spiel shortlist in 2001–2010, 3 since 2011). Like any sports record, we accept that and don't adjust for it or write disclaimers about it.
- **For designer stats, special awards count as shortlisted** (and as recommended). This is already how the code works.
- **Wolfgang Kramer & Klaus Teuber shared nine Spiel des Jahres awards** between 1986 and 2000. That sentence is correct as long as it's clearly about the Spiel des Jahres; it is.
- **BGG designer credits are taken at face value** (e.g. Yves Hirschfeld is Yves Hirschfeld, no need to verify).
- **Dropped as boring:** co-design partnerships (Kramer & Kiesling, the Brands, …) and trends in how often games are co-designed.

## Fixes needed relative to the current draft

1. **Hall of Fame cutoff wording.** It should say "at least 2 wins (special awards included) or at least 5 listed games". The draft says "5 nominations", which is wrong: Wittig, Burm, Siegers, Shafir and Zeimet are in the table without a single nomination. The code has it right (`HALL_OF_FAME` in the notebook).
2. **Say whether each table is cumulative.** The games table is cumulative ("Nominated" includes winners; "Recommended" is the entire longlist). The designer table is exclusive (wins / nominations / recommendations). Label both clearly.
3. **Dangling reference.** The draft says "I've already mentioned that the first 12 Kinderspiel winners were really special awards", but the paragraph it refers to was not carried over. Either explain the history (Kinderspiel awarded as a special award 1989–2000, its own award since 2001; we count those years as regular winners) or drop the reference.
4. The 896 vs 897 games and 277 vs 278 Kinderspiel recommendations mismatch (TODO comment in `index.md`).

## Story material (all checked against the data)

### Knizia (definitely in)

- **18 years between wins:** *Keltis* (Spiel 2008) → *Rebirth* (Kennerspiel 2026). That ties the record with **Michael Kiesling**: *Torres* (Spiel 2000) → *Azul* (Spiel 2018). Next longest: Andreas Seyfarth, 12 years (*Manhattan* 1994 → *Thurn and Taxis* 2006).
- **18 years from first to most recent win** (*Whoowasit?* 2008 → *Rebirth* 2026), second only to **Kiesling's 19** (*Tikal* 1999 → *Azul* 2018). Then Randolph 15 (*Enchanted Forest* 1982 → *Leinen los!* 1997), Kramer 14 (*Heimlich & Co.* 1986 → *Torres* 2000), Seyfarth 12.
- **The only designer to win two categories in the same year:** *Keltis* (Spiel) and *Whoowasit?* (Kinderspiel), both 2008.
- **A long career:** listed in 26 seasons between 1992 and 2026; 38 listed games, 14 of them shortlisted. **20 listed games before his first win** (first listing 1992, first win 2008).
- **Two shortlisted games in the same year, three times** (more than anyone else): 2004 (*Ingenious*, Spiel; *Treasure of the Dragons*, Kinderspiel), 2005 (*Mago Magino*, *Ribbit*, both Kinderspiel), and 2008 (both wins).
- **He won at his first shot at the triple** (see next section).

### Shots at the triple

Definition: shortlisted in the third category while already holding regular wins in the other two. A shot was only possible from 2011, when the Kennerspiel started.

| Year | Designer | Shortlisted for | Wins already held | Result |
|---|---|---|---|---|
| 2013 | Wolfgang Kramer | Kennerspiel: *The Palaces of Carrara* | Spiel 1986 (+4 more), Kinderspiel 1991 | missed |
| 2021 | Antoine Bauza | Kinderspiel: *Mia London* | Kennerspiel 2011, Spiel 2013 | missed |
| 2026 | Markus Slawitscheck | Spiel: *Morty Sorty Magic Shop* | Kennerspiel 2023, Kinderspiel 2024 | missed |
| 2026 | **Reiner Knizia** | Kennerspiel: *Rebirth* | Spiel 2008, Kinderspiel 2008 | **won** |

- **Kramer was the first** to get a shot.
- **In 2026, two designers went for the triple at the same time.**
- Other designers with wins in two categories, and their record in the third:
  - Warsch (Kennerspiel 2018, Kinderspiel 2025): nominated for the Spiel in 2018, but that was before his second win, so not a shot.
  - Cathala (Spiel 2017, Kinderspiel 2021): Kennerspiel longlist only (*7 Wonders Duel* 2016, *Frosted Blooms* 2026).
  - Inka & Markus Brand (Kennerspiel 2012 & 2017, Kinderspiel 2013): Spiel longlist only (*La Boca* 2013, *Word Slam* 2017).
  - Randolph (Spiel 1982, Kinderspiel 1989): never listed for the Kennerspiel.
  - Bogen (Kinderspiel 2012, Spiel 2014): never listed for the Kennerspiel.

### Wins in the same or consecutive years (good; fits Knizia's two in 2008)

- Kramer: *Heimlich & Co.* (Spiel 1986) → *Auf Achse* (Spiel 1987)
- Teuber: *Hoity Toity* (Spiel 1990) → *Wacky Wacky West* (Spiel 1991)
- Kramer & Kiesling: *Tikal* (Spiel 1999) → *Torres* (Spiel 2000)
- Knizia: *Whoowasit?* and *Keltis*, both 2008
- Inka & Markus Brand: *Village* (Kennerspiel 2012) → *The Enchanted Tower* (Kinderspiel 2013)
- Pfister & Pelikan: *Broom Service* (Kennerspiel 2015) → *Isle of Skye* (Kennerspiel 2016)
- Slawitscheck: *Challengers!* (Kennerspiel 2023) → *Magic Keys* (Kinderspiel 2024)

### Several shortlisted games in one year (good)

Knizia did it three times (2004, 2005, 2008), Warsch twice (2018, 2022), everyone else once.

- 2004 Knizia: *Ingenious* (Spiel), *Treasure of the Dragons* (Kinderspiel)
- 2004 Kramer: *Maharaja* (Spiel), *Macius* (Kinderspiel)
- 2005 Knizia: *Mago Magino*, *Ribbit* (both Kinderspiel)
- 2006 Grunau: *Just4Fun* (Spiel), *Giro Galoppo* (Kinderspiel)
- 2008 Knizia: *Keltis* (Spiel, won), *Whoowasit?* (Kinderspiel, won)
- 2018 Kiesling: *Azul* (Spiel, won), *Heaven & Ale* (Kennerspiel)
- 2018 Warsch: *The Mind* (Spiel), *That's Pretty Clever!*, *Quacks* (both Kennerspiel, *Quacks* won) – the only case with three games
- 2021 Marie & Wilfried Fort: *Dragomino* (won), *Storytailors* (both Kinderspiel)
- 2022 Warsch: *That's Pretty Clever! Kids*, *Quacks & Co.* (both Kinderspiel)
- 2024 Leacock: *Daybreak* (won), *Ticket to Ride Legacy* (both Kennerspiel)
- 2026 Sirieix: *Mooki Island* (won), *Boo Party* (both Kinderspiel)

### Long waits from first listing to first win (keep)

- **Yves Hirschfeld:** *Schoko & Co.* recommended in 1988 → won the Kinderspiel 2023 with *Mysterium Kids: Captain Echo's Treasure*. 35 years.
- ***Endeavor* → *Endeavor: Deep Sea*:** Carl de Visser & Jarratt Gray were recommended in 2010 and won the Kennerspiel in 2025.
- Others: Günter Burkhardt (1997 → 2018), Manfred Ludwig (1983 → 2003), Jens-Peter Schliemann (2005 → 2022), Knizia (1992 → 2008), Matt Leacock (2009 → 2024).
- The full list (10+ years) is in the "Newcomers among the winners" section of the notebook.

### Honourable mentions: the best never to win

This means designers who **never won the main award**. It does **not** mean winners just below the Hall of Fame cutoff; nobody cares about the next names below a cutoff. Ranked by games on the shortlist (special awards included), then by listed games. See the "Honourable mentions" cell in the notebook.

- **Jürgen P. Grunau:** 5 shortlisted (2 Spiel, 3 Kinderspiel). All 5 of his listed games made the shortlist, and none won.
- **Stefan Dorra:** 3 shortlisted (2 Spiel, 1 Kinderspiel) out of 10 listed games.
- **Stefan Feld:** 3 Kennerspiel nominations out of 9 listed games.
- **Leo Colovini:** 3 shortlisted (2 Spiel, 1 Kinderspiel) out of 8 listed games, on the lists from 1988 to 2023.
- **Matthew Dunstan:** 3 shortlisted (1 Spiel, 2 Kennerspiel) out of 4 listed games.
- **Rob Daviau:** 2 Kennerspiel nominations and 1 special award (*Pandemic Legacy: Season 2*, 2018). All 3 listed games made the shortlist.
- **Hans Raggan:** 3 shortlisted (1 Spiel, 2 Kinderspiel) out of 3 listed games.
- **Uwe Rosenberg:** 8 listed games, including *Bohnanza* and *Patchwork* (recommended) and *Nova Luna* (nominated). His only award is *Agricola*'s 2008 special award.

## Not for this article: a separate article idea

The jury frequently rewards first-time or little-known designers. 66 of the 103 winning designers won with a game first listed in their debut year on the lists, and 47 of 103 never had another game listed. This contrasts sharply with "legendary Knizia completes the first triple", so it is out of scope here and deserves its own deep dive (games published before the win, age at winning, …). Tracked in GitLab issue recommend.games/blog#217.
