"""Languages added after the first five (en, de, tr, nl, fr) live in app/i18n/<lang>.json,
one file per language with everything the site needs in it:

  ui            web UI strings (same keys as I18N.en in web/ui.js)
  consent       the 4 cookie-banner strings (web/analytics.js)
  ui_labels     filter label -> short text          -> taxonomy.UI_LABELS
  facet_titles  facet -> field title                -> taxonomy.FACET_TITLES
  lexicon       label -> keywords                   -> taxonomy.LEXICON
  stopwords     space separated                     -> ml.preprocess.STOPWORDS
  gift_words    the word for "gift"                 -> config.GIFT_WORDS
  augment       templates / noise / title_prefix    -> ml.augment (synthetic training text)
  rules         rule id -> keywords                 -> data.rules (added to that rule's patterns)

Adding a language = adding a file; nothing else to edit.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

LANGS = {}
for _path in sorted(glob.glob(os.path.join(HERE, "*.json"))):
    with open(_path, encoding="utf-8") as _f:
        _d = json.load(_f)
    LANGS[_d["lang"]] = _d


def table(key):
    """{lang: data[key]} for every added language."""
    return {lang: d[key] for lang, d in LANGS.items() if key in d}


GIFT_WORDS = {lang: [w.lower() for w in ws] for lang, ws in table("gift_words").items()}


def web_script():
    """JS that hands the added languages' UI and cookie-banner strings to web/ui.js and web/analytics.js."""
    return "window.I18N_EXTRA=%s;window.CONSENT_EXTRA=%s;" % (
        json.dumps(table("ui"), ensure_ascii=False), json.dumps(table("consent"), ensure_ascii=False))
