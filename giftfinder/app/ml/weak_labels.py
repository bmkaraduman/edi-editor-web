"""Lexicon-based weak labelling and query expansion.

Raw affiliate feeds come without gift facets. Before (or instead of) the
trained classifier we score each facet label by counting lexicon hits in the
product text. The same lexicon turns a visitor's filter choice into a
language-specific pseudo-query for the TF-IDF retriever.
"""
from collections import defaultdict

from ..taxonomy import LEXICON, FACETS, LANGS
from .preprocess import normalize

# label -> set of normalised phrases over all languages
_PHRASES = {}
for label, by_lang in LEXICON.items():
    _PHRASES[label] = {normalize(p) for ps in by_lang.values() for p in ps}


def lexicon_scores(text):
    """Return {label: hit_count} for every label with at least one hit."""
    padded = f" {normalize(text)} "
    scores = defaultdict(int)
    for label, phrases in _PHRASES.items():
        for p in phrases:
            if f" {p} " in padded:
                scores[label] += 1 + p.count(" ")   # multi-word hits count more
    return dict(scores)


def weak_labels(text, min_hits=1):
    """Produce facet -> [labels] from lexicon hits alone."""
    scores = lexicon_scores(text)
    out = {}
    for facet, labels in FACETS.items():
        hits = [(scores.get(l, 0), l) for l in labels if scores.get(l, 0) >= min_hits]
        hits.sort(reverse=True)
        if facet == "gender":
            out[facet] = [hits[0][1]] if hits else ["unisex"]
        elif facet == "category":
            out[facet] = [hits[0][1]] if hits else []
        else:
            out[facet] = [l for _, l in hits[:3]]
    return out


def expand_query(labels, lang):
    """Turn selected labels into a bag of lexicon words in `lang` (plus
    English, which many feeds mix in)."""
    words = []
    for label in labels:
        for l in (lang, "en") if lang != "en" else ("en",):
            words.extend(LEXICON.get(label, {}).get(l, [])[:6])
    return " ".join(words)
