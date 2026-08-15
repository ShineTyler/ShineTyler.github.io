"""Markdown processing: math protection, plain-text helpers, HTML rendering.

Rendering is delegated to the vendored Python-Markdown library (BSD-3-Clause,
kept in src/vendor/markdown/ with its LICENSE.md) so the site gains tables,
fenced code blocks, blockquotes and nested lists, while the build itself
still requires nothing but Python 3.
"""
import re
from typing import List, Tuple

import markdown as _md

MD_EXTENSIONS = [
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.sane_lists",
]


def protect_math(text: str) -> Tuple[str, List[str]]:
    """Replace math blocks with placeholders so HTML escaping won't mangle
    & < > inside them, and emphasis parsing won't touch $ delimiters."""
    blocks: List[str] = []

    def save(m: re.Match) -> str:
        blocks.append(m.group(0))
        return f"\x00MATH{len(blocks) - 1}\x00"

    # Display math first ($$...$$), then inline math ($...$)
    text = re.sub(r'\$\$[^$]+\$\$', save, text)
    text = re.sub(r'(?<!\$)\$[^$]+\$(?!\$)', save, text)
    return text, blocks


def restore_math(text: str, blocks: List[str]) -> str:
    """Restore math blocks from placeholders."""
    for i, block in enumerate(blocks):
        text = text.replace(f"\x00MATH{i}\x00", block)
    return text


def strip_markdown(text: str) -> str:
    """Strip inline Markdown syntax — used only for plain-text contexts
    (summary, reading time, etc.)."""
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
    math_text, math_blocks = protect_math(markdown)
    rendered = _md.markdown(
        math_text,
        extensions=MD_EXTENSIONS,
        output_format="html5",
    )
    rendered = restore_math(rendered, math_blocks)
    # Keep the site's signature link treatment on every Markdown link.
    rendered = re.sub(r'<a href="', r'<a class="post-link" href="', rendered)
    # Wrap images in a figure span so CSS can layer the sepia/noise treatment.
    rendered = re.sub(
        r'<img\s+([^>]*?)\s*/?>',
        r'<span class="post-figure"><img \1 class="post-image" loading="lazy"></span>',
        rendered,
    )
    return rendered


def reading_time(body: str, lang: str = "en") -> str:
    """Estimate reading time. Chinese counts CJK characters (~400/min);
    other text counts words (~180/min)."""
    from .config import t

    text = strip_markdown(body)
    if lang.startswith("zh"):
        cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
        other_words = max(0, len(re.sub(r"[\u4e00-\u9fff]", " ", text).split()))
        minutes = max(1, round(cjk / 400 + other_words / 180))
    else:
        minutes = max(1, round(len(text.split()) / 180))
    return f"{minutes} {t(lang, 'minutes_read')}"
