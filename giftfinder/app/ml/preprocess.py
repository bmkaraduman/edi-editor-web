"""Language-agnostic text normalisation for the text-mining pipeline.

We fold accents (é->e, ş->s, ü->u ...) so that word and character n-grams
line up across the five languages and across sloppy merchant feeds that
omit diacritics. Stopwords for each language are removed from the word
channel only; the character channel keeps them (they carry morphology).
"""
import re
import unicodedata

_WS = re.compile(r"\s+")
_NONWORD = re.compile(r"[^a-z0-9 ]+")

STOPWORDS = {
    "en": "a an the and or of for with to in on at by from is are it its this that these those your you his her their our as be can has have will not".split(),
    "de": "der die das und oder für mit zu in auf an von ist sind es dein ihr ihre sein seine ein eine einen einem einer dem den des aus bei nach über um auch nicht wird als".split(),
    "tr": "ve veya için ile bir bu şu o da de ki mi mı mu mü her çok daha en gibi kadar olan olarak üzere sonra önce ya ama fakat ancak ise".split(),
    "nl": "de het een en of voor met te in op aan van is zijn het dit dat deze die je jouw jij zijn haar hun ons als ook niet wordt bij naar over om uit".split(),
    "fr": "le la les un une des et ou pour avec à au aux en dans sur de du d l est sont ce cette ces votre vos son sa ses leur leurs notre nos qui que ne pas plus par".split(),
}


def fold(text):
    """Lowercase and strip diacritics. Turkish dotless i is handled too."""
    text = text.replace("ı", "i").replace("İ", "i").replace("ß", "ss")
    for a, b in (("ł", "l"), ("Ł", "l"), ("ø", "o"), ("Ø", "o"), ("æ", "ae"), ("Æ", "ae"), ("œ", "oe"), ("Œ", "oe"), ("đ", "d")):
        text = text.replace(a, b)          # letters NFKD does not split (Polish, Danish, French)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def normalize(text):
    text = fold(text or "")
    text = _NONWORD.sub(" ", text)
    return _WS.sub(" ", text).strip()


from ..i18n import table as _i18n_table  # noqa: E402

STOPWORDS.update({lang: words.split() if isinstance(words, str) else list(words) for lang, words in _i18n_table("stopwords").items()})
_ALL_STOP = {fold(w) for ws in STOPWORDS.values() for w in ws}


def tokens(text, drop_stopwords=True):
    toks = normalize(text).split()
    if drop_stopwords:
        toks = [t for t in toks if t not in _ALL_STOP and len(t) > 1]
    return toks


def doc_text(title, description, brand="", category="", keywords="", category_path="", product_type=""):
    """Title and keywords are repeated so that they weigh more than the description."""
    return " ".join([normalize(title), normalize(title), normalize(keywords), normalize(keywords),
                     normalize(description), normalize(brand), normalize(category),
                     normalize(category_path), normalize(product_type)]).strip()


def product_doc(p):
    """doc_text for a catalog dict."""
    return doc_text(p["title"], p.get("description", ""), p.get("brand", ""), p.get("category", ""),
                    p.get("keywords", ""), p.get("category_path", ""), p.get("product_type", ""))
