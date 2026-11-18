# 🎲 Recommend.Games Blog 📝

Source of [Analysis Paralysis](https://analysisparalysis.games/), built with
[Hugo](https://gohugo.io/) and the
[Beautiful Hugo](https://github.com/halogenica/beautifulhugo) theme.

## Requirements

| Tool               | Version   | Pinned in                          |
| ------------------ | --------- | ---------------------------------- |
| Hugo (standard)    | 0.170.1   | `.gitlab-ci.yml` (`default.image`) |
| Beautiful Hugo     | v5.2.1    | `themes/beautifulhugo` submodule   |
| uv                 | 0.13.9    | `.gitlab-ci.yml` (`UV_VERSION`)    |
| Python (via uv)    | 3.13      | `.gitlab-ci.yml` (`UV_PYTHON`)     |
| PyYAML (via uv)    | 6.0.3     | `sync_assets.py.lock`              |

Use the same Hugo version locally (`hugo version`). CI fails on any build
warning (`--panicOnWarning`), so check a local build for warnings before
pushing.

## Building from a clean checkout

```bash
git clone --recurse-submodules https://gitlab.com/recommend.games/blog.git
cd blog
# or, in an existing clone:
git submodule update --init --recursive

uv run --locked sync_assets.py  # copy generated assets into content/posts
hugo server                     # preview on http://localhost:1313/
hugo --minify                   # production build into public/
```

`sync_assets.py` copies the files listed in `asset-links.yaml` (mostly plots
and CSVs from `experiments/`) into their post bundles and regenerates
`content/posts/.gitignore` so the copies are not committed. Every mapped
source is required: the script exits non-zero if any is missing. Re-run it
whenever an experiment's output changes. Without it, the `img` and `video`
shortcodes fail the build with the name of the missing resource.

## CI and deployment

GitLab CI runs only branch pipelines (no separate merge request pipelines,
so nothing runs twice):

- `test` builds every branch other than the default branch.
- `deploy` builds the default branch and publishes `public/` to GitLab
  Pages. A daily schedule on the default branch republishes the site so
  that posts with a future date go live.

## Custom templates

- `layouts/_default/rss.xml` is Hugo's embedded RSS template with
  `.Summary` replaced by `.Content`, so feeds carry full posts. Keep this
  override until Hugo or the theme offer full-content feeds.
- `layouts/shortcodes/` holds the site's own shortcodes (`img`, `video`,
  `game`, `sdj`, …). Only `video` shadows a theme shortcode: ours plays
  inline like a GIF (autoplay, loop, muted, no controls) and matches `src`
  without its extension, whereas the theme's shows controls and needs the
  exact file name. Keep ours unless posts are migrated to that behaviour.

## Updating Hugo and the theme

This procedure also applies to the
[RH blog](https://gitlab.com/mshepherd/riemannhypothesis.blog), which shares
the same baseline.

1. Read the [Hugo release notes](https://github.com/gohugoio/hugo/releases)
   and the theme's commits since the pinned tag. Look for deprecations and
   template changes.
2. Build the current pin and the candidate from clean checkouts, each in the
   official image (`ghcr.io/gohugoio/hugo:<version>`).
3. Compare the outputs: the set of generated paths, `index.xml`,
   `sitemap.xml`, `<img>`/`<video>` counts and a normalised diff of the
   HTML. Resized images are renamed whenever Hugo's processing hash
   changes, which is expected. Review every remaining difference.
4. Run `hugo --logLevel info` and check for deprecation notices.
5. Bump the image tag in `.gitlab-ci.yml`, the theme submodule and the
   table above in one merge request. Check the branch pipeline before
   merging.
