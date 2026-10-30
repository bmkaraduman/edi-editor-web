"""Build the self-contained static storefront (client-side ranking, no server):
the shared UI from web/ plus the catalog with precomputed facet scores.

    python3 scripts/export_static.py /path/to/giftfinder.html
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.config import COUNTRIES, MERCHANT_BY_ID, affiliate_link, format_price  # noqa: E402
from app.ml.preprocess import normalize  # noqa: E402
from app.ml.search import GiftSearch  # noqa: E402
from app.taxonomy import FACETS, FACET_TITLES, LEXICON, UI_LABELS  # noqa: E402


def main():
    engine = GiftSearch()
    items = []
    for i, p in enumerate(engine.products):
        scores = {}
        for facet, cols in engine.label_cols.items():
            for label, j in cols.items():
                s = float(engine.S[facet][i, j])
                if s >= 0.05:
                    scores[label] = round(s, 2)
        m = MERCHANT_BY_ID[p["merchant_id"]]
        items.append({
            "id": p["id"], "c": p["country"], "t": p["title"], "d": p["description"],
            "p": p["price"], "pt": format_price(p["price"], p["country"]), "m": m["name"],
            "e": p.get("emoji", "🎁"), "cid": p.get("concept_id", p["id"]),
            "u": affiliate_link(p["merchant_id"], product_url=p.get("url") or None, query=p["title"]),
            "n": normalize(p["title"] + " " + p["title"] + " " + p["description"]), "s": scores,
        })
    lex = {label: {lang: [normalize(x) for x in ws] for lang, ws in by.items()} for label, by in LEXICON.items()}
    out = {"countries": {cc: {k: c[k] for k in ("name", "lang", "currency", "flag")} for cc, c in COUNTRIES.items()},
           "facets": FACETS, "titles": FACET_TITLES, "labels": UI_LABELS, "lexicon": lex, "items": items,
           "report": json.load(open(os.path.join(os.path.dirname(__file__), "..", "app", "data", "models", "report.json")))}
    web = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
    read = lambda name: open(os.path.join(web, name), encoding="utf-8").read()
    data = json.dumps(out, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (
        "<title>GiftFinder</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n"
        "<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Manrope:wght@500;600;700&display=swap\">\n"
        f"<style>\n{read('style.css')}\n</style>\n{read('body.html')}\n"
        f"<script>const DATA = {data};</script>\n<script>\n{read('provider_static.js')}\n</script>\n<script>\n{read('ui.js')}\n</script>\n"
    )
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(web, "..", "giftfinder-static.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {dest} ({os.path.getsize(dest) // 1024} KB, {len(items)} products)")


if __name__ == "__main__":
    main()
