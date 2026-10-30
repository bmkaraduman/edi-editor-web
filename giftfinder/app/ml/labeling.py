"""Production labelling for new feed items: classifier ∪ lexicon."""
from ..taxonomy import FACETS
from .weak_labels import weak_labels


def label_product(engine, title, description):
    predicted = engine.predict_labels(title, description)
    weak = weak_labels(f"{title} {description}")
    out = {}
    for facet in FACETS:
        if facet == "gender":
            # an explicit gender cue beats the classifier's guess of unisex
            strong = [g for g in weak.get("gender", []) if g != "unisex"]
            out[facet] = strong[:1] or predicted.get(facet, ["unisex"])[:1]
        else:
            out[facet] = list(dict.fromkeys(weak.get(facet, []) + predicted.get(facet, [])))[:3]
    return out
