# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```
npm run build      # python src/scripts/build_site.py — regenerates public/ from source
npm run preview    # python -m http.server 8000 --directory public — serve the built site
```

No linter, test runner, or package manager install needed. Only dependency is Python 3.

## Architecture

This is a bilingual (EN + zh-CN) personal site deployed via GitHub Pages. A single Python script reads JSON data and Markdown content, then writes complete static HTML into `public/`.

**Build pipeline (`src/scripts/build_site.py`):**
1. Wipes `public/`, copies `src/assets/` → `public/assets/`
2. Loads `src/data/site.json`, `src/data/home.json`, plus all `.md` files from `content/posts/` and `content/projects/`
3. Generates one HTML file per page per language — homepage, blog index, project index, individual post pages, individual project pages
4. Writes a root `public/index.html` that browser-redirects based on `navigator.language`
5. Uses Python `html.escape()` throughout — no template engine

**Content (`content/`):**
- Posts and projects are Markdown files with YAML frontmatter (`--- … ---`). Supporting data in `content/meta/` (authors, categories, tags). `_template.*.md` files are skipped during build.
- Frontmatter keys: `title`, `lang` (`en` or `zh-CN`), `slug`, `date`, `category`, optional `summary`

**CSS (`src/styles/` → `src/assets/styles.css`):**
The Tailwind config is for editor intellisense only — no PostCSS/build step. Styles are hand-written CSS organized BEM-style: `base/` (reset, variables, typography), `components/` (header, hero, section, cards, footer), `layouts/` (grid, container). The compiled bundle at `src/assets/styles.css` is what gets deployed. When editing styles, edit both the source file in `src/styles/` AND the compiled `src/assets/styles.css` (or recompile with Tailwind CLI if configured).

**JavaScript (`src/assets/site.js`):**
Single deployed JS file. Handles: (1) intro overlay with sessionStorage dismissal, (2) scroll-reveal via IntersectionObserver (`[data-reveal]` elements), (3) copyright year auto-fill (`[data-year]`), (4) KaTeX math rendering on `.article-shell` elements. The individual files in `src/scripts/` are reference/source versions; the deployed file is `src/assets/site.js`.

**Bilingual content pattern:**
Each post/project has two `.md` files — one per language (e.g., `2026-why-personal-site.md` and `2026-why-personal-site.zh-CN.md`). They share the same `slug` in frontmatter but have different `lang` values. The build script cross-links them at the bottom of each detail page.

**Deployment:**
GitHub Actions (`.github/workflows/pages.yml`) builds on push to `main` — runs the Python build script, uploads `public/` as a Pages artifact, deploys to GitHub Pages.
