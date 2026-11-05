"""Build the seed catalog: every labelled concept becomes several merchant
listings per country, with language-specific augmented descriptions.

    python3 scripts/build_seed.py            -> app/data/catalog.json
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.config import COUNTRIES, MERCHANTS  # noqa: E402
from app.data.concepts import CONCEPTS  # noqa: E402
from app.sources.base import Product  # noqa: E402
from app.ml.augment import augment  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "data", "catalog.json")

def nice_price(usd, country):
    c = COUNTRIES[country]
    v = usd * c["usd_rate"]
    if c["currency"] == "TRY":
        return float(round(v / 10) * 10 - 0.1)
    return float(int(v)) + 0.99


def main(variants_per_country=5, seed=1):
    rng = random.Random(seed)
    products = []
    for concept in CONCEPTS:
        lo, hi = concept["price_usd"]
        for cc, cinfo in COUNTRIES.items():
            lang = cinfo["lang"]
            if lang not in concept["text"]:          # added languages have no hand-written concept text
                continue
            pool = [m for m in MERCHANTS[cc] if not m.get("fit") or set(m["fit"]) & set(concept["personality"])]
            merchants = rng.sample(pool, k=min(variants_per_country, len(pool)))
            for m in merchants:
                title, desc = augment(rng, concept, lang)
                p = Product(
                    id=Product.make_id(m["id"], f"{concept['id']}:{title}"),
                    country=cc, lang=lang, merchant_id=m["id"], title=title, description=desc,
                    price=nice_price(rng.uniform(lo, hi), cc), currency=cinfo["currency"],
                    url="", image="", brand="", category="",
                    labels={"gender": [concept["gender"]], "age": concept["age"],
                            "occasion": concept["occasion"], "personality": concept["personality"]},
                    source="seed",
                ).to_dict()
                p["concept_id"] = concept["id"]
                p["emoji"] = concept["emoji"]
                products.append(p)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=0)
    print(f"wrote {len(products)} products to {OUT}")


if __name__ == "__main__":
    main()
