from __future__ import annotations

import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"

UI = {
    "home": "Home",
    "about": "About",
    "projects": "Projects",
    "blog": "Blog",
    "contact": "Contact",
    "primary_nav": "Primary",
    "email": "Email",
    "home_description": "A personal student homepage and blog.",
    "blog_description": "Essays, project notes, reading logs, and short reflections.",
    "projects_description": "Selected and upcoming projects from Tyler.",
    "not_found_title": "Page Not Found",
    "not_found_description": "This page could not be found.",
    "not_found_heading": "This page drifted out of orbit.",
    "not_found_copy": "The link may be outdated, or the page may have moved while the site was being reorganized.",
    "go_home": "Go Home",
    "read_article": "Read article",
    "back_to_blog": "Back to blog",
    "read_project": "View project",
    "placeholder_post_title": "Your first project breakdown",
    "placeholder_post_summary": "The next post can be a small project breakdown.",
    "placeholder_post_kicker": "Placeholder",
    "placeholder_post_meta": "Future post",
    "placeholder_post_link": "Add this next",
    "start_here": "Start Here",
    "draft_project": "Coming soon",
    "project_label": "Project",
    "writing_intro": "Essays, project notes, reading logs, and short reflections. Clear writing matters more than volume.",
    "projects_intro": "A separate page for work I want to present with more room, context, and screenshots.",
}


@dataclass
class ContentEntry:
    meta: Dict[str, str]
    body: str
    source_path: Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text.strip()
    _, front_matter, body = parts
    meta: Dict[str, str] = {}
    for line in front_matter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body.strip()


def infer_slug(path: Path) -> str:
    return path.stem


def load_entries(folder: Path) -> List[ContentEntry]:
    entries: List[ContentEntry] = []
    for path in sorted(folder.glob("*.md")):
        if path.name.startswith("_template"):
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("slug", infer_slug(path))
        entries.append(ContentEntry(meta=meta, body=body, source_path=path))
    return entries


def format_inline(text: str) -> str:
    """Convert inline Markdown to HTML. Call on already-escaped text.
    Order matters: images before links, bold before italic."""
    # Images: ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+(?:\s+"[^"]*")?)\)',
                  r'<img src="\2" alt="\1" class="post-image" loading="lazy">', text)
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" class="post-link">\1</a>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def strip_markdown(text: str) -> str:
    """Strip inline Markdown syntax — used only for plain-text contexts (summary, reading time, etc.)."""
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def first_paragraph(markdown: str) -> str:
    blocks = [block.strip() for block in markdown.split("\n\n") if block.strip()]
    for block in blocks:
        if block.startswith("#") or block.startswith("- ") or block.startswith("```"):
            continue
        return strip_markdown(" ".join(line.strip() for line in block.splitlines()))
    return ""


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    chunks: List[str] = []
    paragraph_buffer: List[str] = []
    in_list = False
    in_code = False
    code_lines: List[str] = []

    def close_paragraph() -> None:
        nonlocal paragraph_buffer
        if paragraph_buffer:
            text = " ".join(part.strip() for part in paragraph_buffer if part.strip())
            escaped = html.escape(text)
            chunks.append(f"<p>{format_inline(escaped)}</p>")
            paragraph_buffer = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            chunks.append("</ul>")
            in_list = False

    def close_code() -> None:
        nonlocal in_code, code_lines
        if in_code:
            code = "\n".join(code_lines)
            chunks.append(f"<pre><code>{html.escape(code)}</code></pre>")
            code_lines = []
            in_code = False

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                close_code()
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(raw_line)
            continue
        if not line.strip():
            close_paragraph()
            close_list()
            continue
        if line.startswith("## "):
            close_paragraph()
            close_list()
            chunks.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("# "):
            close_paragraph()
            close_list()
            chunks.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
            continue
        if line.startswith("- "):
            close_paragraph()
            if not in_list:
                chunks.append("<ul>")
                in_list = True
            escaped = html.escape(line[2:].strip())
            chunks.append(f"<li>{format_inline(escaped)}</li>")
            continue
        paragraph_buffer.append(line)

    close_paragraph()
    close_list()
    close_code()
    return "\n    ".join(chunks)


def ensure_public_dir() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    shutil.copytree(SRC / "assets", PUBLIC / "assets", dirs_exist_ok=True)


def rel_prefix(depth: int) -> str:
    return "../" * depth


