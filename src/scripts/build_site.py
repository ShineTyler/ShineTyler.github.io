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

LANG_PATHS = {"en": "en", "zh-CN": "zh"}

UI = {
    "en": {
        "home": "Home",
        "about": "About",
        "projects": "Projects",
        "blog": "Blog",
        "contact": "Contact",
        "primary_nav": "Primary",
        "language_switcher": "Language switcher",
        "email": "Email",
        "home_title_suffix": "Student Homepage & Blog",
        "home_description": "A bilingual student homepage and blog built for GitHub Pages.",
        "blog_description": "English posts from a bilingual student homepage and blog.",
        "projects_description": "Selected and upcoming projects from Tyler.",
        "not_found_title": "Page Not Found",
        "not_found_description": "This page could not be found.",
        "not_found_heading": "This page drifted out of orbit.",
        "not_found_copy": "The link may be outdated, or the page may have moved while the site was being reorganized.",
        "go_home_en": "Go to English Home",
        "go_home_zh": "Go to Chinese Home",
        "read_article": "Read article",
        "back_to_blog": "Back to blog",
        "read_in_other_language": "Read this in Chinese",
        "read_project": "View project",
        "placeholder_post_title": "Your first project breakdown",
        "placeholder_post_summary": "The next post can be a small project breakdown.",
        "placeholder_post_kicker": "Placeholder",
        "placeholder_post_meta": "Future post",
        "placeholder_post_link": "Add this next",
        "start_here": "Start Here",
        "draft_project": "Coming soon",
        "project_label": "Project",
        "article_language": "English",
        "writing_intro": "Essays, project notes, reading logs, and short reflections. Clear writing matters more than volume.",
        "projects_intro": "A separate page for work I want to present with more room, context, and screenshots.",
    },
    "zh-CN": {
        "home": "首页",
        "about": "关于",
        "projects": "项目",
        "blog": "博客",
        "contact": "联系",
        "primary_nav": "主要导航",
        "language_switcher": "语言切换",
        "email": "邮箱",
        "home_title_suffix": "学生主页与博客",
        "home_description": "一个适合学生的中英文个人主页与博客。",
        "blog_description": "中英文学生活页中的中文博客页面。",
        "projects_description": "Tyler 的项目展示页。",
        "not_found_title": "页面未找到",
        "not_found_description": "这个页面暂时不存在。",
        "not_found_heading": "这个页面暂时飞走了。",
        "not_found_copy": "链接可能已经失效，或者页面在整理网站结构时被移动了位置。",
        "go_home_en": "前往英文首页",
        "go_home_zh": "前往中文首页",
        "read_article": "阅读全文",
        "back_to_blog": "返回博客",
        "read_in_other_language": "阅读英文版",
        "read_project": "查看项目",
        "placeholder_post_title": "写下你的第一篇项目复盘",
        "placeholder_post_summary": "下一篇可以先从一个小项目的复盘开始。",
        "placeholder_post_kicker": "预留位",
        "placeholder_post_meta": "下一篇",
        "placeholder_post_link": "把这里换成你的新文章",
        "start_here": "从这里开始",
        "draft_project": "暂未公开",
        "project_label": "项目",
        "article_language": "中文",
        "writing_intro": "文章、项目复盘、读书笔记和阶段反思。学生博客最重要的是清晰和持续。",
        "projects_intro": "把作品单独放在这里，会比堆在首页里更舒服，也更方便以后慢慢补充细节。",
    },
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
    return path.stem.replace(".zh-CN", "")


def load_entries(folder: Path) -> List[ContentEntry]:
    entries: List[ContentEntry] = []
    for path in sorted(folder.glob("*.md")):
        if path.name.startswith("_template"):
            continue
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        meta.setdefault("slug", infer_slug(path))
        entries.append(ContentEntry(meta=meta, body=body, source_path=path))
    return entries


def strip_markdown(text: str) -> str:
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
            chunks.append(f"<p>{html.escape(text)}</p>")
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
            chunks.append(f"<li>{html.escape(strip_markdown(line[2:].strip()))}</li>")
            continue
        paragraph_buffer.append(strip_markdown(line))

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


def lang_dir(lang: str) -> str:
    return LANG_PATHS[lang]


def html_lang(lang: str) -> str:
    return "zh-CN" if lang == "zh-CN" else "en"


def ui(lang: str, key: str) -> str:
    return UI[lang][key]


def other_lang(lang: str) -> str:
    return "zh-CN" if lang == "en" else "en"


def base_path(lang: str, depth: int) -> str:
    return f"{rel_prefix(depth)}{lang_dir(lang)}/"


def language_switch(lang: str, depth: int, section: str | None = None, slug: str | None = None) -> str:
    links = []
    for candidate in ("en", "zh-CN"):
        href = base_path(candidate, depth)
        if section == "blog":
            href += "blog/"
            if slug:
                href += f"{slug}/"
        elif section == "projects":
            href += "projects/"
            if slug:
                href += f"{slug}/"
        current_attr = ' class="current"' if candidate == lang else ""
        text = "EN" if candidate == "en" else "中文"
        links.append(f'<a{current_attr} href="{href}">{text}</a>')
    return "".join(links)


def site_header(lang: str, current: str, depth: int) -> str:
    current_base = base_path(lang, depth)
    nav = [
        ("home", current_base),
        ("about", f"{current_base}#about"),
        ("projects", f"{current_base}projects/"),
        ("blog", f"{current_base}blog/"),
        ("contact", f"{current_base}#contact"),
    ]
    nav_items: List[str] = []
    for key, href in nav:
        current_attr = ' class="current"' if key == current else ""
        nav_items.append(f'<a{current_attr} href="{href}">{html.escape(ui(lang, key))}</a>')
    nav_html = "\n        ".join(nav_items)
    return f"""
    <header class="site-header">
      <a class="brand" href="{current_base}">
        <span class="brand-wordmark">Tyler&apos;s Corner</span>
      </a>
      <nav class="site-nav" aria-label="{html.escape(ui(lang, 'primary_nav'))}">
        {nav_html}
      </nav>
      <div class="language-switch" aria-label="{html.escape(ui(lang, 'language_switcher'))}">
        {language_switch(lang, depth)}
      </div>
    </header>"""


def site_footer(lang: str, site: dict, home: dict) -> str:
    return f"""
    <footer class="site-footer" id="contact">
      <div class="footer-row footer-row-centered"><span class="footer-title">{html.escape(home['footer']['closing'][lang])}</span></div>
      <div class="footer-row footer-row-centered"><span>&copy; <span data-year></span> {html.escape(site['owner'])}</span></div>
    </footer>"""


def shell_html(lang: str, title: str, description: str, body: str, depth: int) -> str:
    prefix = rel_prefix(depth)
    return f"""<!DOCTYPE html>
<html lang="{html_lang(lang)}">
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


def reading_time(body: str, lang: str) -> str:
    word_count = max(1, len(strip_markdown(body).split()))
    minutes = max(1, round(word_count / 180))
    if lang == "zh-CN":
        return f"{minutes} 分钟阅读"
    return f"{minutes} min read"


def post_summary(entry: ContentEntry, lang: str) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A short note about learning in public."
        if lang == "en"
        else "一篇关于公开记录学习过程的短文。"
    )


def project_summary(entry: ContentEntry, lang: str) -> str:
    return entry.meta.get("summary") or first_paragraph(entry.body) or (
        "A placeholder project that will be expanded later."
        if lang == "en"
        else "一个之后会继续展开整理的项目。"
    )


def render_post_cards(posts: Iterable[ContentEntry], lang: str, href_prefix: str) -> str:
    cards: List[str] = []
    for entry in posts:
        slug = entry.meta["slug"]
        cards.append(
            f"""
          <article class="post-card">
            <div class="card-top"><div class="card-kicker">{html.escape(entry.meta.get('date', ui(lang, 'start_here')))}</div><span class="meta-pill">{html.escape(reading_time(entry.body, lang))}</span></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(post_summary(entry, lang))}</p>
            <a class="card-link" href="{href_prefix}{html.escape(slug)}/">{html.escape(ui(lang, 'read_article'))}</a>
          </article>"""
        )
    return "".join(cards)


def render_placeholder_post(lang: str) -> str:
    return f"""
          <article class="post-card">
            <div class="card-top"><div class="card-kicker">{html.escape(ui(lang, 'placeholder_post_kicker'))}</div><span class="meta-pill">{html.escape(ui(lang, 'placeholder_post_meta'))}</span></div>
            <h3>{html.escape(ui(lang, 'placeholder_post_title'))}</h3>
            <p>{html.escape(ui(lang, 'placeholder_post_summary'))}</p>
            <a class="card-link" href="./blog/">{html.escape(ui(lang, 'placeholder_post_link'))}</a>
          </article>"""


def render_home(lang: str, site: dict, home: dict, posts: List[ContentEntry]) -> str:
    lang_posts = [entry for entry in posts if entry.meta.get("lang") == lang]
    title_lines = "\n            ".join(
        f'<span class="hero-title-line">{html.escape(line)}</span>'
        for line in home["hero"]["title_lines"][lang]
    )
    cards = render_post_cards(lang_posts[:2], lang, "./blog/")
    if len(lang_posts) < 2:
        cards += render_placeholder_post(lang)
    body = f"""
  <div class="intro-overlay" role="button" tabindex="0" aria-label="Press start to enter Tyler's blog">
    <div class="intro-overlay-backdrop"></div>
    <div class="intro-overlay-content">
      <h1 class="intro-overlay-title">TYLER</h1>
    </div>
    <p class="intro-overlay-prompt"><span>PRESS</span><span>START</span></p>
    <div class="intro-overlay-arrow" aria-hidden="true">
      <span></span>
      <span></span>
    </div>
  </div>
  <div class="site-shell">
    {site_header(lang, 'home', 1)}
    <main>
      <section class="hero" data-reveal>
        <div class="hero-copy">
          <h1 class="hero-title">
            {title_lines}
          </h1>
          <p class="hero-subline">{html.escape(home['hero']['subtitle'][lang])}</p>
        </div>
        <div class="hero-visual">
          <div class="portrait"></div>
          <div class="hero-visual-meta">
            <a href="mailto:{html.escape(site['email'])}">{html.escape(ui(lang, 'email'))}</a>
            <a href="{html.escape(site['github'])}" target="_blank" rel="noreferrer">GitHub</a>
          </div>
        </div>
      </section>

      <section class="section" id="about" data-reveal>
        <div class="section-head">
          <div>
            <h2 class="section-title">{html.escape(home['about']['section_title'][lang])}</h2>
          </div>
        </div>
        <div class="single-column">
          <article class="info-card">
            <p>{html.escape(home['hero']['portrait_note'][lang])}</p>
            <p>{html.escape(home['about']['card_body'][lang])}</p>
          </article>
        </div>
      </section>

      <section class="section" data-reveal>
        <div class="section-head">
          <div>
            <h2 class="section-title">{html.escape(home['recent_writing']['section_title'][lang])}</h2>
          </div>
        </div>
        <div class="grid-two">
          {cards}
        </div>
      </section>
    </main>
    {site_footer(lang, site, home)}
  </div>
