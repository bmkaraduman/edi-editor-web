"""Pull products from every configured affiliate source, label them with the
trained text-mining model and merge them into the catalog.

    python3 scripts/ingest.py            # all countries
    python3 scripts/ingest.py DE TR      # some countries
    INGEST_LIMIT=1000 python3 scripts/ingest.py DE   # products per source (per advertiser for Awin feeds)

Sources without credentials/files are skipped, so the command is safe to run
at any time (e.g. nightly from cron). Re-train afterwards if you hand-label
some of the new items (set "source": "manual").
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.config import COUNTRIES  # noqa: E402
from app.ml.search import GiftSearch  # noqa: E402
from app.ml.labeling import label_product  # noqa: E402
from app.ml.weak_labels import expand_query  # noqa: E402
from app.sources import SOURCES  # noqa: E402
from app.sources.images import verify_images  # noqa: E402
from app.taxonomy import FACETS  # noqa: E402

CATALOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "data", "catalog.json")


def gift_queries(lang):
    """Search phrases per label in the country's language."""
    qs = []
    for facet in ("occasion", "personality"):
        for label in FACETS[facet]:
            qs.append(expand_query([label], lang).split(" ")[0] + " " + {"en": "gift", "de": "geschenk", "tr": "hediye", "nl": "cadeau", "fr": "cadeau"}[lang])
    return qs


def main(countries):
    with open(CATALOG, encoding="utf-8") as f:
        catalog = json.load(f)
    by_id = {p["id"]: p for p in catalog}
    engine = GiftSearch()
    added = 0
    for cc in countries:
        lang = COUNTRIES[cc]["lang"]
        queries = gift_queries(lang)
        for cls in SOURCES:
            src = cls(cc)
            if not src.available():
                print(f"[{cc}] {src.name}: not configured, skipped")
                continue
            print(f"[{cc}] {src.name}: fetching {len(queries)} queries")
            fetched = list(src.fetch(queries, limit=int(os.environ.get("INGEST_LIMIT", "500"))))
            for product in verify_images(fetched):
                product.labels = label_product(engine, product.title, product.description, product)
                d = product.to_dict()
                if d["id"] not in by_id:
                    added += 1
                by_id[d["id"]] = d
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(list(by_id.values()), f, ensure_ascii=False, indent=0)
    print(f"catalog: {len(by_id)} products ({added} new)")


if __name__ == "__main__":
    main([c.upper() for c in sys.argv[1:]] or list(COUNTRIES))
