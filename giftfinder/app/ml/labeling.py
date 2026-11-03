"""Production labelling for new feed items.

Priority, per facet:
  1. rules on the strong text (title, category path, product type, keywords, brand)
     -> app/data/rules.py
  2. lexicon hits on the strong text
  3. lexicon hits in the description, only multi-hit (>= 2) ones and only for a
     facet no rule decided, so a scent note ("schwarzer Tee") or a sock's
     "Laserschnitt-Technik" does not turn the product into a coffee or tech gift
  4. the trained classifier fills what is still empty

Gender is single-label: rules > strong lexicon > classifier; the description only
counts with an explicit multi-word cue ("für ihn", "for her").
"""
from ..data.rules import match_rules
from ..taxonomy import FACETS, LEXICON
from .preprocess import normalize
from .weak_labels import lexicon_scores

_MULTIWORD = {label: {normalize(p) for ps in by.values() for p in ps if " " in p} for label, by in LEXICON.items()}


def strong_text(title, keywords="", category="", category_path="", product_type="", brand=""):
    return normalize(" ".join([title or "", keywords or "", category or "", category_path or "", product_type or "", brand or ""]))


def _facet_of(label):
    for facet, labels in FACETS.items():
        if label in labels:
            return facet
    return None


def label_product(engine, title, description, product=None):
    """Return facet -> [labels]. `product` (a Product or dict) adds the strong fields;
    when it is given, its `rules` and `gift` fields are filled in too."""
    get = (lambda k: getattr(product, k, "")) if product is not None and not isinstance(product, dict) else (lambda k: (product or {}).get(k, ""))
    strong = strong_text(title, get("keywords"), get("category"), get("category_path"), get("product_type"), get("brand"))
    rule_labels, rule_ids, gift = match_rules(strong)
    strong_hits = lexicon_scores(strong)
    desc_hits = lexicon_scores(description or "")
    desc_norm = f" {normalize(description or '')} "
    predicted = engine.predict_labels(title, description) if engine is not None else {}

    out = {}
    for facet, labels in FACETS.items():
        picked = list(rule_labels.get(facet, []))
        if facet == "gender":
            if not picked:
                strong_g = [(strong_hits.get(l, 0), l) for l in ("female", "male") if strong_hits.get(l, 0)]
                if strong_g:
                    picked = [max(strong_g)[1]]
                else:
                    for g in ("female", "male"):
                        if any(f" {p} " in desc_norm for p in _MULTIWORD.get(g, ())):
                            picked = [g]
                            break
            out[facet] = (picked or predicted.get(facet) or ["unisex"])[:1]
            continue
        strong_l = sorted(((strong_hits.get(l, 0), l) for l in labels if strong_hits.get(l, 0)), reverse=True)
        picked += [l for _, l in strong_l if l not in picked]
        if not rule_labels.get(facet):   # description cues only where no category rule decided the facet
            weak_l = sorted(((desc_hits.get(l, 0), l) for l in labels if desc_hits.get(l, 0) >= 2), reverse=True)
            picked += [l for _, l in weak_l if l not in picked]
        if not picked:          # the classifier only fills a facet no rule or lexicon cue decided
            picked += list(predicted.get(facet, []))
        out[facet] = picked[:3]

    if product is not None:
        if isinstance(product, dict):
            product["rules"], product["gift"] = rule_ids, gift
        else:
            product.rules, product.gift = rule_ids, gift
    return out
