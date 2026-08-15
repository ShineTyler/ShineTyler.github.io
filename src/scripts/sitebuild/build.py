"""Build orchestration: wipe public/, copy assets, load data, write pages.

The site ships in English only; the bilingual scaffolding (UI dicts in
config.py, per-language helpers) stays in place should a second language
edition ever be wanted again.
"""
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from .config import CONTENT, LANG_DEFAULT, PUBLIC, SRC, SITE_URL
from .data import load_entries, load_json
from .feeds import render_feed, render_robots, render_sitemap
from .render import (
    render_404,
    render_about,
    render_blog_index,
    render_collection_page,
    render_home,
    render_post_page,
    render_project_page,
    render_projects_index,
)


def ensure_public_dir() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True, exist_ok=True)


def copy_assets() -> None:
    shutil.copytree(SRC / "assets", PUBLIC / "assets", dirs_exist_ok=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _collection_pages(entries):
    """Group entries by category and by tag."""
    categories: dict = defaultdict(list)
    tags: dict = defaultdict(list)
    for entry in entries:
        category = entry.meta.get("category", "").strip()
        if category:
            categories[category].append(entry)
        for tag in [x.strip() for x in entry.meta.get("tags", "").split(",") if x.strip()]:
            tags[tag].append(entry)
    return categories, tags


def build() -> None:
    ensure_public_dir()
    copy_assets()

    site = load_json(SRC / "data" / "site.json")
    home = load_json(SRC / "data" / "home.json")
    posts = load_entries(CONTENT / "posts")
    projects = load_entries(CONTENT / "projects")
    lang = LANG_DEFAULT

    pages: list = []

    write(PUBLIC / "index.html", render_home(site, home, posts, lang=lang))
    pages.append("")
    write(PUBLIC / "about" / "index.html", render_about(site, home, lang=lang))
    pages.append("about/")
    write(PUBLIC / "blog" / "index.html", render_blog_index(site, home, posts, lang=lang))
    pages.append("blog/")
    write(PUBLIC / "projects" / "index.html", render_projects_index(site, home, projects, lang=lang))
    pages.append("projects/")

    # Category and tag collections
    categories, tags = _collection_pages(posts)
    for name, entries in categories.items():
        path = PUBLIC / "blog" / "categories" / quote(name) / "index.html"
        write(path, render_collection_page(site, home, lang, "category", name, entries))
        pages.append("blog/categories/" + quote(name) + "/")
    for name, entries in tags.items():
        path = PUBLIC / "blog" / "tags" / quote(name) / "index.html"
        write(path, render_collection_page(site, home, lang, "tag", name, entries))
        pages.append("blog/tags/" + quote(name) + "/")

    # Posts with prev/next pager
    for idx, entry in enumerate(posts):
        prev = posts[idx - 1] if idx > 0 else None
        nxt = posts[idx + 1] if idx + 1 < len(posts) else None
        write(
            PUBLIC / "blog" / entry.meta["slug"] / "index.html",
            render_post_page(site, home, entry, page_no=12 + idx, prev=prev, nxt=nxt),
        )
        pages.append("blog/" + entry.meta["slug"] + "/")

    # Projects
    for idx, entry in enumerate(projects):
        write(
            PUBLIC / "projects" / entry.meta["slug"] / "index.html",
            render_project_page(site, home, entry, page_no=24 + idx),
        )
        pages.append("projects/" + entry.meta["slug"] + "/")

    # Root 404 page (GitHub Pages serves it for every missing path) — not in sitemap
    write(PUBLIC / "404.html", render_404(site, home))

    # SEO and syndication
    write(PUBLIC / "sitemap.xml", render_sitemap(pages))
    write(PUBLIC / "robots.txt", render_robots())
    write(PUBLIC / "feed.xml", render_feed(site, posts))


def main() -> None:
    build()


if __name__ == "__main__":
    main()