"""
    title = site['title']
    return shell_html(lang, title, ui(lang, "home_description"), body, 1)


def render_blog_index(lang: str, site: dict, home: dict, posts: List[ContentEntry]) -> str:
    lang_posts = [entry for entry in posts if entry.meta.get("lang") == lang]
    body = f"""
  <div class="site-shell page-shell">
    {site_header(lang, 'blog', 2)}
    <main>
      <section class="section page-hero" data-reveal>
        <h1 class="page-title">{html.escape(ui(lang, 'blog'))}</h1>
        <p class="page-intro">{html.escape(ui(lang, 'writing_intro'))}</p>
      </section>
      <section class="section" data-reveal>
        <div class="grid-two">
          {render_post_cards(lang_posts, lang, "./")}
        </div>
      </section>
    </main>
    {site_footer(lang, site, home)}
  </div>
"""
    title = f"{ui(lang, 'blog')} | {site['owner']}"
    return shell_html(lang, title, ui(lang, "blog_description"), body, 2)


def render_projects_index(lang: str, site: dict, home: dict, projects: List[ContentEntry]) -> str:
    lang_projects = [entry for entry in projects if entry.meta.get("lang") == lang]
    cards = []
    for idx, entry in enumerate(lang_projects, start=1):
        status = entry.meta.get("status", "draft")
        badge = ui(lang, "draft_project") if status == "draft" else status
        cards.append(
            f"""
          <article class="project-card">
            <div class="card-top"><div class="card-kicker">{html.escape(ui(lang, 'project_label'))} {idx:02d}</div><span class="meta-pill">{html.escape(badge)}</span></div>
            <h3>{html.escape(entry.meta.get('title', 'Untitled'))}</h3>
            <p>{html.escape(project_summary(entry, lang))}</p>
            <a class="card-link" href="./{html.escape(entry.meta['slug'])}/">{html.escape(ui(lang, 'read_project'))}</a>
          </article>"""
        )
    body = f"""
  <div class="site-shell page-shell">
    {site_header(lang, 'projects', 2)}
    <main>
      <section class="section page-hero" data-reveal>
        <h1 class="page-title">{html.escape(ui(lang, 'projects'))}</h1>
        <p class="page-intro">{html.escape(ui(lang, 'projects_intro'))}</p>
      </section>
      <section class="section" data-reveal>
        <div class="grid-three">
          {''.join(cards)}
        </div>
      </section>
    </main>
    {site_footer(lang, site, home)}
  </div>
