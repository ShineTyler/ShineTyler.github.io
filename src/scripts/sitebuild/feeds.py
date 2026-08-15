"""SEO and syndication output: sitemap.xml, robots.txt, RSS feed."""
import html
from datetime import datetime
from typing import List

from .config import LANG_DEFAULT, SITE_NAME, SITE_URL
from .data import ContentEntry
from .render import post_summary


def render_sitemap(pages: List[str]) -> str:
    entries = "".join(f"  <url><loc>{SITE_URL}/{page}</loc></url>\n" for page in sorted(set(pages)))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}"
        "</urlset>\n"
    )


def render_robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


def _rfc822_date(date_str: str) -> str:
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except (ValueError, AttributeError):
        return ""
    return parsed.strftime("%a, %d %b %Y 00:00:00 +0000")


def render_feed(site: dict, posts: List[ContentEntry], lang: str = LANG_DEFAULT) -> str:
    items = []
    for entry in posts:
        slug = entry.meta["slug"]
        url = f"{SITE_URL}/blog/{slug}/"
        title = entry.meta.get("title", "Untitled")
        description = post_summary(entry)
        pub_date = _rfc822_date(entry.meta.get("date", ""))
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(title)}</title>\n"
            f"      <link>{url}</link>\n"
            f'      <guid isPermaLink="true">{url}</guid>\n'
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"      <description>{html.escape(description)}</description>\n"
            "    </item>"
        )
    items_xml = "\n".join(items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{html.escape(site['title'])}</title>\n"
        f"    <link>{SITE_URL}/</link>\n"
        f"    <description>{html.escape(site.get('tagline', ''))}</description>\n"
        f"    <language>{lang}</language>\n"
        f"{items_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )
