"""Build the serverless storefront for static hosting (Cloudflare Pages, GitHub Pages ...):

    python3 scripts/export_static.py dist/

Writes dist/index.html (the shared UI with the browser-side provider), dist/data.json
(the visible catalog of the active countries with everything the ranker needs
precomputed: facet scores, giftability, the next dated occasion per country; duplicate
keys and the near-duplicate test are cheap enough to run in the browser), dist/_redirects so /p/{id} product pages
resolve to the app, the country home pages and gift lists (list_pages.py) and the blog (blog_pages.py). Everything that needs the model or pairwise similarity is done
here, once, so the browser only sorts.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.config import ACTIVE_COUNTRIES, COUNTRIES, GA_MEASUREMENT_ID, MERCHANT_BY_ID, affiliate_link, format_price  # noqa: E402
from app.i18n import web_script  # noqa: E402
import blog_pages  # noqa: E402
import list_pages  # noqa: E402
from app.ml.preprocess import normalize  # noqa: E402
from app.ml.search import GiftSearch  # noqa: E402
from app.occasions import upcoming  # noqa: E402
from app.taxonomy import FACETS, FACET_TITLES, LEXICON, UI_LABELS, clashes  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
DESC_CHARS = 400


def page_renderer(dest=None):
    """render(lang, head, blog_html="", blog_cfg=None, slots=None) -> a full page: the gift search, plus
    (on blog and list pages) content under the results.

    blog_cfg becomes window.BLOG (web/ui.js): the page's language and country and what kind of
    page it is. slots fill the static parts of a landing page: {"hero": (h1, sub)},
    {"before_results": html, "results": cards html, "title": heading of the results}.
    With dest, the styles and scripts are written once to dest/assets/ and linked (every page
    shares them from the browser cache); without it they are inlined."""
    read = lambda name: open(os.path.join(WEB, name), encoding="utf-8").read()
    body = read("body.html")
    css = read("style.css")
    js = "\n".join([web_script(), read("provider_static.js"), read("ui.js"), read("analytics.js")])
    if dest:
        assets = os.path.join(dest, "assets")
        shutil.rmtree(assets, ignore_errors=True)
        os.makedirs(assets)
        tag = hashlib.sha1((css + js).encode("utf-8")).hexdigest()[:10]
        open(os.path.join(assets, f"app.{tag}.css"), "w", encoding="utf-8").write(css)
        open(os.path.join(assets, f"app.{tag}.js"), "w", encoding="utf-8").write(js)
        style, script = f'<link rel="stylesheet" href="/assets/app.{tag}.css">', f'<script src="/assets/app.{tag}.js"></script>'
    else:
        style, script = f"<style>\n{css}\n</style>", f"<script>\n{js}\n</script>"

    def render(lang, head, blog_html="", blog_cfg=None, slots=None):
        b, slots = body, slots or {}
        results = '<main class="results gutter" id="results-wrap" hidden>'
        if slots.get("results"):
            b = b.replace(results, slots.get("before_results", "") + '\n<main class="results gutter" id="results-wrap">', 1)
            b = b.replace('<section class="grid" id="results"></section>', f'<section class="grid" id="results">{slots["results"]}</section>', 1)
            b = b.replace('<h2 id="title"></h2>', f'<h2 id="title">{html.escape(slots.get("title", ""))}</h2>', 1)
        if slots.get("hero"):
            h1, sub = slots["hero"]
            b = b.replace('<h1 id="t-hero"></h1>', f'<h1 id="t-hero">{html.escape(h1)}</h1>', 1).replace('<p id="t-sub"></p>', f'<p id="t-sub">{html.escape(sub)}</p>', 1)
        if blog_html:
            b = b.replace('<section class="product-page gutter" id="product-wrap" hidden>', blog_html + '\n<section class="product-page gutter" id="product-wrap" hidden>', 1)
        cfg = f"window.BLOG={json.dumps(blog_cfg)};" if blog_cfg else ""
        mode = ' class="blog-mode"' if blog_cfg and not blog_cfg.get("home") else ""
        return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🎁%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Manrope:wght@500;600;700&display=swap">
{style}</head><body{mode}>
{b}
<script>{cfg}window.GA_ID={json.dumps(GA_MEASUREMENT_ID)};</script>
{script}</body></html>"""
    return render


def main(dest):
    engine = GiftSearch()
    rows = [i for i, p in enumerate(engine.products) if engine.visible[i] and p["country"] in ACTIVE_COUNTRIES]
    items = []
    for i in rows:
        p = engine.products[i]
        scores = {}
        for facet, cols in engine.label_cols.items():
            for label, j in cols.items():
                s = float(engine.S[facet][i, j])
                if s >= 0.05:
                    scores[label] = round(s, 2)
        m = MERCHANT_BY_ID.get(p["merchant_id"]) or {"name": p.get("merchant_name") or "Shop"}
        item = {
            "id": p["id"], "c": p["country"], "t": p["title"],
            "d": (p.get("details", {}).get("short_description") or p["description"])[:DESC_CHARS],
            "p": p["price"], "pt": format_price(p["price"], p["country"]), "m": m["name"], "mid": p["merchant_id"],
            "e": p.get("emoji", "🎁"), "g": round(float(engine.gifty[i]), 2),
            "u": affiliate_link(p["merchant_id"], product_url=p.get("url") or None, query=p["title"]),
            "s": scores, "lab": p.get("labels", {}), "src": p.get("source", "feed"),
        }
        if p.get("concept_id"):
            item["cid"] = p["concept_id"]
        for key, field in (("i", "image"), ("imgs", "images"), ("b", "brand"), ("r", "rules"), ("det", "details")):
            if p.get(field):
                item[key] = p[field]
        if p.get("rrp"):
            item["rt"] = format_price(p["rrp"], p["country"])
        if p.get("category_path") or p.get("category"):
            item["cat"] = p.get("category_path") or p.get("category")
        if p.get("product_type"):
            item["pt2"] = p["product_type"]
        if p.get("keywords"):
            item["kw"] = [k.strip() for k in re.split(r"[,;>|]", p["keywords"]) if k.strip()]
        items.append(item)
    # countries are listed only once they have products (CH and BE wait for their shops' approval);
    # their visitors land on a neighbour (web/ui.js NEAR)
    shown = [cc for cc in ACTIVE_COUNTRIES if any(it["c"] == cc for it in items)]
    lex = {label: {lang: [normalize(x) for x in ws] for lang, ws in by.items()} for label, by in LEXICON.items()}
    report_path = os.path.join(HERE, "..", "app", "data", "models", "report.json")
    data = {
        "countries": {cc: {k: c[k] for k in ("name", "lang", "currency", "flag", "locale")} for cc, c in COUNTRIES.items() if cc in shown},
        "real": sorted(engine.real_countries & set(shown)),
        "upcoming": {cc: dict(upcoming(cc), label=UI_LABELS[upcoming(cc)["occasion"]][COUNTRIES[cc]["lang"]]) for cc in shown},
        "facets": FACETS, "titles": FACET_TITLES, "clashes": clashes(), "labels": UI_LABELS, "lexicon": lex,
        "counts": {cc: sum(it["c"] == cc for it in items) for cc in shown},
        "report": json.load(open(report_path)) if os.path.exists(report_path) else {},
    }
    os.makedirs(dest, exist_ok=True)
    read = lambda name: open(os.path.join(WEB, name), encoding="utf-8").read()
    # Shared metadata in data.json, each country's products in items-<CC>.json (the browser
    # loads only the chosen country; one file for all would pass Cloudflare's 25 MB limit),
    # and where.json (product id -> country) for product links opened from outside.
    for name in os.listdir(dest) if os.path.isdir(dest) else []:
        if name.startswith("items-") and name.endswith(".json"):
            os.remove(os.path.join(dest, name))
    dump = lambda name, obj: json.dump(obj, open(os.path.join(dest, name), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    dump("data.json", data)
    for cc in shown:
        dump(f"items-{cc}.json", [it for it in items if it["c"] == cc])
    dump("where.json", {cc: "".join(it["id"] for it in items if it["c"] == cc) for cc in shown})
    render = page_renderer(dest)
    with open(os.path.join(dest, "_redirects"), "w") as f:
        f.write("/p/*  /index.html  200\n")
    # product pages repeat the shops' texts: usable, but not for the index; assets never change under their name
    with open(os.path.join(dest, "_headers"), "w") as f:
        f.write("/p/*\n  X-Robots-Tag: noindex\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    with open(os.path.join(dest, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: https://giftdetect.com/sitemap.xml\n")
    for name in os.listdir(dest):
        if name.startswith("sitemap-") and name.endswith(".xml"):
            os.remove(os.path.join(dest, name))
    # the home pages and gift lists (they also write index.html), then the blog; sitemap.xml indexes both
    parts = [list_pages.build(dest, render, engine, {it["id"]: it["u"] for it in items}, shown, COUNTRIES, format_price)]
    blog_map = blog_pages.build(dest, lambda lang, head, html, cfg: render(lang, head, html, cfg))
    if blog_map:
        parts.append(blog_map)
    with open(os.path.join(dest, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for name in parts:
            f.write(f"<sitemap><loc>https://giftdetect.com/{name}</loc></sitemap>\n")
        f.write("</sitemapindex>\n")
    files = ["index.html", "data.json", "where.json"] + [f"items-{cc}.json" for cc in shown]
    sizes = ", ".join(f"{n} {os.path.getsize(os.path.join(dest, n)) // 1024} KB" for n in files)
    print(f"wrote {dest}: {sizes}; {len(items)} products")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "dist"))
