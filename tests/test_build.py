"""Stdlib-only unit tests for the sitebuild package.

Run with: python -m unittest discover -s tests
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src" / "scripts"))

from sitebuild.config import CONTENT, ROOT, SRC, page_path, t  # noqa: E402
from sitebuild.data import ContentEntry, load_entries, load_json, parse_front_matter  # noqa: E402
from sitebuild.markdown import (  # noqa: E402
    first_paragraph,
    markdown_to_html,
    protect_math,
    reading_time,
    restore_math,
    strip_markdown,
)
from sitebuild.render import (  # noqa: E402
    post_lang,
    render_blog_index,
    render_collection_page,
    render_home,
    render_post_page,
    shell_html,
    site_footer,
    site_header,
)

SAMPLE_MD = """---
title: Test Post
slug: test-post
---

## Heading two

A paragraph with **bold**, *italic* and `code`, plus [a link](https://example.com).

### Heading three

- item one
- item two

| col a | col b |
|-------|-------|
| 1     | 2     |

```python
print("hi")
```

> A quoted thought.

![an image](img.png)

Math: $x^2$ and $$y = mx + b$$
"""


class FrontMatterTests(unittest.TestCase):
    def test_parse_with_frontmatter(self):
        meta, body = parse_front_matter(SAMPLE_MD)
        self.assertEqual(meta["title"], "Test Post")
        self.assertEqual(meta["slug"], "test-post")
        self.assertTrue(body.startswith("## Heading two"))

    def test_parse_without_frontmatter(self):
        meta, body = parse_front_matter("just some text")
        self.assertEqual(meta, {})
        self.assertEqual(body, "just some text")

    def test_load_entries_skips_templates(self):
        entries = load_entries(CONTENT / "posts")
        names = [e.source_path.name for e in entries]
        self.assertTrue(all(not n.startswith("_template") for n in names))
        self.assertTrue(all(e.meta.get("slug") for e in entries))


class MathProtectionTests(unittest.TestCase):
    def test_roundtrip(self):
        text = "before $a < b$ middle $$c > d$$ after"
        protected, blocks = protect_math(text)
        self.assertEqual(len(blocks), 2)
        self.assertNotIn("$", protected)
        self.assertEqual(restore_math(protected, blocks), text)

    def test_math_survives_rendering(self):
        html = markdown_to_html("Inline $a < b$ and display $$c > d$$ here.")
        self.assertIn("$a < b$", html)
        self.assertIn("$$c > d$$", html)
        # Angle brackets inside math must NOT be HTML-escaped.
        self.assertNotIn("&lt;", html)


class MarkdownRenderTests(unittest.TestCase):
    def test_headings(self):
        html = markdown_to_html("## A\n\n### B\n\n#### C")
        self.assertIn("<h2>A</h2>", html)
        self.assertIn("<h3>B</h3>", html)
        self.assertIn("<h4>C</h4>", html)

    def test_table(self):
        html = markdown_to_html("| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<table>", html)
        self.assertIn("<th>a</th>", html)
        self.assertIn("<td>1</td>", html)

    def test_fenced_code_is_escaped(self):
        html = markdown_to_html("```python\nprint('<hi>')\n```")
        self.assertIn("<pre><code", html)
        self.assertIn("&lt;hi&gt;", html)
        self.assertNotIn("<hi>", html)

    def test_emphasis_and_code(self):
        html = markdown_to_html("**bold** and *italic* and `code`")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<code>code</code>", html)

    def test_link_gets_post_link_class(self):
        html = markdown_to_html("[x](https://example.com)")
        self.assertIn('class="post-link"', html)

    def test_image_wrapped_in_figure(self):
        html = markdown_to_html("![alt text](img.png)")
        self.assertIn('<span class="post-figure">', html)
        self.assertIn('class="post-image"', html)
        self.assertIn('loading="lazy"', html)

    def test_blockquote(self):
        html = markdown_to_html("> quoted")
        self.assertIn("<blockquote>", html)
        self.assertIn("quoted", html)


class PlainTextHelperTests(unittest.TestCase):
    def test_first_paragraph_skips_headings_and_lists(self):
        text = "# Title\n\n- item\n\nReal first paragraph here."
        self.assertEqual(first_paragraph(text), "Real first paragraph here.")

    def test_strip_markdown(self):
        self.assertEqual(
            strip_markdown("**bold** and [link](https://x.com) and `code`"),
            "bold and link and code",
        )

    def test_reading_time_english(self):
        words = " ".join(["word"] * 540)
        self.assertEqual(reading_time(words, "en"), "3 min read")

    def test_reading_time_chinese(self):
        body = "采样定理给出了回答。" * 200  # 2000 CJK chars
        self.assertIn("分钟", reading_time(body, "zh-CN"))
        self.assertNotEqual(reading_time(body, "zh-CN"), "1 分钟")


class BilingualTests(unittest.TestCase):
    def test_t_falls_back_to_english(self):
        self.assertEqual(t("zh-CN", "issn_print"), "ISSN 2994-0756")
        self.assertEqual(t("klingon", "home"), "Home")

    def test_page_path(self):
        self.assertEqual(page_path("en", "blog/x/"), "blog/x/")
        self.assertEqual(page_path("zh-CN", "blog/x/"), "zh-CN/blog/x/")

    def test_post_lang_defaults_to_en(self):
        entry = ContentEntry(meta={}, body="x", source_path=pathlib.Path("x.md"))
        self.assertEqual(post_lang(entry), "en")


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.site = load_json(SRC / "data" / "site.json")
        self.home = load_json(SRC / "data" / "home.json")
        self.home_zh = load_json(SRC / "data" / "home.zh-CN.json")

    def test_header_has_toc_numbers(self):
        html = site_header("blog", 1, magazine=True)
        self.assertIn("toc-no", html)
        self.assertIn(">04<", html)
        self.assertNotIn("lang-switch", html)

    def test_colophon_is_minimal(self):
        html = site_footer(self.site, self.home, magazine=True)
        self.assertIn("&copy;", html)
        self.assertIn(self.site["email"], html)
        # The quiet-library pass removed the ornamental colophon furniture.
        self.assertNotIn("ISSN", html)
        self.assertNotIn("colophon-label", html)
        self.assertNotIn("colophon-vol", html)

    def test_shell_html_applies_body_class(self):
        html = shell_html("T", "D", "<p>x</p>", 0, body_class="magazine")
        self.assertIn('<body class="magazine">', html)
        self.assertIn('<html lang="en">', html)

    def test_blog_index_structure(self):
        posts = load_entries(CONTENT / "posts")
        html = render_blog_index(self.site, self.home, posts, lang="en")
        self.assertIn("site-header masthead", html)
        self.assertIn("card-no", html)
        self.assertIn("colophon", html)

    def test_blog_index_lists_all_posts(self):
        posts = load_entries(CONTENT / "posts")
        html = render_blog_index(self.site, self.home, posts, lang="en")
        # The site is English-only now, but the Chinese article stays in the
        # blog as content — the index lists every post.
        self.assertIn("signal-sampling-reconstruction", html)
        self.assertIn("start-here", html)

    def test_home_shows_recent_posts_instead_of_nav_ledger(self):
        posts = load_entries(CONTENT / "posts")
        html = render_home(self.site, self.home, posts, lang="en")
        self.assertIn("contents-ledger", html)
        self.assertIn("Recently updated", html)
        self.assertIn("All articles", html)
        self.assertIn("card-no", html)
        # The old nav-duplicating ledger is gone.
        self.assertNotIn("contents-no", html)
        self.assertNotIn("masthead-vol", html)

    def test_post_page_structure(self):
        posts = load_entries(CONTENT / "posts")
        post = next(p for p in posts if p.meta["slug"] == "start-here")
        html = render_post_page(self.site, self.home, post)
        self.assertIn("article-head", html)
        self.assertIn("article-body", html)
        self.assertIn("article-title", html)
        # English page has no math → no KaTeX tags
        self.assertNotIn("katex.min.js", html)
        # Magazine furniture is gone: no folio, no vol/issue in the masthead
        self.assertNotIn("article-folio", html)
        self.assertNotIn("masthead-vol", html)

    def test_math_post_loads_katex(self):
        posts = load_entries(CONTENT / "posts")
        post = next(p for p in posts if p.meta["slug"] == "signal-sampling-reconstruction")
        html = render_post_page(self.site, self.home_zh, post)
        self.assertIn("katex.min.js", html)
        self.assertIn('<html lang="zh-CN">', html)

    def test_collection_page(self):
        posts = load_entries(CONTENT / "posts")
        html = render_collection_page(self.site, self.home, "en", "category", "notes", posts[:1])
        self.assertIn("page-title", html)
        self.assertIn("Back to blog", html)
        self.assertIn("categories/notes/", html)


if __name__ == "__main__":
    unittest.main()
