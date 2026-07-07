# SdJ prediction articles — data recipes

How to (re)fill the stat tables and embeds in `content/posts/sdj_<year>_3/index.md`.
Substitute the year's BGG ids and poll/thread ids. Round stats to one decimal;
bold the leader per column.

## Stat-table columns

| Column  | Source |
|---------|--------|
| Jury    | `reviews.csv` in the post dir: mean of per-reviewer scores, count in parens (`7.2 (4)`). |
| R.G     | `rec_rating` for the `S_d_J` bot (query below). |
| Average | `avg_rating` in `../board-game-data/scraped/bgg_GameItem.csv`. |
| Bayes   | `bayes_rating`, same CSV. |
| Poll    | BGG geekpoll percentage (recipe below). |

## R.G recommendation scores for a fixed set of games

Reversed year range excludes every game, so only `include=` remains — one request,
no pagination (the endpoint pages 25 at a time and ignores `page_size`). Mirrors the
`yearMin=2026&yearMax=2025` in the article's R.G links.

```bash
curl -s "https://recommend.games/api/games/recommend/?user=S_d_J\
&year__gte=<year>&year__lte=<year-1>&exclude_known=true\
&include=<comma,separated,bgg_ids>"
```

`rec_rating` is the column value. Scores can shift year-round (model retrains) —
that's fine to update. Pipeline reference: `spiel-des-jahres/.../predictions.py`.

## BGG polls / threads

boardgamegeek.com is behind Cloudflare (403 "Just a moment"; `xmlapi2` is 401).
Use `api.geekdo.com` with a browser User-Agent:

```bash
# thread first post body contains [poll=<pollid>]
curl -s -A "$UA" "https://api.geekdo.com/api/articles?threadid=<threadid>"
# option labels: options.columns[].bodyXml <safehtml>
curl -s -A "$UA" "https://api.geekdo.com/api/polls/<pollid>"
# vote counts: rows[].columns[].voteCount, joined on columnId
curl -s -A "$UA" "https://api.geekdo.com/api/polls/<pollid>/results"
```

Poll stays open until the ceremony — re-pull just before publishing. Kinderspiel
has no jury reviews; that category is gut-feeling only.

## Predictions are historical — never regenerate

The `prediction #N` ranks are forecasts made before the nominations. Never re-run
the predictions pipeline / regenerate `predictions.csv` to freshen them. Only live
measures (R.G, ratings, poll) get updated.

## Embeds

- `layouts/shortcodes/youtube.html` is a clone of Hugo's built-in with an optional
  `max-width`; output is byte-identical when it's omitted. Re-verify that after any
  Hugo upgrade.
- Named params can't mix with a positional id: `{{< youtube id=XXXX max-width="640px" >}}`.
- Enumerate a channel's clips:
  `uvx yt-dlp --flat-playlist --print "%(id)s | %(title)s" <channel>/videos`.
  Jury clips: `youtube.com/user/spieldesjahres`. Designer interviews: `@FiveGamesForDoomsday`.
