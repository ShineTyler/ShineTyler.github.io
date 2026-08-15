"""Paths and bilingual UI strings shared by the build pipeline."""
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
CONTENT = ROOT / "content"
PUBLIC = ROOT / "public"

SITE_URL = "https://shinetyler.github.io"
SITE_NAME = "Tyler's Corner"
OG_IMAGE_PATH = "/assets/images/og/og-cover.png"

LANG_DEFAULT = "en"

UI: Dict[str, Dict[str, str]] = {
    "en": {
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
        "start_here": "Start Here",
        "draft_project": "Coming soon",
        "project_label": "Project",
        "writing_intro": "Essays, project notes, reading logs, and short reflections. Clear writing matters more than volume.",
        "projects_intro": "A separate page for work I want to present with more room, context, and screenshots.",
        "masthead_vol": "Vol. 01 — The Student Edition",
        "masthead_issue": "No. 01 · MMXXVI",
        "colophon_label": "Colophon",
        "colophon_set": "Set in Playfair Display & IBM Plex Mono",
        "colophon_paper": "Printed on recycled pixels at 96 dpi",
        "issn_print": "ISSN 2994-0756",
        "issn_online": "ISSN 2994-0757",
        "about_eyebrow": "Profile",
        "blog_eyebrow": "The Writing Desk",
        "projects_eyebrow": "Selected Work",
        "read_more": "Read article",
        "continue": "Continue reading",
        "cover_eyebrow": "A student's notebook",
        "contents_label": "Recently updated",
        "portrait_caption": "Fig. 01 — The editor at work.",
        "lang_label": "中文",
        "language_nav": "Language",
        "previous_post": "Previous article",
        "next_post": "Next article",
        "view_all": "All articles",
        "category_label": "Category",
        "tag_label": "Tag",
        "category_intro": "Articles filed under this category.",
        "tag_intro": "Articles carrying this tag.",
        "minutes_read": "min read",
        "no_posts": "Nothing here yet — the first article is on its way.",
    },
    "zh-CN": {
        "home": "首页",
        "about": "关于",
        "projects": "项目",
        "blog": "博客",
        "contact": "联系",
        "primary_nav": "主导航",
        "email": "邮箱",
        "home_description": "一名学生的主页与博客。",
        "blog_description": "随笔、项目笔记、读书日志与短篇思考。",
        "projects_description": "Tyler 精选的与即将到来的项目。",
        "not_found_title": "页面未找到",
        "not_found_description": "找不到这个页面。",
        "not_found_heading": "这一页漂出了轨道。",
        "not_found_copy": "链接可能已经过时，或者页面在网站重组时被移动了位置。",
        "go_home": "回到首页",
        "read_article": "阅读全文",
        "back_to_blog": "返回博客",
        "read_project": "查看项目",
        "start_here": "从这里开始",
        "draft_project": "即将上线",
        "project_label": "项目",
        "writing_intro": "随笔、项目笔记、读书日志与短篇思考。清晰的写作比数量更重要。",
        "projects_intro": "用更多空间、背景与截图来呈现我想展示的作品。",
        "masthead_vol": "第一卷 — 学生特辑",
        "masthead_issue": "第 01 期 · MMXXVI",
        "colophon_label": "版权页",
        "colophon_set": "以 Playfair Display 与 IBM Plex Mono 排版",
        "colophon_paper": "以回收像素印制 · 96 dpi",
        "issn_print": "ISSN 2994-0756",
        "issn_online": "ISSN 2994-0757",
        "about_eyebrow": "人物志",
        "blog_eyebrow": "写作台",
        "projects_eyebrow": "精选作品",
        "read_more": "阅读全文",
        "continue": "继续阅读",
        "cover_eyebrow": "一名学生的学习笔记",
        "contents_label": "最近更新",
        "portrait_caption": "图 01 — 主编工作中。",
        "lang_label": "English",
        "language_nav": "语言",
        "previous_post": "上一篇文章",
        "next_post": "下一篇文章",
        "view_all": "全部文章",
        "category_label": "分类",
        "tag_label": "标签",
        "category_intro": "归档于该分类下的文章。",
        "tag_intro": "带有该标签的文章。",
        "minutes_read": "分钟",
        "no_posts": "这里暂时还没有内容——第一篇文章正在路上。",
    },
}


def t(lang: str, key: str) -> str:
    """Look up a UI string, falling back to English for missing keys."""
    table = UI.get(lang) or UI[LANG_DEFAULT]
    return table.get(key) or UI[LANG_DEFAULT].get(key, key)


def section_dir(lang: str) -> str:
    """Subdirectory that holds a language's pages ('' for the default language)."""
    return "" if lang == LANG_DEFAULT else f"{lang}/"


def page_path(lang: str, slug_path: str) -> str:
    """URL path for a page, e.g. page_path('zh-CN', 'blog/x/') -> 'zh-CN/blog/x/'."""
    return section_dir(lang) + slug_path