"""
    title = f"{ui(lang, 'projects')} | {site['owner']}"
    return shell_html(lang, title, ui(lang, "projects_description"), body, 2)


def render_post_page(lang: str, site: dict, post: ContentEntry, siblings: List[ContentEntry]) -> str:
    title = post.meta.get("title", "Untitled")
    slug = post.meta["slug"]
    alt = next((entry for entry in siblings if entry.meta.get("slug") == slug and entry.meta.get("lang") == other_lang(lang)), None)
    alt_link = ""
    if alt:
        target = "../../../" + lang_dir(other_lang(lang)) + f"/blog/{slug}/"
        alt_link = f'<p><a class="card-link" href="{target}">{html.escape(ui(lang, "read_in_other_language"))}</a></p>'
    body = f"""
  <article class="article-shell" data-reveal>
    <header>
      <p class="eyebrow">{html.escape(ui(lang, 'start_here'))}</p>
      <div class="meta-row"><span class="meta-pill">{html.escape(ui(lang, 'article_language'))}</span><span class="meta-pill">{html.escape(reading_time(post.body, lang))}</span><span class="meta-pill">{html.escape(post.meta.get('date', ''))}</span></div>
      <h1>{html.escape(title)}</h1>
      <p class="page-intro">{html.escape(post_summary(post, lang))}</p>
      {alt_link}
    </header>
    {markdown_to_html(post.body)}
    <a class="article-back" href="../">&larr; {html.escape(ui(lang, 'back_to_blog'))}</a>
  </article>
