"""HTML rendering: page shell, headers, footers, and all page templates.

Every render function takes a `lang` ("en" | "zh-CN"). UI chrome comes from
the bilingual string tables in config.py; page content (home copy, post
bodies) is picked per language by the build orchestration.
"""
import html
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote

from .config import (
    LANG_DEFAULT,
    OG_IMAGE_PATH,
    SITE_NAME,
    SITE_URL,
    page_path,
    t,
)
from .data import ContentEntry
from .markdown import first_paragraph, markdown_to_html, reading_time

KNOWN_LANGS = ("en", "zh-CN")


def rel_prefix(depth: int) -> str:
    return "../" * depth


def post_lang(entry: ContentEntry) -> str:
    lang = entry.meta.get("lang", LANG_DEFAULT)
    return lang if lang in KNOWN_LANGS else LANG_DEFAULT


def site_header(
    current: str,
    depth: int,
    magazine: bool = True,
    lang: str = LANG_DEFAULT,
) -> str:
    prefix = rel_prefix(depth)
    home_href = prefix or "./"
    nav = [
        ("home", t(lang, "home"), home_href),
        ("about", t(lang, "about"), f"{prefix}about/"),
        ("projects", t(lang, "projects"), f"{prefix}projects/"),
        ("blog", t(lang, "blog"), f"{prefix}blog/"),
    ]
    if magazine:
        nav_items: List[str] = []
        for idx, (key, label, href) in enumerate(nav, start=1):
            current_attr = ' class="current"' if key == current else ""
            nav_items.append(
                f'<a{current_attr} href="{href}">'
                f'<span class="toc-no">{idx:02d}</span>'
                f'<span class="toc-label">{html.escape(label)}</span></a>'
            )
        nav_html = "\n        ".join(nav_items)
        return f"""
    <header class="site-header masthead">
      <div class="masthead-row">
        <a class="brand" href="{home_href}">
          <span class="brand-wordmark">Tyler&apos;s Corner</span>
        </a>
      </div>
      <nav class="site-nav toc-nav" aria-label="{html.escape(t(lang, 'primary_nav'))}">
        {nav_html}
      </nav>
    </header>"""
    nav_items = []
    for key, label, href in nav:
        current_attr = ' class="current"' if key == current else ""
        nav_items.append(f'<a{current_attr} href="{href}">{html.escape(label)}</a>')
    nav_html = "\n        ".join(nav_items)
    return f"""
    <header class="site-header">
      <a class="brand" href="{home_href}">
        <span class="brand-wordmark">Tyler&apos;s Corner</span>
      </a>
      <nav class="site-nav" aria-label="{html.escape(t(lang, 'primary_nav'))}">
        {nav_html}
      </nav>
    </header>"""


def site_footer(site: dict, home: dict, magazine: bool = True, lang: str = LANG_DEFAULT) -> str:
    if magazine:
        return f"""
    <footer class="site-footer colophon" id="contact">
      <div class="footer-row footer-row-centered"><span>&copy; <span data-year></span> {html.escape(site['owner'])} · {html.escape(site['email'])}</span></div>
    </footer>"""
    return f"""
    <footer class="site-footer" id="contact">
      <div class="footer-row footer-row-centered"><span class="footer-title">{html.escape(home['footer']['closing'])}</span></div>
      <div class="footer-row footer-row-centered"><span>&copy; <span data-year></span> {html.escape(site['owner'])}</span></div>
    </footer>"""


