"""Build the serverless storefront for static hosting (Cloudflare Pages, GitHub Pages ...):

    python3 scripts/export_static.py dist/

Writes dist/index.html (the shared UI with the browser-side provider), dist/data.json
(the visible catalog of the active countries with everything the ranker needs
precomputed: facet scores, giftability, the next dated occasion per country; duplicate
keys and the near-duplicate test are cheap enough to run in the browser) and dist/_redirects so /p/{id} product pages
resolve to the app. Everything that needs the model or pairwise similarity is done
here, once, so the browser only sorts.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.config import ACTIVE_COUNTRIES, COUNTRIES, MERCHANT_BY_ID, affiliate_link, format_price  # noqa: E402
from app.ml.preprocess import normalize  # noqa: E402
from app.ml.search import GiftSearch  # noqa: E402
from app.occasions import upcoming  # noqa: E402
from app.taxonomy import FACETS, FACET_TITLES, LEXICON, UI_LABELS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
DESC_CHARS = 400


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
    lex = {label: {lang: [normalize(x) for x in ws] for lang, ws in by.items()} for label, by in LEXICON.items()}
    report_path = os.path.join(HERE, "..", "app", "data", "models", "report.json")
    data = {
        "countries": {cc: {k: c[k] for k in ("name", "lang", "currency", "flag")} for cc, c in COUNTRIES.items() if cc in ACTIVE_COUNTRIES},
        "real": sorted(engine.real_countries & set(ACTIVE_COUNTRIES)),
        "upcoming": {cc: dict(upcoming(cc), label=UI_LABELS[upcoming(cc)["occasion"]][COUNTRIES[cc]["lang"]]) for cc in ACTIVE_COUNTRIES},
        "facets": FACETS, "titles": FACET_TITLES, "labels": UI_LABELS, "lexicon": lex, "items": items,
        "report": json.load(open(report_path)) if os.path.exists(report_path) else {},
    }
    os.makedirs(dest, exist_ok=True)
    read = lambda name: open(os.path.join(WEB, name), encoding="utf-8").read()
    with open(os.path.join(dest, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    page = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>giftdetect.com</title>
<meta name="description" content="giftdetect.com: Geschenk-Suchmaschine. Wähle, für wen es ist, den Anlass und die Persönlichkeit und bekomme passende Geschenkideen aus deutschen Shops.">
<link rel="canonical" href="https://giftdetect.com/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🎁%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Manrope:wght@500;600;700&display=swap">
<style>
{read('style.css')}
</style></head><body>
{read('body.html')}
<script>
{read('provider_static.js')}
</script>
<script>
{read('ui.js')}
</script></body></html>"""
    with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(dest, "_redirects"), "w") as f:
        f.write("/p/*  /index.html  200\n")
    with open(os.path.join(dest, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: https://giftdetect.com/sitemap.xml\n")
    with open(os.path.join(dest, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>https://giftdetect.com/</loc></url>\n')
        for it in items:
            f.write(f"<url><loc>https://giftdetect.com/p/{it['id']}</loc></url>\n")
        f.write("</urlset>\n")
    sizes = {n: os.path.getsize(os.path.join(dest, n)) // 1024 for n in ("index.html", "data.json")}
    print(f"wrote {dest}: index.html {sizes['index.html']} KB, data.json {sizes['data.json']} KB, {len(items)} products")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "dist"))