def site_header(current: str, depth: int) -> str:
    prefix = rel_prefix(depth)
    home_href = prefix or "./"
    nav = [
        ("home", home_href),
        ("about", f"{prefix}about/"),
        ("projects", f"{prefix}projects/"),
        ("blog", f"{prefix}blog/"),
    ]
    nav_items: List[str] = []
    for key, href in nav:
        current_attr = ' class="current"' if key == current else ""
        nav_items.append(f'<a{current_attr} href="{href}">{html.escape(UI[key])}</a>')
    nav_html = "\n        ".join(nav_items)
    return f"""
    <header class="site-header">
      <a class="brand" href="{home_href}">
        <span class="brand-wordmark">Tyler&apos;s Corner</span>
      </a>
      <nav class="site-nav" aria-label="{html.escape(UI['primary_nav'])}">
        {nav_html}
      </nav>
    </header>"""


def site_footer(site: dict, home: dict) -> str:
    return f"""
    <footer class="site-footer" id="contact">
      <div class="footer-row footer-row-centered"><span class="footer-title">{html.escape(home['footer']['closing'])}</span></div>
      <div class="footer-row footer-row-centered"><span>&copy; <span data-year></span> {html.escape(site['owner'])}</span></div>
    </footer>"""


def shell_html(title: str, description: str, body: str, depth: int) -> str:
    prefix = rel_prefix(depth)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="icon" href="{prefix}assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="{prefix}assets/fonts/Megrim-Regular.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  <link rel="stylesheet" href="{prefix}assets/vendor/katex/katex.min.css">
  <script defer src="{prefix}assets/vendor/katex/katex.min.js"></script>
  <script defer src="{prefix}assets/vendor/katex/auto-render.min.js"></script>
  <script defer src="{prefix}assets/site.js"></script>
</head>
<body>
{body}
</body>
</html>
"""


def reading_time(body: str) -> str:
    word_count = max(1, len(strip_markdown(body).split()))
    minutes = max(1, round(word_count / 180))
    return f"{minutes} min read"


def post_summary(entry: ContentEntry) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A short note about learning in public."
    )


def project_summary(entry: ContentEntry) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A placeholder project that will be expanded later."
    )


def render_post_cards(posts: Iterable[ContentEntry], href_prefix: str) -> str:
    cards: List[str] = []
    for entry in posts:
        slug = entry.meta["slug"]
        cards.append(
            f"""
          <article class="post-card">
            <div class="card-top"><div class="card-kicker">{html.escape(entry.meta.get('date', UI['start_here']))}</div><span class="meta-pill">{html.escape(reading_time(entry.body))}</span></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(post_summary(entry))}</p>
            <a class="card-link" href="{href_prefix}{html.escape(slug)}/">{html.escape(UI['read_article'])}</a>
          </article>"""
        )
    return "".join(cards)


def render_placeholder_post() -> str:
    return f"""
          <article class="post-card">
            <div class="card-top"><div class="card-kicker">{html.escape(UI['placeholder_post_kicker'])}</div><span class="meta-pill">{html.escape(UI['placeholder_post_meta'])}</span></div>
            <h3>{html.escape(UI['placeholder_post_title'])}</h3>
            <p>{html.escape(UI['placeholder_post_summary'])}</p>
            <a class="card-link" href="./blog/">{html.escape(UI['placeholder_post_link'])}</a>
          </article>"""


def render_home(site: dict, home: dict, posts: List[ContentEntry]) -> str:
    title_text = " ".join(home["hero"]["title_lines"])
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
  <div class="site-shell">
    {site_header('home', 0)}
    <main>
      <section class="hero" data-reveal>
        <header class="hero-header">
          <h1 class="hero-title">{html.escape(title_text)}</h1>
          <p class="hero-subline">{html.escape(home['hero']['subtitle'])}</p>
        </header>
        <div class="hero-body">
          <div class="hero-about">
            <p>{html.escape(home['hero']['portrait_note'])}</p>
            <p>{html.escape(home['about']['card_body'])}</p>
          </div>
          <div class="hero-portrait">
            <div class="portrait"></div>
          </div>
        </div>
      </section>
    </main>
  </div>
"""
    title = site['title']
    return shell_html(title, UI["home_description"], body, 0)


def render_about(site: dict, home: dict) -> str:
    body = f"""
  <div class="site-shell page-shell">
    {site_header('about', 1)}
    <main>
      <section class="section" style="padding-top: 52px;">
        <div class="about-prose">
          <p>{html.escape(home['hero']['portrait_note'])}</p>
          <p>{html.escape(home['about']['card_body'])}</p>
        </div>
      </section>
    </main>
    {site_footer(site, home)}
  </div>
"""
    title = f"{UI['about']} | {site['owner']}"
    return shell_html(title, UI["about"], body, 1)


