"""The gift search engine.

Ranking = text relevance (TF-IDF cosine between the visitor's query and the
product's title+description) + facet affinity (classifier probability, or
the hand label when one exists, for every facet the visitor selected).
When the visitor types nothing, the selected facets are expanded into a
pseudo-query in the country's language through the lexicon, so pure
"filter" searches still benefit from the text index.
"""
import json
import os

import numpy as np
from joblib import load
from scipy.sparse import hstack
from sklearn.preprocessing import normalize as l2

from ..config import COUNTRIES, MERCHANT_BY_ID, format_price
from ..taxonomy import FACETS, UI_LABELS
from .preprocess import doc_text, normalize
from .train import THRESHOLD, lexicon_features
from .weak_labels import expand_query, lexicon_scores

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

WEIGHTS = {"text": 1.0, "gender": 0.9, "age": 0.6, "occasion": 0.8, "personality": 1.0}


class GiftSearch:
    def __init__(self, catalog_path=None, model_path=None):
        catalog_path = catalog_path or os.path.join(DATA, "catalog.json")
        model_path = model_path or os.path.join(DATA, "models", "facet_model.joblib")
        with open(catalog_path, encoding="utf-8") as f:
            self.products = json.load(f)
        bundle = load(model_path)
        self.vecs = bundle["vectorizers"]
        self.heads = bundle["heads"]
        self.by_id = {p["id"]: p for p in self.products}
        self._index()

    # ------------------------------------------------------------ indexing
    def _featurize(self, texts):
        return hstack([v.transform(texts) for v in self.vecs.values()] + [lexicon_features(texts)]).tocsr()

    def _index(self):
        texts = [doc_text(p["title"], p["description"], p.get("brand", ""), p.get("category", "")) for p in self.products]
        Xraw = self._featurize(texts)
        self.X = l2(Xraw)          # unit vectors for cosine retrieval
        n = len(self.products)
        self.label_cols = {}
        self.S = {}
        for facet, head in self.heads.items():
            classes = head["classes"]
            P = head["clf"].predict_proba(Xraw)
            # hand labels override the classifier where they exist
            for i, p in enumerate(self.products):
                given = p.get("labels", {}).get(facet)
                if given:
                    row = np.zeros(len(classes))
                    for l in given:
                        if l in classes:
                            row[classes.index(l)] = 1.0
                    P[i] = np.maximum(P[i] * 0.5, row)
            self.S[facet] = P
            self.label_cols[facet] = {l: j for j, l in enumerate(classes)}
        self.country = np.array([p["country"] for p in self.products])
        self.price = np.array([float(p["price"]) for p in self.products])

    # ------------------------------------------------------------ querying
    def predict_labels(self, title, description, threshold=THRESHOLD):
        """Facet labels for a new product (used by the ingest pipeline)."""
        X = self._featurize([doc_text(title, description)])
        out = {}
        for facet, head in self.heads.items():
            P = head["clf"].predict_proba(X)[0]
            classes = head["classes"]
            if facet == "gender":
                out[facet] = [classes[int(P.argmax())]]
            else:
                picked = [classes[j] for j in np.argsort(-P) if P[j] >= threshold][:3]
                out[facet] = picked
        return out

    def search(self, country, q="", gender=None, age=None, occasion=None, personality=None,
               price_min=None, price_max=None, limit=24, offset=0):
        country = country.upper()
        if country not in COUNTRIES:
            raise ValueError("unknown country")
        lang = COUNTRIES[country]["lang"]
        age = [a for a in (age or []) if a]
        occasion = [o for o in (occasion or []) if o]
        personality = [p for p in (personality or []) if p]
        mask = self.country == country
        if price_min is not None:
            mask &= self.price >= price_min
        if price_max is not None:
            mask &= self.price <= price_max
        idx = np.where(mask)[0]
        if len(idx) == 0:
            return {"total": 0, "results": []}

        score = np.zeros(len(idx))
        why = [[] for _ in idx]

        # 1) text channel ------------------------------------------------
        selected = ([gender] if gender and gender != "unisex" else []) + age + occasion + personality
        text_query = normalize(q)
        pseudo = expand_query(selected, lang) if selected else ""
        full_query = f"{text_query} {text_query} {pseudo}".strip()
        if full_query:
            qv = l2(self._featurize([full_query]))
            cos = np.asarray(self.X[idx].dot(qv.T).todense()).ravel()
            score += WEIGHTS["text"] * cos * (2.0 if text_query else 1.0)

        # Free-text hints: "for my dad who loves fishing" -> male, fathers_day, outdoor
        hinted = {}
        if text_query:
            for label, hits in lexicon_scores(text_query).items():
                for facet, cols in self.label_cols.items():
                    if label in cols:
                        hinted.setdefault(facet, {})[label] = min(1.0, 0.4 * hits)

        # 2) facet channels ---------------------------------------------
        def facet_boost(facet, labels, weight, soft=None):
            nonlocal score
            cols = self.label_cols[facet]
            if labels:
                best = np.zeros(len(idx))
                for l in labels:
                    if l in cols:
                        s = self.S[facet][idx, cols[l]]
                        best = np.maximum(best, s)
                        for k in np.where(s >= 0.5)[0]:
                            why[k].append(l)
                score += weight * best
            for l, w in (soft or {}).items():
                s = self.S[facet][idx, cols[l]]
                score += weight * w * s
                for k in np.where(s >= 0.5)[0]:
                    why[k].append(l)

        if gender in ("female", "male"):
            cols = self.label_cols["gender"]
            s_sel = self.S["gender"][idx, cols[gender]]
            s_uni = self.S["gender"][idx, cols["unisex"]]
            other = "male" if gender == "female" else "female"
            s_oth = self.S["gender"][idx, cols[other]]
            score += WEIGHTS["gender"] * (np.maximum(s_sel, 0.7 * s_uni) - 0.8 * s_oth)
            for k in np.where(s_sel >= 0.5)[0]:
                why[k].append(gender)
        facet_boost("gender", [], WEIGHTS["gender"], hinted.get("gender"))
        facet_boost("age", age, WEIGHTS["age"], hinted.get("age"))
        facet_boost("occasion", occasion, WEIGHTS["occasion"], hinted.get("occasion"))
        facet_boost("personality", personality, WEIGHTS["personality"], hinted.get("personality"))

        # Nothing selected and nothing typed: show a varied, well-priced mix.
        if not selected and not text_query:
            rng = np.random.default_rng(7)
            score = rng.random(len(idx))

        order = np.argsort(-score)
        # Diversify: do not show the same concept twice in a row of results.
        seen, picked = {}, []
        for k in order:
            p = self.products[idx[k]]
            cid = p.get("concept_id", p["id"])
            if seen.get(cid, 0) >= 2:
                continue
            seen[cid] = seen.get(cid, 0) + 1
            picked.append(k)
        total = len(picked)
        picked = picked[offset:offset + limit]
        results = [self._render(self.products[idx[k]], float(score[k]), why[k], lang) for k in picked]
        return {"total": total, "results": results}

    def _render(self, p, score, why, lang):
        m = MERCHANT_BY_ID[p["merchant_id"]]
        seen = []
        for w in why:
            if w not in seen:
                seen.append(w)
        return {
            "id": p["id"],
            "title": p["title"],
            "description": p["description"],
            "price": p["price"],
            "price_text": format_price(p["price"], p["country"]),
            "currency": p["currency"],
            "merchant": m["name"],
            "merchant_domain": m["domain"],
            "image": p.get("image", ""),
            "emoji": p.get("emoji", "🎁"),
            "score": round(score, 3),
            "why": [UI_LABELS.get(w, {}).get(lang, w) for w in seen[:4]],
            "link": f"/go/{p['id']}",
        }


def facet_options(lang):
    return {facet: [{"id": l, "label": UI_LABELS[l].get(lang, l)} for l in labels] for facet, labels in FACETS.items()}
