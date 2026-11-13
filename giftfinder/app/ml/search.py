"""The gift search engine.

Ranking = text relevance (TF-IDF cosine between the visitor's query and the
product's title + keywords + description) + facet affinity (classifier
probability, or the stored label when one exists, for every facet the visitor
selected), damped by the product's giftability prior. When the visitor types
nothing, the selected facets are expanded into a pseudo-query in the country's
language through the lexicon, so pure "filter" searches still benefit from the
text index.

House rules applied here:
  * a product without a picture is never shown (seed demo listings stay visible
    only in a country that has no real products yet);
  * the same product is never shown twice: feed variants (sizes, colours, 2 ml /
    5 ml decants) and the seed's merchant copies of one concept collapse to one;
  * feed rows that no rule or text marks as gift-like (office supplies, patch
    cables) are hidden from filter-only searches and damped in text searches.
"""
import json
import os
import re

import numpy as np
from joblib import load
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize as l2

from ..config import COUNTRIES, GIFT_WORDS, MERCHANT_BY_ID, format_price
from ..data.rules import GIFT_FLOOR
from ..taxonomy import FACETS, UI_LABELS
from .labeling import rule_category
from .preprocess import doc_text, normalize, product_doc
from .train import THRESHOLD, lexicon_features
from .weak_labels import expand_query, lexicon_scores

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

WEIGHTS = {"text": 1.0, "gender": 0.9, "age": 0.6, "occasion": 0.8, "personality": 1.0}
# How much a stored label is trusted over the classifier: hand labels fully, labels
# from a category rule almost, lexicon/classifier labels of raw feed rows less, so
# curated items win ties and a raw feed item never claims a perfect fit.
LABEL_TRUST = {"seed": 1.0, "manual": 1.0}
RULE_LABEL_TRUST = 0.9
FEED_LABEL_TRUST = 0.75

_VARIANT_SPLIT = re.compile(r"\s+[–|\-/]\s+|\s*\|\s*|,\s+")
_VARIANT_TOKEN = re.compile(r"^(\d+([.,]\d+)?(ml|cl|l|g|kg|mm|cm|m|w|v|a|er|x|st|stk|pcs|pack|paar|pair)?|x?s|m|l|xl|xxl|xxxl|\d+-\d+|\d+/\d+|gr(o|ö)(ss|ß)e|size|farbe|colou?r|black|white|schwarz|weiss|blau|blue|rot|red|grau|grey|gray|beige|braun|brown|grun|green|gelb|yellow|rosa|pink|navy|marine|oliv|olive|silber|silver|gold)$")


def _stem_tokens(p):
    stem = _VARIANT_SPLIT.split(p["title"], maxsplit=1)[0]
    return [t for t in normalize(stem).split() if not _VARIANT_TOKEN.match(t)]


def dedupe_key(p):
    """Collapse variants of one product to a single key.

    Seed copies share a concept; feed titles like "Socken aus Baumwolle – Beige –
    43-46" or "Dior Homme – 8 ml Parfüm-Abfüllung" are cut at the first variant
    separator and stripped of size/colour/volume tokens."""
    if p.get("concept_id"):
        return f"concept:{p['concept_id']}"
    return f"{p['merchant_id']}:{' '.join(_stem_tokens(p)[:3])}"


def dedupe_keys(p):
    """All keys under which a product counts as "already shown": its variant stem,
    its picture (variants often share one photo), its family (shop + first two
    words: "Chateau Purcari …", "Personalisierte Foto …", "Police Herren …") and its
    full stem across shops (resellers listing one article under the same title)."""
    keys = {dedupe_key(p)}
    if p.get("image"):
        keys.add("img:" + p["image"])
    if not p.get("concept_id"):
        toks = _stem_tokens(p)
        keys.add(f"fam:{p['merchant_id']}:{' '.join(toks[:2])}")
        if len(toks) >= 3:            # the same article sold by two shops under one title
            keys.add("same:" + " ".join(toks))
    return keys


