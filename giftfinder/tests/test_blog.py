"""The blog: every language has the same guides with the same search filters, and the export
writes crawlable pages with hreflang alternates and a sitemap."""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import blog_pages  # noqa: E402
from app.taxonomy import FACETS  # noqa: E402

DATA = blog_pages.load()


def filters(article):
    """The search filters of an article, without the price ceilings (those follow the currency)."""
    specs = [article.get("search", "")] + re.findall(r"\[\[search\s*(.*?)\|", article["body"])
    return [sorted(p for p in spec.split() if not p.startswith(("max=", "min="))) for spec in specs]


def test_every_language_has_the_english_guides_with_the_same_filters():
    en = {a["id"]: a for a in DATA["en"]}
    assert len(en) == 20
    for lang, arts in DATA.items():
        assert lang in blog_pages.LANG_COUNTRY and lang in blog_pages.T
        assert {a["id"] for a in arts} == set(en), lang
        for a in arts:
            assert filters(a) == filters(en[a["id"]]), (lang, a["id"])
            assert re.findall(r"\]\(blog:([^)]+)\)", a["body"]) == re.findall(r"\]\(blog:([^)]+)\)", en[a["id"]]["body"]), (lang, a["id"])
            assert len(a["title"]) <= 70 and 110 <= len(a["description"]) <= 170, (lang, a["id"])


def test_search_buttons_use_real_facet_ids():
    for lang, arts in DATA.items():
        for a in arts:
            for spec in [a.get("search", "")] + re.findall(r"\[\[search\s*(.*?)\|", a["body"]):
                for part in spec.split():
                    k, _, v = part.partition("=")
                    if k in ("max", "min"):
                        assert v.isdigit(), (lang, a["id"], part)
                    else:
                        assert k in FACETS and all(x in FACETS[k] for x in v.split(",")), (lang, a["id"], part)


def test_markdown_subset():
    html, faq = blog_pages.to_html("Intro with **bold** and [dad](blog:gifts-for-dad).\n\n## Ideas\n\n- one\n- two\n\n"
                                   "[[search occasion=christmas max=25 | Find]]\n\n### Is it late?\n\nNo, not yet.", "en",
                                   {"gifts-for-dad": "gifts-for-dad"})
    assert '<strong>bold</strong>' in html and 'href="/blog/en/gifts-for-dad/"' in html
    assert "<ul><li>one</li><li>two</li></ul>" in html
    assert 'class="blog-cta" href="/?occasion=christmas&amp;max=25"' in html
    assert faq == [["Is it late?", "No, not yet."]] or faq == [("Is it late?", "No, not yet.")]


def test_build_writes_pages_with_alternates(tmp_path):
    render = lambda lang, head, html, cfg: f'<html lang="{lang}"><head>{head}</head><body>{html}</body></html>'
    assert blog_pages.build(str(tmp_path), render) == "sitemap-blog.xml"
    langs = list(DATA)
    for lang in langs:
        page = (tmp_path / "blog" / lang / "index.html").read_text(encoding="utf-8")
        assert f'<html lang="{lang}">' in page and page.count("post-card") == 20
        first = DATA[lang][0]
        art = (tmp_path / "blog" / lang / first["slug"] / "index.html").read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="https://giftdetect.com/blog/{lang}/{first["slug"]}/">' in art
        assert art.count('rel="alternate" hreflang=') == len(langs) + 1          # every language + x-default
        assert '"@type": "BlogPosting"' in art and 'class="blog-cta"' in art
    sitemap = (tmp_path / "sitemap-blog.xml").read_text(encoding="utf-8")
    assert sitemap.count("<url>") == len(langs) * 21
