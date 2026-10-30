"""Text augmentation shared by the seed builder and the trainer."""
from ..taxonomy import LEXICON

TEMPLATES = {
    "en": ["Perfect gift for {x}.", "A great {x} gift idea.", "Ideal for {x}.", "Makes a thoughtful present for {x}."],
    "de": ["Perfektes Geschenk für {x}.", "Tolle Geschenkidee für {x}.", "Ideal für {x}.", "Ein liebevolles Präsent für {x}."],
    "tr": ["{x} için mükemmel hediye.", "{x} için harika bir hediye fikri.", "{x} için ideal.", "{x} için düşünceli bir armağan."],
    "nl": ["Perfect cadeau voor {x}.", "Een leuk cadeau-idee voor {x}.", "Ideaal voor {x}.", "Een attent geschenk voor {x}."],
    "fr": ["Cadeau parfait pour {x}.", "Une belle idée cadeau pour {x}.", "Idéal pour {x}.", "Un présent attentionné pour {x}."],
}
NOISE = {
    "en": ["Free shipping.", "Available in black, navy and sand.", "Ships in a gift box.", "Backed by a 2-year warranty.", "Bestseller with 4.7 stars."],
    "de": ["Kostenloser Versand.", "Erhältlich in Schwarz, Navy und Sand.", "Lieferung in Geschenkbox.", "2 Jahre Garantie.", "Bestseller mit 4,7 Sternen."],
    "tr": ["Ücretsiz kargo.", "Siyah, lacivert ve kum renklerinde.", "Hediye kutusunda gönderilir.", "2 yıl garantili.", "4,7 yıldızlı çok satan."],
    "nl": ["Gratis verzending.", "Verkrijgbaar in zwart, navy en zand.", "Geleverd in geschenkdoos.", "2 jaar garantie.", "Bestseller met 4,7 sterren."],
    "fr": ["Livraison gratuite.", "Disponible en noir, marine et sable.", "Livré dans un coffret cadeau.", "Garantie 2 ans.", "Best-seller noté 4,7 étoiles."],
}
TITLE_PREFIX = {
    "en": ["", "", "Premium ", "Gift Set: ", "New "],
    "de": ["", "", "Premium ", "Geschenkset: ", "Neu: "],
    "tr": ["", "", "Premium ", "Hediye Seti: ", "Yeni "],
    "nl": ["", "", "Premium ", "Cadeauset: ", "Nieuw: "],
    "fr": ["", "", "Premium ", "Coffret cadeau : ", "Nouveau : "],
}


def augment(rng, concept, lang, cue_labels=None):
    """Return (title, description) with label-bearing phrases appended.
    `cue_labels` are extra labels (not in the concept) whose phrases are also
    injected, so the model learns that an explicit cue such as "fête des
    pères" implies the label regardless of product type."""
    title, desc = concept["text"][lang]
    labels = [concept["gender"]] + concept["age"] + concept["occasion"] + concept["personality"]
    labels = [l for l in labels if l != "unisex"] + list(cue_labels or [])
    extra = []
    for label in cue_labels or []:
        extra.append(rng.choice(TEMPLATES[lang]).format(x=rng.choice(LEXICON[label][lang])))
    for _ in range(rng.choice([1, 2, 2, 3])):
        label = rng.choice(labels)
        phrases = LEXICON[label][lang]
        extra.append(rng.choice(TEMPLATES[lang]).format(x=rng.choice(phrases)))
    if rng.random() < 0.6:
        extra.append(rng.choice(NOISE[lang]))
    rng.shuffle(extra)
    extra = [e[0].upper() + e[1:] for e in extra]
    title = rng.choice(TITLE_PREFIX[lang]) + title
    return title, desc + " " + " ".join(extra)