def shell_html(
    title: str,
    description: str,
    body: str,
    depth: int,
    body_class: str = "",
    lang: str = LANG_DEFAULT,
    with_math: bool = False,
    og_type: str = "website",
    canonical: str = "",
    noindex: bool = False,
) -> str:
    prefix = rel_prefix(depth)
    og_locale = "zh_CN" if lang.startswith("zh") else "en_US"
    og_image = SITE_URL + OG_IMAGE_PATH
    canonical_tag = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    robots_tag = '<meta name="robots" content="noindex">' if noindex else ""
    katex_tags = f"""
  <link rel="stylesheet" href="{prefix}assets/vendor/katex/katex.min.css">
  <script defer src="{prefix}assets/vendor/katex/katex.min.js"></script>
  <script defer src="{prefix}assets/vendor/katex/auto-render.min.js"></script>""" if with_math else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  {canonical_tag}
  {robots_tag}
  <meta property="og:site_name" content="{html.escape(SITE_NAME)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:locale" content="{og_locale}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="icon" href="{prefix}assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="{prefix}assets/fonts/Megrim-Regular.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="preload" href="{prefix}assets/fonts/playfair-display-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{prefix}assets/fonts/ibm-plex-mono-w400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
{katex_tags}  <script defer src="{prefix}assets/site.js"></script>
</head>
<body{(' class="' + body_class + '"') if body_class else ""}>
{body}
</body>
</html>
"""


def post_summary(entry: ContentEntry) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A short note about learning in public."
    )


def project_summary(entry: ContentEntry) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A placeholder project that will be expanded later."
    )


def render_post_cards(
    posts: Iterable[ContentEntry], href_prefix: str, lang: str = LANG_DEFAULT
) -> str:
    cards: List[str] = []
    for idx, entry in enumerate(posts, start=1):
        slug = entry.meta["slug"]
        cards.append(
            f"""
          <article class="post-card">
            <div class="card-top"><span class="card-no">{idx:02d}</span><div class="card-meta"><div class="card-kicker">{html.escape(entry.meta.get('date', t(lang, 'start_here')))}</div><span class="meta-pill">{html.escape(reading_time(entry.body, lang))}</span></div></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(post_summary(entry))}</p>
            <a class="card-link" href="{href_prefix}{html.escape(slug)}/">{html.escape(t(lang, 'read_article'))} &rarr;</a>
          </article>"""
        )
    return "".join(cards)


def render_home(
    site: dict,
    home: dict,
    posts: List[ContentEntry],
    lang: str = LANG_DEFAULT,
) -> str:
    title_html = html.escape(" ".join(home["hero"]["title_lines"]))
    recent = posts[:4]
    recent_cards = render_post_cards(recent, "blog/", lang) if recent else (
        f'<div class="card-stack-empty">{html.escape(t(lang, "no_posts"))}</div>'
    )
    body = f"""
  <div class="intro-overlay" role="button" tabindex="0" aria-label="Press start to enter Tyler's blog">
    <div class="intro-overlay-backdrop"></div>
    <div class="intro-overlay-content">
      <h1 class="intro-overlay-title">TYLER</h1>
    </div>
    <button class="intro-overlay-prompt intro-overlay-enter" type="button" aria-label="Press start to enter">
      <span>PRESS</span><span>START</span>
    </button>
    <div class="intro-overlay-arrow" aria-hidden="true">
      <span></span>
      <span></span>
    </div>
  </div>
  <div class="site-shell page-shell">
    {site_header('home', 0, magazine=True, lang=lang)}
    <main>
      <section class="hero" data-reveal>
        <header class="hero-header">
          <p class="eyebrow hero-eyebrow">{html.escape(t(lang, 'cover_eyebrow'))}</p>
          <h1 class="hero-title">{title_html}</h1>
          <p class="hero-subline">{html.escape(home['hero']['subtitle'])}</p>
        </header>
        <div class="hero-body">
          <div class="hero-about">
            <p>{html.escape(home['hero']['portrait_note'])}</p>
            <p>{html.escape(home['about']['card_body'])}</p>
          </div>
        </div>
      </section>
      <section class="section contents-ledger" data-reveal>
        <div class="contents-head">
          <span class="eyebrow">{html.escape(t(lang, 'contents_label'))}</span>
          <a class="contents-vol" href="blog/">{html.escape(t(lang, 'view_all'))} &rarr;</a>
        </div>
        <div class="card-stack">
          {recent_cards}
        </div>
      </section>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    title = site['title']
    return shell_html(
        title,
        t(lang, "home_description"),
        body,
        0,
        body_class="magazine",
        lang=lang,
        canonical=f"{SITE_URL}/{page_path(lang, '')}",
    )


