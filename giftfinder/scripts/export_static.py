"""Export the catalog with precomputed facet scores for the static demo page
(client-side ranking, no server needed).

    python3 scripts/export_static.py > /path/to/data.json
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
    json.dump(out, sys.stdout, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
