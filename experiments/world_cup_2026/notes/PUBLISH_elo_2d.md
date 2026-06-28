# Publishing elo_2d — group-stage knockout follow-up

The runbook for shipping `content/posts/elo_2d/index.md` once the group stage
concludes. Prep items 1-4 are done (asset pipeline wired, bracket exact at full
N, article un-stubbed, local build rehearsed). This is item 5: the exact
publish-day steps and the git policy behind them.

## The one thing that's easy to get wrong

**CI does not regenerate plots or run the simulation.** `.gitlab-ci.yml` runs
only:

```
uv run sync_assets.py     # copies committed source assets into content/posts/
hugo --minify
```

`sync_assets.py` copies the **committed source plots** named in
`asset-links.yaml` into the (gitignored) page bundle. So:

- The copied files in `content/posts/elo_2d/` are build artifacts — do **not**
  commit them (they're in `content/posts/.gitignore`).
- The **source** plots they copy from **must be committed and current**:
  - `experiments/world_cup_2026/plots/conditional/knockout_bracket.svg`
  - `experiments/world_cup_2026/plots/conditional/title_probabilities.png`

Our routine mid-tournament refresh commits deliberately **exclude** plots. **The
publish commit is the exception: it must include the conditional plots**, or the
deployed article renders with broken images.

The site deploys from **`master`** (the `pages` CI job is `only: master`).
`master` tracks `gitlab/master`; there are several remotes, so check
`git remote -v` rather than assuming. Publishing therefore means landing the
final state on `master` (merge MR !129).

## Steps

1. **Group stage concludes (all 72 group matches played).** Confirm
   `data/processed/results.csv` has 72 group rows.

2. **Full update** (per [[project_wc26_full_update]] — the whole conditional
   chain *including* `wc26-bracket-heatmap --conditional`). This refreshes Elo +
   results, runs the 10M sim (which now writes
   `outputs/conditional/bracket_slot_probabilities.csv` exact at 10M), rebuilds
   every conditional CSV and plot, and re-renders the bracket from the canonical
   CSV.

3. **Fill in the article** (`content/posts/elo_2d/index.md`) from the final
   outputs — each blank is flagged with an inline `TODO`:
   - The three numeric tables (face-plant/hit reality, title race,
     model-vs-market) off the 72-result `team_probabilities.csv` /
     `market_comparison.csv`.
   - Confirm the Ecuador / Uruguay "on the brink" rows resolved.
   - Write the §"The bracket, for real this time" **bracket-shape paragraph**
     against the real draw (which half each of Argentina / Spain / France
     landed in, whether the two favourites can meet before the final, the host
     brackets). The committed bracket image already shows the answer.
   - State the exact Elo snapshot timestamp in the `[^elo-source]` footnote
     (from `data/raw/conditional/elo_snapshot_date.txt`).
   - Set the real publish `date`; delete the top TODO banner.

4. **Local build rehearsal** (mirrors CI):

   ```
   uv run sync_assets.py
   hugo            # add -F only if the date is still in the future
   ```

   Confirm `/posts/world-cup-2026-knockouts/` renders with the bracket + share
   image, parses its title, and appears in the elo-rating tag listing.

5. **Commit — plots included this time.** On `wc26-conditional-rerun`:
   - data + outputs CSVs (the refresh)
   - **the conditional plots**, at minimum `knockout_bracket.svg` and
     `title_probabilities.png` (`title_probabilities.svg` too for consistency)
   - the finalised `content/posts/elo_2d/index.md`

6. **Push and merge MR !129 into `master`.** The `pages` job runs
   `sync_assets.py` + `hugo --minify` and deploys. Push to the right remote(s) —
   `master` → `gitlab/master`.

7. **Verify live**, then schedule the *post-final* retrospective the article
   already teases (July 19).

## Not in this publish

The bracket convergence animation (`world_cup_2026/animate_bracket.py`, output
`plots/conditional/bracket_convergence.gif`) is a **separate prototype** — team
codes not flags, GIF not WebM, no easing yet. It is **not** part of elo_2d v1:
don't include it, wire it into `asset-links.yaml` or block the publish on it. If
it ships at all it is its own follow-up (flags + ffmpeg/WebM + a video shortcode).