def render_about(site: dict, home: dict, lang: str = LANG_DEFAULT) -> str:
    body = f"""
  <div class="site-shell page-shell">
    {site_header('about', 1, magazine=True, lang=lang)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="eyebrow">{html.escape(t(lang, 'about_eyebrow'))}</p>
        <h1 class="page-title">{html.escape(t(lang, 'about'))}</h1>
        <p class="page-intro">{html.escape(home['about']['section_copy'])}</p>
      </section>
      <section class="section" data-reveal>
        <div class="about-layout">
          <figure class="about-figure">
            <div class="portrait"></div>
            <figcaption class="portrait-caption">{html.escape(t(lang, 'portrait_caption'))}</figcaption>
          </figure>
          <div class="about-prose">
            <p>{html.escape(home['hero']['portrait_note'])}</p>
            <p>{html.escape(home['about']['card_body'])}</p>
          </div>
        </div>
      </section>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    title = f"{t(lang, 'about')} | {site['owner']}"
    return shell_html(
        title,
        t(lang, "about"),
        body,
        1,
        body_class="magazine",
        lang=lang,
        canonical=f"{SITE_URL}/{page_path(lang, 'about/')}",
    )


def render_blog_index(
    site: dict, home: dict, posts: List[ContentEntry], lang: str = LANG_DEFAULT
) -> str:
    cards = render_post_cards(posts, "./", lang) if posts else (
        f'<div class="card-stack-empty">{html.escape(t(lang, "no_posts"))}</div>'
    )
    body = f"""
  <div class="site-shell page-shell">
    {site_header('blog', 1, magazine=True, lang=lang)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="eyebrow">{html.escape(t(lang, 'blog_eyebrow'))}</p>
        <h1 class="page-title">{html.escape(t(lang, 'blog'))}</h1>
        <p class="page-intro">{html.escape(t(lang, 'writing_intro'))}</p>
      </section>
      <section class="section" data-reveal>
        <div class="card-stack">
          {cards}
        </div>
      </section>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    title = f"{t(lang, 'blog')} | {site['owner']}"
    return shell_html(
        title,
        t(lang, "blog_description"),
        body,
        1,
        body_class="magazine",
        lang=lang,
        canonical=f"{SITE_URL}/{page_path(lang, 'blog/')}",
    )


def render_projects_index(
    site: dict, home: dict, projects: List[ContentEntry], lang: str = LANG_DEFAULT
) -> str:
    cards = []
    for idx, entry in enumerate(projects, start=1):
        status = entry.meta.get("status", "draft")
        badge = t(lang, "draft_project") if status == "draft" else status
        cards.append(
            f"""
          <article class="project-card">
            <div class="card-top"><span class="card-no">{idx:02d}</span><div class="card-meta"><div class="card-kicker">{html.escape(t(lang, 'project_label'))}</div><span class="meta-pill">{html.escape(badge)}</span></div></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(project_summary(entry))}</p>
            <a class="card-link" href="./{html.escape(entry.meta['slug'])}/">{html.escape(t(lang, 'read_project'))} &rarr;</a>
          </article>"""
        )
    body = f"""
  <div class="site-shell page-shell">
    {site_header('projects', 1, magazine=True, lang=lang)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="eyebrow">{html.escape(t(lang, 'projects_eyebrow'))}</p>
        <h1 class="page-title">{html.escape(t(lang, 'projects'))}</h1>
        <p class="page-intro">{html.escape(t(lang, 'projects_intro'))}</p>
      </section>
      <section class="section" data-reveal>
        <div class="card-stack">
          {''.join(cards) or f'<div class="card-stack-empty">{html.escape(t(lang, "no_posts"))}</div>'}
        </div>
      </section>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    title = f"{t(lang, 'projects')} | {site['owner']}"
    return shell_html(
        title,
        t(lang, "projects_description"),
        body,
        1,
        body_class="magazine",
        lang=lang,
        canonical=f"{SITE_URL}/{page_path(lang, 'projects/')}",
    )


def render_collection_page(
    site: dict,
    home: dict,
    lang: str,
    kind: str,
    name: str,
    entries: List[ContentEntry],
) -> str:
    label = t(lang, f"{kind}_label")
    intro = t(lang, f"{kind}_intro")
    kind_plural = "categories" if kind == "category" else "tags"
    cards = render_post_cards(entries, "./", lang)
    body = f"""
  <div class="site-shell page-shell">
    {site_header('blog', 2, magazine=True, lang=lang)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="eyebrow">{html.escape(label)}</p>
        <h1 class="page-title">{html.escape(name)}</h1>
        <p class="page-intro">{html.escape(intro)}</p>
        <p class="page-intro"><a class="post-link" href="../">&larr; {html.escape(t(lang, 'back_to_blog'))}</a></p>
      </section>
      <section class="section" data-reveal>
        <div class="card-stack">
          {cards}
        </div>
      </section>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    title = f"{label} — {name} | {site['owner']}"
    return shell_html(
        title,
        intro,
        body,
        2,
        body_class="magazine",
        lang=lang,
        canonical=f"{SITE_URL}/{page_path(lang, 'blog/' + kind_plural + '/' + quote(name) + '/')}",
    )


def _pager_html(
    lang: str, prev: Optional[ContentEntry], nxt: Optional[ContentEntry]
) -> str:
    if not prev and not nxt:
        return ""
    prev_html = (
        f'<a class="pager-prev" href="../{html.escape(prev.meta["slug"])}/" title="{html.escape(prev.meta.get("title", ""))}">&larr; {html.escape(t(lang, "previous_post"))}</a>'
        if prev
        else '<span class="pager-empty"></span>'
    )
    next_html = (
        f'<a class="pager-next" href="../{html.escape(nxt.meta["slug"])}/" title="{html.escape(nxt.meta.get("title", ""))}">{html.escape(t(lang, "next_post"))} &rarr;</a>'
        if nxt
        else '<span class="pager-empty"></span>'
    )
    return f"""
        <nav class="article-pager" aria-label="{html.escape(t(lang, 'primary_nav'))}">
          {prev_html}
          {next_html}
        </nav>"""


def render_post_page(
    site: dict,
    home: dict,
    post: ContentEntry,
    page_no: int = 12,
    prev: Optional[ContentEntry] = None,
    nxt: Optional[ContentEntry] = None,
) -> str:
    lang = post_lang(post)
    title = post.meta.get("title", "Untitled")
    tags_raw = post.meta.get("tags", "")
    tags_html = ""
    if tags_raw:
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
        tags_html = "".join(f'<span class="tag-pill">{html.escape(tag)}</span>' for tag in tags)
    body = f"""
  <div class="site-shell page-shell">
    {site_header('blog', 2, magazine=True, lang=lang)}
    <main>
      <article class="article-shell" data-reveal>
        <header class="article-head">
          <div class="article-topbar">
            <a class="article-back" href="../">&larr; {html.escape(t(lang, 'back_to_blog'))}</a>
          </div>
          <div class="meta-row"><span class="meta-pill">{html.escape(post.meta.get('date', ''))}</span>{tags_html}</div>
          <h1 class="article-title">{html.escape(title)}</h1>
          <p class="page-intro article-standfirst">{html.escape(post_summary(post))}</p>
        </header>
        <div class="article-body">
          {markdown_to_html(post.body)}
        </div>
        {_pager_html(lang, prev, nxt)}
      </article>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    return shell_html(
        f"{title} | {site['owner']}",
        post_summary(post),
        body,
        2,
        body_class="magazine",
        lang=lang,
        with_math="$" in post.body,
        og_type="article",
        canonical=f"{SITE_URL}/{page_path(lang, 'blog/' + post.meta['slug'] + '/')}",
    )


def render_project_page(
    site: dict,
    home: dict,
    project: ContentEntry,
    page_no: int = 24,
) -> str:
    lang = post_lang(project)
    title = project.meta.get("title", "Untitled")
    body = f"""
  <div class="site-shell page-shell">
    {site_header('projects', 2, magazine=True, lang=lang)}
    <main>
      <article class="article-shell" data-reveal>
        <header class="article-head">
          <div class="article-topbar">
            <a class="article-back" href="../">&larr; {html.escape(t(lang, 'projects'))}</a>
          </div>
          <div class="meta-row"><span class="meta-pill">{html.escape(project.meta.get('status', t(lang, 'draft_project')))}</span></div>
          <h1 class="article-title">{html.escape(title)}</h1>
          <p class="page-intro article-standfirst">{html.escape(project_summary(project))}</p>
        </header>
        <div class="article-body">
          {markdown_to_html(project.body)}
        </div>
      </article>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    return shell_html(
        f"{title} | {site['owner']}",
        project_summary(project),
        body,
        2,
        body_class="magazine",
        lang=lang,
        with_math="$" in project.body,
        og_type="article",
        canonical=f"{SITE_URL}/{page_path(lang, 'projects/' + project.meta['slug'] + '/')}",
    )


def render_404(site: dict, home: dict, lang: str = LANG_DEFAULT) -> str:
    body = f"""
  <div class="site-shell page-shell">
    {site_header('', 0, magazine=True, lang=lang)}
    <main class="error-main">
      <div class="error-shell">
        <p class="eyebrow">404</p>
        <h1 class="page-title">{html.escape(t(lang, 'not_found_heading'))}</h1>
        <p class="page-intro">{html.escape(t(lang, 'not_found_copy'))}</p>
        <div class="button-row">
          <a class="button button-primary" href="./">{html.escape(t(lang, 'go_home'))}</a>
        </div>
      </div>
    </main>
    {site_footer(site, home, magazine=True, lang=lang)}
  </div>
"""
    return shell_html(
        t(lang, "not_found_title"),
        t(lang, "not_found_description"),
        body,
        0,
        body_class="magazine",
        lang=lang,
        noindex=True,
    )
