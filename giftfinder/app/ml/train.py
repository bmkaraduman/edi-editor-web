"""Train the facet classifiers on the labelled catalog.

Model: two TF-IDF channels (word 1-2 grams and char_wb 3-5 grams) stacked,
then one logistic-regression one-vs-rest head per facet. Character n-grams
make the model robust to the five languages and to unseen inflections;
word n-grams catch multi-word cues such as "fête des mères".

Artifacts are written to app/data/models/ and loaded by the search engine.
"""
import json
import os
import sys
import time

import numpy as np
from joblib import dump
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

import random

from ..config import COUNTRIES
from ..data.concepts import CONCEPTS
from ..taxonomy import FACETS, all_labels
from .augment import augment
from .preprocess import doc_text
from .weak_labels import lexicon_scores

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
MODELS = os.path.join(DATA, "models")
THRESHOLD = 0.4   # decision threshold for multi-label facets


def build_vectorizers():
    return {
        "word": TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=60000, sublinear_tf=True),
        "char": TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, max_features=120000, sublinear_tf=True),
    }


_LABELS = all_labels()


def lexicon_features(texts):
    """Dense lexicon-hit channel: one column per label, log-scaled."""
    M = np.zeros((len(texts), len(_LABELS)))
    for i, t in enumerate(texts):
        for label, hits in lexicon_scores(t).items():
            M[i, _LABELS.index(label)] = np.log1p(hits)
    return csr_matrix(M * 2.0)


def featurize(vecs, texts, fit=False):
    parts = []
    for v in vecs.values():
        parts.append(v.fit_transform(texts) if fit else v.transform(texts))
    parts.append(lexicon_features(texts))
    return hstack(parts).tocsr()


def synthetic_docs(n_per_lang=6, seed=3):
    """Extra augmented training docs straight from the concepts (not part of
    the catalog). Gives the classifier more phrasing per label."""
    rng = random.Random(seed)
    docs = []
    for concept in CONCEPTS:
        for cinfo in COUNTRIES.values():
            for _ in range(n_per_lang):
                # cue-consistent noise: add a foreign occasion/personality phrase
                # and its label, so explicit cues override product-type priors
                occ, per = list(concept["occasion"]), list(concept["personality"])
                cues = []
                if rng.random() < 0.5:
                    l = rng.choice([x for x in FACETS["occasion"] if x not in occ]); occ.append(l); cues.append(l)
                if rng.random() < 0.35:
                    l = rng.choice([x for x in FACETS["personality"] if x not in per]); per.append(l); cues.append(l)
                title, desc = augment(rng, concept, cinfo["lang"], cue_labels=cues)
                docs.append({"concept_id": concept["id"], "title": title, "description": desc,
                             "labels": {"gender": [concept["gender"]], "age": concept["age"],
                                        "occasion": occ, "personality": per}})
    return docs


def train(catalog_path=None, out_dir=MODELS, test_size=0.2, seed=42):
    catalog_path = catalog_path or os.path.join(DATA, "catalog.json")
    with open(catalog_path, encoding="utf-8") as f:
        products = json.load(f)
    labelled = [p for p in products if p.get("labels") and p.get("source") in ("seed", "manual")]
    print(f"{len(labelled)} labelled products of {len(products)} total")
    labelled += synthetic_docs()
    print(f"{len(labelled)} docs after synthetic augmentation")

    texts = [doc_text(p["title"], p["description"], p.get("brand", ""), p.get("category", "")) for p in labelled]
    concept = [p.get("concept_id") or p["id"] for p in labelled]

    # Split by concept so that augmentations of one concept never leak into test.
    uniq = sorted(set(concept))
    train_c, test_c = train_test_split(uniq, test_size=test_size, random_state=seed)
    train_c = set(train_c)
    tr_idx = [i for i, c in enumerate(concept) if c in train_c]
    te_idx = [i for i, c in enumerate(concept) if c not in train_c]

    vecs = build_vectorizers()
    X_tr = featurize(vecs, [texts[i] for i in tr_idx], fit=True)
    X_te = featurize(vecs, [texts[i] for i in te_idx])
    print(f"features: {X_tr.shape[1]}  train docs: {X_tr.shape[0]}  test docs: {X_te.shape[0]}")

    heads, report = {}, {}
    for facet, labels in FACETS.items():
        mlb = MultiLabelBinarizer(classes=labels)
        Y = mlb.fit_transform([labelled[i]["labels"].get(facet, []) for i in range(len(labelled))])
        clf = OneVsRestClassifier(LogisticRegression(C=8.0, max_iter=3000, class_weight="balanced"), n_jobs=-1)
        t0 = time.time()
        clf.fit(X_tr, Y[tr_idx])
        P = clf.predict_proba(X_te)
        pred = (P >= THRESHOLD).astype(int)
        if facet == "gender":
            pred = np.zeros_like(P, dtype=int)
            pred[np.arange(len(P)), P.argmax(1)] = 1
        rep = {
            "micro_f1": round(f1_score(Y[te_idx], pred, average="micro", zero_division=0), 3),
            "macro_f1": round(f1_score(Y[te_idx], pred, average="macro", zero_division=0), 3),
            "precision": round(precision_score(Y[te_idx], pred, average="micro", zero_division=0), 3),
            "recall": round(recall_score(Y[te_idx], pred, average="micro", zero_division=0), 3),
            "seconds": round(time.time() - t0, 1),
        }
        report[facet] = rep
        print(f"  {facet:12s} micro-F1 {rep['micro_f1']}  macro-F1 {rep['macro_f1']}  P {rep['precision']}  R {rep['recall']}")
        heads[facet] = (mlb, clf)

    # Refit on everything for the production model.
    vecs = build_vectorizers()
    X_all = featurize(vecs, texts, fit=True)
    final = {}
    for facet, labels in FACETS.items():
        mlb = MultiLabelBinarizer(classes=labels)
        Y = mlb.fit_transform([p["labels"].get(facet, []) for p in labelled])
        clf = OneVsRestClassifier(LogisticRegression(C=8.0, max_iter=3000, class_weight="balanced"), n_jobs=-1)
        clf.fit(X_all, Y)
        final[facet] = {"classes": labels, "clf": clf}

    os.makedirs(out_dir, exist_ok=True)
    dump({"vectorizers": vecs, "heads": final}, os.path.join(out_dir, "facet_model.joblib"), compress=3)
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump({"trained_at": time.strftime("%Y-%m-%d %H:%M:%S"), "n_labelled": len(labelled),
                   "n_features": int(X_all.shape[1]), "holdout": report}, f, indent=2)
    print(f"saved model to {out_dir}")
    return report


if __name__ == "__main__":
    train(sys.argv[1] if len(sys.argv) > 1 else None)
