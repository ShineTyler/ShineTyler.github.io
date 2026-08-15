# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```
npm run build      # python src/scripts/build_site.py — regenerates public/ from source
npm run test       # python -m unittest discover -s tests — stdlib-only unit tests
npm run preview    # python -m http.server 8000 --directory public — serve the built site
```

Maintenance scripts (run once, when assets change):
```
python src/scripts/fetch_fonts.py     # re-download self-hosted Google Fonts woff2 (latin subset)
python src/scripts/make_og_image.py   # regenerate the Open Graph cover PNG (needs Pillow)
```

No linter, test runner, or package manager install needed. Only dependency is Python 3
(plus the vendored pure-Python `markdown` library in `src/vendor/` — no install step).

## Architecture

This is a bilingual (EN + zh-CN) personal site deployed via GitHub Pages. A small Python
package reads JSON data and Markdown content, then writes complete static HTML into `public/`.

**Build pipeline (`src/scripts/sitebuild/`):**
- `build.py` — orchestration: wipes `public/`, copies `src/assets/` → `public/assets/`, loads data, writes every page for every language plus SEO files
- `config.py` — path constants, `SITE_URL`, and the bilingual `UI` string tables with the `t(lang, key)` lookup helper
- `data.py` — JSON loading and Markdown frontmatter parsing (`ContentEntry`)
- `markdown.py` — Markdown → HTML via the vendored Python-Markdown library (tables, fenced code, blockquotes, h1–h6, nested lists), plus `$`-math protection for KaTeX, plain-text helpers, and bilingual reading-time estimates (CJK ~400 chars/min)
- `render.py` — page templates for both languages (home, about, blog index, projects index, category/tag collections, post/project pages with prev/next pager, 404) using `html.escape()` throughout — no template engine
- `feeds.py` — sitemap.xml, robots.txt, and per-language RSS feeds
- `src/scripts/build_site.py` — thin compatibility entry point (kept so `npm run build` and CI stay unchanged)

**Bilingual layout:**
- English pages live at the site root (`/`, `/blog/…`); Chinese pages under `/zh-CN/` with the same relative structure
- Every page carries `<html lang>`, canonical URL, Open Graph/Twitter meta, and `hreflang` alternates when the counterpart exists
- The masthead has an EN/中文 switch; the blog index of each language lists only that language's posts
- UI copy: `UI` dicts in `config.py`; homepage copy: `src/data/home.json` (EN) and `src/data/home.zh-CN.json` (zh)

**Vendored dependency (`src/vendor/markdown/`):**
Python-Markdown (BSD-3-Clause), committed with its `LICENSE.md` and `dist-info`. Extensions
are referenced by fully-qualified names (`markdown.extensions.tables`) because entry-point
resolution needs the dist-info on `sys.path`.

**Fonts (`src/assets/fonts/`):**
Self-hosted, latin subset, no CDN: Playfair Display (variable woff2, weight axis 400–900) and
IBM Plex Mono (static woff2 at 400/500/600 + italic). Fallbacks: Young Serif Web / JetBrains
Mono Web. Critical fonts are preloaded in the head.

**KaTeX:** loaded only on pages whose Markdown contains `$` math (`with_math` in `shell_html`).

**Tests (`tests/test_build.py`):**
Stdlib `unittest` covering frontmatter parsing, math protection, Markdown rendering
(headings/tables/fences/links/images/blockquotes), reading-time estimates, bilingual helpers,
and page-template structure. CI runs them before building.

**Content (`content/`):**
- Posts and projects are Markdown files with YAML frontmatter (`--- … ---`). Supporting data in `content/meta/` (authors, categories, tags). `_template.*.md` files are skipped during build.
- Frontmatter keys: `title`, `lang` (`en` or `zh-CN`), `slug`, `date`, `category`, optional `summary`, `tags`
- Two files with the same `slug` but different `lang` are treated as translations: the build emits `hreflang` alternates and the language switch links them directly
- Category pages (`/blog/categories/<name>/`) and tag pages (`/blog/tags/<name>/`) are generated per language
- Math is written with `$…$` / `$$…$$` and rendered by KaTeX at page load.

**CSS (`src/assets/styles.css` + mirror in `src/styles/components/magazine.css`):**
The Tailwind config is for editor intellisense only — no PostCSS/build step. Styles are
hand-written CSS. `src/assets/styles.css` is the compiled bundle that gets deployed; the
magazine theme is scoped to `body.magazine` and mirrored in
`src/styles/components/magazine.css`. When editing styles, edit both files.

**JavaScript (`src/assets/site.js`):**
Single deployed JS file. Handles: (1) intro overlay with sessionStorage dismissal, (2) scroll-reveal
via IntersectionObserver (`[data-reveal]` elements), (3) copyright year auto-fill (`[data-year]`),
(4) KaTeX math rendering on `.article-shell` elements, (5) magazine page-turn transitions between
internal links.

**Deployment:**
GitHub Actions (`.github/workflows/pages.yml`) runs the tests, then builds on push to `main` —
uploads `public/` as a Pages artifact, deploys to GitHub Pages.

## Legacy leftovers

- `src/pages/*.html` — stale reference templates from an earlier version; not used by the build (see `src/pages/README.md`).
- `src/styles/base/…`, `src/styles/components/…` (except `magazine.css`) and `src/scripts/main.js` — outdated source sketches; the deployed artifacts are `src/assets/styles.css` and `src/assets/site.js`.