MERCHANT_CAP = 4      # at most this many listings of one shop per block of 12 results
BLOCK = 12
# Near-duplicate test within one shop, for listings the keys above did not catch
# ("Weihnachtsgeschenkset Herren" vs "Weihnacht Geschenkset Herren", "Sterlingsilber
# Personalisierte Foto Projektion Kette" vs "925 Sterling Silber Foto Projektion
# Halskette"): titles share character n-grams, or the whole listing is nearly identical.
# Same-shop descriptions are templated, so the full-text bar is high.
NEAR_TITLE = 0.33
NEAR_FULL = 0.9
HIDDEN_FILE = os.path.join(DATA, "hidden.jsonl")


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
        self.pos = {p["id"]: i for i, p in enumerate(self.products)}
        self._index()

    # ------------------------------------------------------------ indexing
    def _featurize(self, texts):
        return hstack([v.transform(texts) for v in self.vecs.values()] + [lexicon_features(texts)]).tocsr()

    def _index(self):
        texts = [product_doc(p) for p in self.products]
        Xraw = self._featurize(texts)
        self.X = l2(Xraw)          # unit vectors for cosine retrieval
        self.label_cols = {}
        self.S = {}
        heads = dict(self.heads)
        heads.setdefault("category", None)     # a model trained before the facet: rules and stored labels only
        for facet, head in heads.items():
            classes = head["classes"] if head else FACETS[facet]
            P = head["clf"].predict_proba(Xraw) if head else np.zeros((len(self.products), len(classes)))
            # stored labels override the classifier where they exist
            for i, p in enumerate(self.products):
                given = p.get("labels", {}).get(facet)
                if facet == "category" and not given and p.get("source", "feed") not in LABEL_TRUST:
                    # rows ingested before the category facet: the rules still know
                    cat = rule_category(p)
                    given = [cat] if cat else None
                if given:
                    trust = LABEL_TRUST.get(p.get("source", "feed"), RULE_LABEL_TRUST if p.get("rules") else FEED_LABEL_TRUST)
                    row = np.zeros(len(classes))
                    for l in given:
                        if l in classes:
                            row[classes.index(l)] = trust
                    P[i] = np.maximum(P[i] * 0.5, row)
            self.S[facet] = P
            self.label_cols[facet] = {l: j for j, l in enumerate(classes)}
        self.country = np.array([p["country"] for p in self.products])
        self.price = np.array([float(p["price"]) for p in self.products])
        self.gifty = np.array([self._giftiness(p, t) for p, t in zip(self.products, texts)])
        # Rule: no picture, no listing. Seed demo rows (emoji only) remain in a
        # country until that country has real, pictured products.
        real = {p["country"] for p in self.products if p.get("image") and p.get("source") not in LABEL_TRUST}
        self.real_countries = real
        self.visible = np.array([bool(p.get("image")) or (p.get("source") in LABEL_TRUST and p["country"] not in real)
                                 for p in self.products])
        self.keys = [dedupe_keys(p) for p in self.products]
        self.merchant = [p["merchant_id"] for p in self.products]
        titles = [normalize(p["title"]) for p in self.products]
        self.T = l2(TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True).fit_transform(titles))
        # products reported by the browser as having a picture that no longer loads
        self.hidden = set()
        if os.path.exists(HIDDEN_FILE):
            with open(HIDDEN_FILE, encoding="utf-8") as f:
                self.hidden = {json.loads(line)["id"] for line in f if line.strip()}
        for pid in self.hidden:
            if pid in self.pos:
                self.visible[self.pos[pid]] = False

    def hide(self, product_id):
        """Hide a product whose picture failed to load in a visitor's browser (persisted)."""
        if product_id not in self.pos or product_id in self.hidden:
            return False
        self.hidden.add(product_id)
        self.visible[self.pos[product_id]] = False
        try:
            with open(HIDDEN_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": product_id}) + "\n")
        except OSError:
            pass
        return True

    @staticmethod
    def _giftiness(p, text):
        if p.get("source", "feed") in LABEL_TRUST:
            return 1.0
        g = p.get("gift")
        words = GIFT_WORDS.get(p.get("lang", "en"), []) + GIFT_WORDS["en"]
        says_gift = any(w in text for w in words)
        if g is None:
            return 0.8 if says_gift else 0.4
        return max(float(g), 0.8) if says_gift and g >= GIFT_FLOOR else float(g)

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
            elif facet == "category":
                out[facet] = [classes[int(P.argmax())]] if P.max() >= 0.5 else []
            else:
                picked = [classes[j] for j in np.argsort(-P) if P[j] >= threshold][:3]
                out[facet] = picked
        return out

    def _rank(self, country, q="", gender=None, age=(), occasion=(), personality=(),
              price_min=None, price_max=None, exclude_key=None, allow_hidden=False, category=()):
        """Return (idx, score, why, match) over the visible products of a country."""
        lang = COUNTRIES[country]["lang"]
        mask = (self.country == country) & self.visible
        if price_min is not None:
            mask &= self.price >= price_min
        if price_max is not None:
            mask &= self.price <= price_max
        text_query = normalize(q)
        selected = ([gender] if gender and gender != "unisex" else []) + list(age) + list(occasion) + list(personality)
        # Category (advanced search) is a hard filter: "only furniture", "only perfume".
        category = [c for c in category if c in self.label_cols.get("category", {})]
        in_cat = None
        if category:
            in_cat = np.zeros(len(self.products), dtype=bool)
            for c in category:
                in_cat |= self.S["category"][:, self.label_cols["category"][c]] >= 0.5
            mask &= in_cat
        if not text_query and not allow_hidden and not category:
            mask &= self.gifty >= GIFT_FLOOR      # office stock only surfaces through a typed search;
                                                  # picking a category is asking for it (a 3-seater sofa under Furniture)
        idx = np.where(mask)[0]
        if len(idx) == 0:
            return idx, np.zeros(0), [], None

        score = np.zeros(len(idx))
        why = [[] for _ in idx]
        match_parts = []   # per selected facet: best affinity, averaged into the match badge

        # 1) text channel ------------------------------------------------
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
                match_parts.append(best)
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
            match_parts.append(np.maximum(s_sel, 0.7 * s_uni))
            for k in np.where(s_sel >= 0.5)[0]:
                why[k].append(gender)
        facet_boost("gender", [], WEIGHTS["gender"], hinted.get("gender"))
        facet_boost("age", list(age), WEIGHTS["age"], hinted.get("age"))
        facet_boost("occasion", list(occasion), WEIGHTS["occasion"], hinted.get("occasion"))
        facet_boost("personality", list(personality), WEIGHTS["personality"], hinted.get("personality"))

        # 3) giftability --------------------------------------------------
        if category:
            cols = self.label_cols["category"]
            per_cat = np.array([self.S["category"][idx, cols[c]] for c in category])
            cat_s = per_cat.max(axis=0)
            for k, j in enumerate(per_cat.argmax(axis=0)):
                why[k].insert(0, category[int(j)])
        if category and not selected and not text_query:
            # only a category picked: the whole category, most gift-like first
            rng = np.random.default_rng(7)
            score = cat_s * (0.3 + 0.7 * self.gifty[idx]) + 0.15 * rng.random(len(idx))
        elif not selected and not text_query:
            # Nothing selected and nothing typed: a varied mix of clearly gift-like items.
            rng = np.random.default_rng(7)
            score = rng.random(len(idx)) * np.where(self.gifty[idx] >= 0.5, self.gifty[idx], 0.0)
        else:
            score *= 0.3 + 0.7 * self.gifty[idx]

        match = (np.mean(match_parts, axis=0) * 100).round() if match_parts else None
        return idx, score, why, match

    def _near_duplicate(self, gi, same_shop):
        """Is product gi a near-duplicate of any already picked product of its shop?"""
        if not same_shop:
            return False
        if (self.T[gi].dot(self.T[same_shop].T).toarray() >= NEAR_TITLE).any():
            return True
        return (self.X[gi].dot(self.X[same_shop].T).toarray() >= NEAR_FULL).any()

    def _pick(self, idx, order, exclude_keys=(), need=None):
        """Order -> positions: never two listings of the same product or family, and
        no shop may fill more than MERCHANT_CAP slots of any 12-result block (its
        surplus moves down the list instead of being dropped). The similarity test
        runs for the first `need` picks (what the page shows); beyond that only the
        cheap key test counts, so `total` is a slight over-estimate."""
        seen, picked, deferred = set(exclude_keys), [], []
        per_merchant, shown = {}, {}
        need = len(order) if need is None else need
        for k in order:
            gi = idx[k]
            keys = self.keys[gi]
            if keys & seen:
                continue
            m = self.merchant[gi]
            if len(picked) < need and self._near_duplicate(gi, shown.get(m, [])):
                continue
            seen |= keys
            block = len(picked) // BLOCK
            if per_merchant.get((m, block), 0) >= MERCHANT_CAP:
                deferred.append(k)
                continue
            per_merchant[(m, block)] = per_merchant.get((m, block), 0) + 1
            picked.append(k)
            shown.setdefault(m, []).append(int(gi))
        return picked + deferred

    def search(self, country, q="", gender=None, age=None, occasion=None, personality=None,
               price_min=None, price_max=None, limit=24, offset=0, sort="relevance", category=None):
        country = country.upper()
        if country not in COUNTRIES:
            raise ValueError("unknown country")
        lang = COUNTRIES[country]["lang"]
        age = [a for a in (age or []) if a]
        occasion = [o for o in (occasion or []) if o]
        personality = [p for p in (personality or []) if p]
        category = [c for c in (category or []) if c]
        idx, score, why, match = self._rank(country, q, gender, age, occasion, personality, price_min, price_max, category=category)
        demo = country not in self.real_countries
        if len(idx) == 0:
            return {"total": 0, "demo": demo, "results": []}
        if sort == "price_asc":
            order = np.lexsort((-score, self.price[idx]))
        elif sort == "price_desc":
            order = np.lexsort((-score, -self.price[idx]))
        else:
            order = np.argsort(-score)
        picked = self._pick(idx, order, need=offset + limit + BLOCK)
        total = len(picked)
        picked = picked[offset:offset + limit]
        results = [self._render(self.products[idx[k]], float(score[k]), why[k], lang,
                                None if match is None else int(match[k])) for k in picked]
        return {"total": total, "demo": demo, "results": results}

    def product(self, product_id, similar=8):
        """Full detail of one product plus similar, differently-keyed products of its country."""
        p = self.by_id.get(product_id)
        if p is None:
            return None
        lang = COUNTRIES[p["country"]]["lang"]
        d = self._render(p, 0.0, [], lang)
        d.update({
            "country": p["country"], "lang": lang,
            "images": [p["image"]] + [u for u in p.get("images", []) if u] if p.get("image") else [],
            "brand": p.get("brand", ""), "category": p.get("category_path") or p.get("category", ""),
            "product_type": p.get("product_type", ""), "keywords": [k.strip() for k in re.split(r"[,;>|]", p.get("keywords", "")) if k.strip()],
            "rrp": p.get("rrp") or None, "rrp_text": format_price(p["rrp"], p["country"]) if p.get("rrp") else None,
            "details": p.get("details", {}), "rules": p.get("rules", []), "source": p.get("source", "feed"),
            "labels": {facet: [{"id": l, "label": UI_LABELS.get(l, {}).get(lang, l)} for l in ls]
                       for facet, ls in p.get("labels", {}).items() if ls and not (facet == "gender" and ls == ["unisex"])},
        })
        # similar: pure text similarity on the product's own strong text (title, keywords,
        # category, type), same country; the facet channels would pull in "anything for him"
        query = " ".join([p["title"], p.get("keywords", ""), p.get("category", ""), p.get("product_type", "")])
        idx, score, why, _ = self._rank(p["country"], q=query)
        sims = []
        if len(idx):
            me = self.keys[self.pos[p["id"]]]
            for k in self._pick(idx, np.argsort(-score), exclude_keys=me, need=similar + BLOCK):
                sp = self.products[idx[k]]
                if sp["id"] == p["id"]:
                    continue
                sims.append(self._render(sp, float(score[k]), why[k], lang))
                if len(sims) >= similar:
                    break
        d["similar"] = sims
        return d

    def _render(self, p, score, why, lang, match=None):
        m = MERCHANT_BY_ID.get(p["merchant_id"]) or {"name": p.get("merchant_name") or "Shop", "domain": ""}
        seen = []
        for w in why:
            if w not in seen:
                seen.append(w)
        return {
            "id": p["id"],
            "title": p["title"],
            "description": p.get("details", {}).get("short_description") or p["description"],
            "price": p["price"],
            "price_text": format_price(p["price"], p["country"]),
            "rrp_text": format_price(p["rrp"], p["country"]) if p.get("rrp") else None,
            "currency": p["currency"],
            "merchant": m["name"],
            "merchant_domain": m["domain"],
            "brand": p.get("brand", ""),
            "image": p.get("image", ""),
            "gallery": 1 + len([u for u in p.get("images", []) if u]) if p.get("image") else 0,
            "emoji": p.get("emoji", "🎁"),
            "score": round(score, 3),
            "match": match,
            "why": [UI_LABELS.get(w, {}).get(lang, w) for w in seen[:4]],
            "link": f"/go/{p['id']}",
            "detail": f"/p/{p['id']}",
        }


def facet_options(lang):
    return {facet: [{"id": l, "label": UI_LABELS[l].get(lang, l)} for l in labels] for facet, labels in FACETS.items()}
