"""Landing pages: every language has the texts of every list, and the build writes a home page
per country and a page per list that has enough well-fitting products, with the products in
the HTML, hreflang alternates and a sitemap."""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import list_pages  # noqa: E402
from app.config import COUNTRIES, format_price  # noqa: E402
from app.taxonomy import FACETS  # noqa: E402

TEXTS = list_pages.load()
placeholders = lambda s: sorted(re.findall(r"\{\w+\}", s))


def test_every_language_has_every_list_with_the_same_placeholders():
    en = TEXTS["en"]
    assert set(en["lists"]) == set(list_pages.BY_ID)
    for lang, t in TEXTS.items():
        assert set(t["lists"]) == set(en["lists"]), lang
        for key in ("under_slug", "under_h1", "under_description"):
            assert placeholders(t[key]) == placeholders(en[key]), (lang, key)
        for part in ("home", "ui"):
            assert set(t[part]) == set(en[part]), (lang, part)
            for k, v in en[part].items():
                assert placeholders(t[part][k]) == placeholders(v), (lang, part, k)
        for lid, v in t["lists"].items():
            assert set(v) == {"slug", "h1", "title", "description", "intro"}, (lang, lid)
            assert len(v["title"]) <= 62 and 110 <= len(v["description"]) <= 170, (lang, lid)


def test_lists_use_real_facet_ids():
    for lid, group, filters, guide, emoji in list_pages.LISTS:
        assert group in list_pages.GROUPS
        for k, v in filters.items():
            assert v in FACETS[k], (lid, k, v)
    assert set(list_pages.BUDGET_LISTS) <= set(list_pages.BY_ID)


def test_british_english_says_mum_under_the_same_id():
    gb = list_pages.texts_for("GB", "en", TEXTS)
    assert gb["lists"]["for-mom"]["h1"] == "Gifts for mum" and gb["lists"]["for-mom"]["slug"] == "for-mum"
    assert list_pages.texts_for("US", "en", TEXTS)["lists"]["for-mom"]["h1"] == "Gifts for mom"


class FakeEngine:
    """Twenty products fit every search in GB and DE; in FR only five do (no list pages there)."""
    def search(self, country, price_max=None, limit=24, **filters):
        n = 5 if country == "FR" else 20
        rows = [{"id": f"{country}{i}", "title": f"Gift {i}", "description": "A nice thing", "price": 10.0 + i, "price_text": format_price(10.0 + i, country),
                 "rrp_text": None, "merchant": f"Shop {i % 3}", "image": f"https://img.example/{i}.jpg", "emoji": "🎁", "match": 90} for i in range(n)]
        rows = [r for r in rows if price_max is None or r["price"] <= price_max]
        return {"total": len(rows), "demo": False, "results": rows[:limit]}


def test_build_writes_home_and_list_pages(tmp_path):
    render = lambda lang, head, html="", cfg=None, slots=None: (
        f'<html lang="{lang}"><head>{head}</head><body>{(slots or {}).get("before_results", "")}{(slots or {}).get("results", "")}{html}<!--{cfg}--></body></html>')
    name = list_pages.build(str(tmp_path), render, FakeEngine(), {"GB0": "https://shop.example/0"}, ["GB", "DE", "FR"], COUNTRIES, format_price)
    assert name == "sitemap-pages.xml"
    page = (tmp_path / "gb" / "gifts" / "for-dad" / "index.html").read_text(encoding="utf-8")
    assert "<h1>" in page and "Gifts for dad" in page and page.count('<article class="card">') == 20
    assert 'href="https://shop.example/0"' in page and 'rel="nofollow sponsored noopener"' in page
    assert "20 gift ideas from 3 shops in the United Kingdom" in page
    assert '<link rel="canonical" href="https://giftdetect.com/gb/gifts/for-dad/">' in page
    assert '<link rel="alternate" hreflang="de-DE" href="https://giftdetect.com/de/geschenke/fuer-papa/">' in page
    assert 'hreflang="fr-FR"' not in page                       # too few products in France: no page, no alternate
    assert "'sel': 'gender=male&occasion=fathers_day'" in page and '"@type": "ItemList"' in page
    assert (tmp_path / "gb" / "gifts" / "for-mum" / "index.html").exists()
    under = (tmp_path / "gb" / "gifts" / "christmas" / "under-40" / "index.html").read_text(encoding="utf-8")
    assert "Christmas gifts under £40" in under and "max=40" in under
    home = (tmp_path / "de" / "index.html").read_text(encoding="utf-8")
    assert 'href="/de/geschenke/fuer-papa/"' in home and 'hreflang="x-default" href="https://giftdetect.com/"' in home
    assert not (tmp_path / "fr" / "cadeaux").exists() and (tmp_path / "fr" / "index.html").exists()
    root = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'href="/gb/"' in root and '<link rel="canonical" href="https://giftdetect.com/">' in root
    sitemap = (tmp_path / "sitemap-pages.xml").read_text(encoding="utf-8")
    assert "<loc>https://giftdetect.com/gb/gifts/for-dad/</loc>" in sitemap and "/p/" not in sitemap