def render_blog_index(site: dict, home: dict, posts: List[ContentEntry]) -> str:
    body = f"""
  <div class="site-shell page-shell">
    {site_header('blog', 1)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="page-intro">{html.escape(UI['writing_intro'])}</p>
      </section>
      <section class="section" data-reveal>
        <div class="card-stack">
          {render_post_cards(posts, "./")}
        </div>
      </section>
    </main>
    {site_footer(site, home)}
  </div>
"""
    title = f"{UI['blog']} | {site['owner']}"
    return shell_html(title, UI["blog_description"], body, 1)


def render_projects_index(site: dict, home: dict, projects: List[ContentEntry]) -> str:
    cards = []
    for idx, entry in enumerate(projects, start=1):
        status = entry.meta.get("status", "draft")
        badge = UI["draft_project"] if status == "draft" else status
        cards.append(
            f"""
          <article class="project-card">
            <div class="card-top"><div class="card-kicker">{html.escape(UI['project_label'])} {idx:02d}</div><span class="meta-pill">{html.escape(badge)}</span></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(project_summary(entry))}</p>
            <a class="card-link" href="./{html.escape(entry.meta['slug'])}/">{html.escape(UI['read_project'])}</a>
          </article>"""
        )
    body = f"""
  <div class="site-shell page-shell">
    {site_header('projects', 1)}
    <main>
      <section class="section page-hero" data-reveal>
        <p class="page-intro">{html.escape(UI['projects_intro'])}</p>
      </section>
      <section class="section" data-reveal>
        <div class="card-stack">
          {''.join(cards)}
        </div>
      </section>
    </main>
    {site_footer(site, home)}
  </div>
"""
    title = f"{UI['projects']} | {site['owner']}"
    return shell_html(title, UI["projects_description"], body, 1)


def render_post_page(site: dict, post: ContentEntry) -> str:
    title = post.meta.get("title", "Untitled")
    tags_raw = post.meta.get("tags", "")
    tags_html = ""
    if tags_raw:
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        tags_html = "".join(f'<span class="tag-pill">{html.escape(t)}</span>' for t in tags)
    body = f"""
  <article class="article-shell" data-reveal>
    <header>
      <div class="article-topbar">
        <a class="article-back" href="../">&larr; {html.escape(UI['back_to_blog'])}</a>
      </div>
      <div class="meta-row"><span class="meta-pill">{html.escape(post.meta.get('date', ''))}</span>{tags_html}</div>
      <h1>{html.escape(title)}</h1>
      <p class="page-intro">{html.escape(post_summary(post))}</p>
    </header>
    {markdown_to_html(post.body)}
  </article>
"""
    return shell_html(f"{title} | {site['owner']}", post_summary(post), body, 2)


def render_project_page(site: dict, project: ContentEntry) -> str:
    title = project.meta.get("title", "Untitled")
    body = f"""
  <article class="article-shell" data-reveal>
    <header>
      <div class="article-topbar">
        <a class="article-back" href="../">&larr; {html.escape(UI['projects'])}</a>
      </div>
      <div class="meta-row"><span class="meta-pill">{html.escape(project.meta.get('status', UI['draft_project']))}</span></div>
      <h1>{html.escape(title)}</h1>
      <p class="page-intro">{html.escape(project_summary(project))}</p>
    </header>
    {markdown_to_html(project.body)}
  </article>
"""
    return shell_html(f"{title} | {site['owner']}", project_summary(project), body, 2)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> None:
    ensure_public_dir()
    copy_assets()

    site = load_json(SRC / "data" / "site.json")
    home = load_json(SRC / "data" / "home.json")
    posts = load_entries(CONTENT / "posts")
    projects = load_entries(CONTENT / "projects")

    # Root homepage — no redirect needed
    write(PUBLIC / "index.html", render_home(site, home, posts))

    # 404 page
    write(
        PUBLIC / "404.html",
        shell_html(
            UI["not_found_title"],
            UI["not_found_description"],
            f"""
  <main class="error-shell">
    <p class="eyebrow">404</p>
    <h1 class="page-title">{html.escape(UI['not_found_heading'])}</h1>
    <p class="page-intro">{html.escape(UI['not_found_copy'])}</p>
    <div class="button-row">
      <a class="button button-primary" href="./">{html.escape(UI['go_home'])}</a>
    </div>
  </main>
""",
            0,
        ),
    )

    # Subpages at root level
    write(PUBLIC / "about" / "index.html", render_about(site, home))
    write(PUBLIC / "blog" / "index.html", render_blog_index(site, home, posts))
    write(PUBLIC / "projects" / "index.html", render_projects_index(site, home, projects))

    for entry in posts:
        write(PUBLIC / "blog" / entry.meta["slug"] / "index.html", render_post_page(site, entry))

    for entry in projects:
        write(PUBLIC / "projects" / entry.meta["slug"] / "index.html", render_project_page(site, entry))


if __name__ == "__main__":
    build()