"""
    return shell_html(lang, f"{title} | {site['owner']}", post_summary(post, lang), body, 3)


def render_project_page(lang: str, site: dict, project: ContentEntry, siblings: List[ContentEntry]) -> str:
    title = project.meta.get("title", "Untitled")
    slug = project.meta["slug"]
    alt = next((entry for entry in siblings if entry.meta.get("slug") == slug and entry.meta.get("lang") == other_lang(lang)), None)
    alt_link = ""
    if alt:
        target = "../../../" + lang_dir(other_lang(lang)) + f"/projects/{slug}/"
        alt_link = f'<p><a class="card-link" href="{target}">{html.escape(ui(lang, "read_in_other_language"))}</a></p>'
    body = f"""
  <article class="article-shell" data-reveal>
    <header>
      <p class="eyebrow">{html.escape(ui(lang, 'projects'))}</p>
      <div class="meta-row"><span class="meta-pill">{html.escape(project.meta.get('status', ui(lang, 'draft_project')))}</span></div>
      <h1>{html.escape(title)}</h1>
      <p class="page-intro">{html.escape(project_summary(project, lang))}</p>
      {alt_link}
    </header>
    {markdown_to_html(project.body)}
    <a class="article-back" href="../">&larr; {html.escape(ui(lang, 'projects'))}</a>
  </article>
"""
    return shell_html(lang, f"{title} | {site['owner']}", project_summary(project, lang), body, 3)


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

    write(
        PUBLIC / "index.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Loading...</title>
  <meta name="description" content="A bilingual student homepage and blog starter for GitHub Pages.">
  <script>(function(){var lang=(navigator.language||'en').toLowerCase();var target=lang.indexOf('zh')===0?'./zh/':'./en/';window.location.replace(target);}());</script>
</head>
<body></body>
</html>
""",
    )

    write(
        PUBLIC / "404.html",
        shell_html(
            "en",
            ui("en", "not_found_title"),
            ui("en", "not_found_description"),
            f"""
  <main class="error-shell">
    <p class="eyebrow">404</p>
    <h1 class="page-title">{html.escape(ui('en', 'not_found_heading'))}</h1>
    <p class="page-intro">{html.escape(ui('en', 'not_found_copy'))}</p>
    <div class="button-row">
      <a class="button button-primary" href="./en/">{html.escape(ui('en', 'go_home_en'))}</a>
      <a class="button button-secondary" href="./zh/">{html.escape(ui('zh-CN', 'go_home_zh'))}</a>
    </div>
  </main>
""",
            0,
        ),
    )

    for lang in ("en", "zh-CN"):
        base = PUBLIC / lang_dir(lang)
        write(base / "index.html", render_home(lang, site, home, posts))
        write(base / "blog" / "index.html", render_blog_index(lang, site, home, posts))
        write(base / "projects" / "index.html", render_projects_index(lang, site, home, projects))

        for entry in posts:
            if entry.meta.get("lang") == lang:
                write(base / "blog" / entry.meta["slug"] / "index.html", render_post_page(lang, site, entry, posts))

        for entry in projects:
            if entry.meta.get("lang") == lang:
                write(base / "projects" / entry.meta["slug"] / "index.html", render_project_page(lang, site, entry, projects))


if __name__ == "__main__":
    build()
