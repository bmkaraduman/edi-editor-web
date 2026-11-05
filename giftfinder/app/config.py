"""Countries, merchants and affiliate programmes.

Every merchant listed here runs a public affiliate programme. Credentials are
read from environment variables so that nothing secret lives in the repo.
When a credential is missing the merchant still works: links are built
without the tracking parameter, so the site degrades gracefully.

Link templates understand these placeholders:
  {url}      product URL, percent-encoded
  {raw_url}  product URL, as is
  {q}        search query, percent-encoded (used for seed/search-page links)
  {tag}, {affid}, {site_id}, {mid} ... taken from the merchant's `params`
"""
import os
from urllib.parse import quote_plus


def _load_dotenv():
    """Read giftfinder/.env (KEY=value lines) without overriding the real environment."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

from .i18n import GIFT_WORDS as _I18N_GIFT_WORDS  # noqa: E402  (languages added from app/i18n/*.json)

# "gift" in every site language; used to prefer gift-like rows when sampling feeds and mixing the home page
GIFT_WORDS = {"en": ["gift"], "de": ["geschenk"], "tr": ["hediye"], "nl": ["cadeau", "geschenk"], "fr": ["cadeau"]}
GIFT_WORDS.update(_I18N_GIFT_WORDS)

# Google Analytics 4 measurement id of the giftdetect.com web stream (empty disables analytics).
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "G-XN9SC9S3K2")

# Countries shown on the site. The others keep their config (merchants, lexicon, seeds)
# and come back by listing them here or in ACTIVE_COUNTRIES=US,DE,TR.
ACTIVE_COUNTRIES = [c.strip().upper() for c in os.environ.get("ACTIVE_COUNTRIES", "DE,NL,FR,US,GB,IE,CA,AU,AT,CH,BE,PL,IT,ES,SE,FI,DK,BR,RO").split(",") if c.strip()]

COUNTRIES = {
    "US": {"name": "United States", "lang": "en", "currency": "USD", "symbol": "$", "flag": "🇺🇸", "usd_rate": 1.0, "locale": "en-US"},
    "DE": {"name": "Deutschland", "lang": "de", "currency": "EUR", "symbol": "€", "flag": "🇩🇪", "usd_rate": 0.92, "locale": "de-DE"},
    "TR": {"name": "Türkiye", "lang": "tr", "currency": "TRY", "symbol": "₺", "flag": "🇹🇷", "usd_rate": 41.0, "locale": "tr-TR"},
    "NL": {"name": "Nederland", "lang": "nl", "currency": "EUR", "symbol": "€", "flag": "🇳🇱", "usd_rate": 0.92, "locale": "nl-NL"},
    "FR": {"name": "France", "lang": "fr", "currency": "EUR", "symbol": "€", "flag": "🇫🇷", "usd_rate": 0.92, "locale": "fr-FR"},
    "GB": {"name": "United Kingdom", "lang": "en", "currency": "GBP", "symbol": "£", "flag": "🇬🇧", "usd_rate": 0.79, "locale": "en-GB"},
    "IE": {"name": "Ireland", "lang": "en", "currency": "EUR", "symbol": "€", "flag": "🇮🇪", "usd_rate": 0.92, "locale": "en-IE"},
    "CA": {"name": "Canada", "lang": "en", "currency": "CAD", "symbol": "CA$", "flag": "🇨🇦", "usd_rate": 1.37, "locale": "en-CA"},
    "AU": {"name": "Australia", "lang": "en", "currency": "AUD", "symbol": "A$", "flag": "🇦🇺", "usd_rate": 1.52, "locale": "en-AU"},
    "AT": {"name": "Österreich", "lang": "de", "currency": "EUR", "symbol": "€", "flag": "🇦🇹", "usd_rate": 0.92, "locale": "de-AT"},
    "CH": {"name": "Schweiz", "lang": "de", "currency": "CHF", "symbol": "CHF", "flag": "🇨🇭", "usd_rate": 0.88, "locale": "de-CH"},
    "BE": {"name": "België", "lang": "nl", "currency": "EUR", "symbol": "€", "flag": "🇧🇪", "usd_rate": 0.92, "locale": "nl-BE"},
    "PL": {"name": "Polska", "lang": "pl", "currency": "PLN", "symbol": "zł", "flag": "🇵🇱", "usd_rate": 3.9, "locale": "pl-PL"},
    "IT": {"name": "Italia", "lang": "it", "currency": "EUR", "symbol": "€", "flag": "🇮🇹", "usd_rate": 0.92, "locale": "it-IT"},
    "ES": {"name": "España", "lang": "es", "currency": "EUR", "symbol": "€", "flag": "🇪🇸", "usd_rate": 0.92, "locale": "es-ES"},
    "SE": {"name": "Sverige", "lang": "sv", "currency": "SEK", "symbol": "kr", "flag": "🇸🇪", "usd_rate": 10.5, "locale": "sv-SE"},
    "FI": {"name": "Suomi", "lang": "fi", "currency": "EUR", "symbol": "€", "flag": "🇫🇮", "usd_rate": 0.92, "locale": "fi-FI"},
    "DK": {"name": "Danmark", "lang": "da", "currency": "DKK", "symbol": "kr.", "flag": "🇩🇰", "usd_rate": 6.9, "locale": "da-DK"},
    "BR": {"name": "Brasil", "lang": "pt", "currency": "BRL", "symbol": "R$", "flag": "🇧🇷", "usd_rate": 5.4, "locale": "pt-BR"},
    "RO": {"name": "România", "lang": "ro", "currency": "RON", "symbol": "lei", "flag": "🇷🇴", "usd_rate": 4.6, "locale": "ro-RO"},
}


def _env(name, default=""):
    return os.environ.get(name, default)


# Affiliate networks. `click` wraps a merchant URL into a tracked deep link.
NETWORKS = {
    "amazon": {  # Amazon Associates / PartnerNet / Partenaires / Ortaklık
        "click": "{raw_url}{sep}tag={tag}",
        "params": lambda cc: {"tag": _env(f"AMAZON_TAG_{cc}", _env("AMAZON_TAG"))},
    },
    "awin": {  # Awin (Etsy, Otto, Fnac, Cdiscount, Coolblue, Decathlon, Thalia ...)
        "click": "https://www.awin1.com/cread.php?awinmid={mid}&awinaffid={affid}&ued={url}",
        "params": lambda cc: {"affid": _env("AWIN_AFFILIATE_ID")},
    },
    "bol": {  # bol.com Partnerprogramma
        "click": "https://partner.bol.com/click/click?p=2&t=url&s={site_id}&url={url}&f=TXL",
        "params": lambda cc: {"site_id": _env("BOL_SITE_ID")},
    },
    "impact": {  # impact.com (Walmart, Target, Uncommon Goods, Wehkamp ...)
        "click": "{raw_url}{sep}irclickid={affid}&irgwc=1",
        "params": lambda cc: {"affid": _env("IMPACT_CLICK_ID")},
    },
    "daisycon": {  # Daisycon (NL / BE)
        "click": "https://ds1.nl/c/?si={site_id}&li={mid}&wi={affid}&ws=&dl={url}",
        "params": lambda cc: {"site_id": _env("DAISYCON_SITE_ID"), "affid": _env("DAISYCON_WEBSITE_ID")},
    },
    "gelirortaklari": {  # Gelirortakları (Hepsiburada, Çiçeksepeti, n11 ...)
        "click": "https://www.gelirortaklari.com/click?mid={mid}&aid={affid}&url={url}",
        "params": lambda cc: {"affid": _env("GELIRORTAKLARI_ID")},
    },
    "trendyol": {  # Trendyol Ortaklık Programı (deep link with partner id)
        "click": "{raw_url}{sep}utm_source=affiliate&utm_medium=partner&pid={affid}",
        "params": lambda cc: {"affid": _env("TRENDYOL_PARTNER_ID")},
    },
    "none": {"click": "{raw_url}", "params": lambda cc: {}},
}

# Merchants per country. `fit` (optional) lists the personalities a merchant
# plausibly stocks; the seed builder only places matching concepts there.
# `search` is a real search URL on the merchant site;
# seed products and any product without a deep URL link there, so clicks are
# still monetised through the network's click wrapper.
MERCHANTS = {
    "US": [
        {"id": "amazon_us", "name": "Amazon", "network": "amazon", "domain": "amazon.com", "search": "https://www.amazon.com/s?k={q}", "mid": ""},
        {"id": "etsy_us", "fit": ["artist", "homebody", "fashion", "maker", "pet_lover", "wellness", "foodie", "coffee_tea", "gardener", "bookworm", "music", "traveler"], "name": "Etsy", "network": "awin", "domain": "etsy.com", "search": "https://www.etsy.com/search?q={q}", "mid": "6220"},
        {"id": "uncommongoods", "name": "Uncommon Goods", "network": "impact", "domain": "uncommongoods.com", "search": "https://www.uncommongoods.com/search?keywords={q}", "mid": ""},
        {"id": "target", "name": "Target", "network": "impact", "domain": "target.com", "search": "https://www.target.com/s?searchTerm={q}", "mid": ""},
        {"id": "walmart", "name": "Walmart", "network": "impact", "domain": "walmart.com", "search": "https://www.walmart.com/search?q={q}", "mid": ""},
    ],
    "DE": [
        {"id": "amazon_de", "name": "Amazon.de", "network": "amazon", "domain": "amazon.de", "search": "https://www.amazon.de/s?k={q}", "mid": ""},
        {"id": "otto", "name": "OTTO", "network": "awin", "domain": "otto.de", "search": "https://www.otto.de/suche/{q}/", "mid": "14336"},
        {"id": "etsy_de", "fit": ["artist", "homebody", "fashion", "maker", "pet_lover", "wellness", "foodie", "coffee_tea", "gardener", "bookworm", "music", "traveler"], "name": "Etsy", "network": "awin", "domain": "etsy.com", "search": "https://www.etsy.com/de/search?q={q}", "mid": "6220"},
        {"id": "thalia", "fit": ["bookworm", "homebody", "artist", "music", "maker"], "name": "Thalia", "network": "awin", "domain": "thalia.de", "search": "https://www.thalia.de/suche?sq={q}", "mid": "9208"},
        {"id": "douglas", "fit": ["wellness", "fashion", "homebody"], "name": "Douglas", "network": "awin", "domain": "douglas.de", "search": "https://www.douglas.de/de/search?query={q}", "mid": "13063"},
    ],
    "TR": [
        {"id": "trendyol", "name": "Trendyol", "network": "trendyol", "domain": "trendyol.com", "search": "https://www.trendyol.com/sr?q={q}", "mid": ""},
        {"id": "hepsiburada", "name": "Hepsiburada", "network": "gelirortaklari", "domain": "hepsiburada.com", "search": "https://www.hepsiburada.com/ara?q={q}", "mid": "hepsiburada"},
        {"id": "amazon_tr", "name": "Amazon.com.tr", "network": "amazon", "domain": "amazon.com.tr", "search": "https://www.amazon.com.tr/s?k={q}", "mid": ""},
        {"id": "ciceksepeti", "fit": ["homebody", "foodie", "wellness", "gardener", "coffee_tea"], "name": "Çiçeksepeti", "network": "gelirortaklari", "domain": "ciceksepeti.com", "search": "https://www.ciceksepeti.com/arama?query={q}", "mid": "ciceksepeti"},
        {"id": "n11", "name": "n11", "network": "gelirortaklari", "domain": "n11.com", "search": "https://www.n11.com/arama?q={q}", "mid": "n11"},
    ],
    "NL": [
        {"id": "bol", "name": "bol.com", "network": "bol", "domain": "bol.com", "search": "https://www.bol.com/nl/nl/s/?searchtext={q}", "mid": ""},
        {"id": "amazon_nl", "name": "Amazon.nl", "network": "amazon", "domain": "amazon.nl", "search": "https://www.amazon.nl/s?k={q}", "mid": ""},
        {"id": "coolblue", "fit": ["tech", "gamer", "music", "fitness", "coffee_tea"], "name": "Coolblue", "network": "awin", "domain": "coolblue.nl", "search": "https://www.coolblue.nl/zoeken?query={q}", "mid": "17636"},
        {"id": "etsy_nl", "fit": ["artist", "homebody", "fashion", "maker", "pet_lover", "wellness", "foodie", "coffee_tea", "gardener", "bookworm", "music", "traveler"], "name": "Etsy", "network": "awin", "domain": "etsy.com", "search": "https://www.etsy.com/nl/search?q={q}", "mid": "6220"},
        {"id": "wehkamp", "fit": ["fashion", "homebody", "tech"], "name": "Wehkamp", "network": "daisycon", "domain": "wehkamp.nl", "search": "https://www.wehkamp.nl/zoeken/?q={q}", "mid": "wehkamp"},
    ],
    "FR": [
        {"id": "amazon_fr", "name": "Amazon.fr", "network": "amazon", "domain": "amazon.fr", "search": "https://www.amazon.fr/s?k={q}", "mid": ""},
        {"id": "fnac", "fit": ["tech", "gamer", "bookworm", "music", "maker"], "name": "Fnac", "network": "awin", "domain": "fnac.com", "search": "https://www.fnac.com/SearchResult/ResultList.aspx?Search={q}", "mid": "4329"},
        {"id": "cdiscount", "name": "Cdiscount", "network": "awin", "domain": "cdiscount.com", "search": "https://www.cdiscount.com/search/10/{q}.html", "mid": "7925"},
        {"id": "etsy_fr", "fit": ["artist", "homebody", "fashion", "maker", "pet_lover", "wellness", "foodie", "coffee_tea", "gardener", "bookworm", "music", "traveler"], "name": "Etsy", "network": "awin", "domain": "etsy.com", "search": "https://www.etsy.com/fr/search?q={q}", "mid": "6220"},
        {"id": "natureetdecouvertes", "fit": ["outdoor", "gardener", "wellness", "maker", "artist", "homebody"], "name": "Nature & Découvertes", "network": "awin", "domain": "natureetdecouvertes.com", "search": "https://www.natureetdecouvertes.com/recherche?q={q}", "mid": "6778"},
    ],
}

# Countries served only by combined feeds have no hand-listed merchants.
for _cc in COUNTRIES:
    MERCHANTS.setdefault(_cc, [])
MERCHANT_BY_ID = {m["id"]: dict(m, country=cc) for cc, ms in MERCHANTS.items() for m in ms}


def affiliate_link(merchant_id, product_url=None, query=None):
    """Build a tracked outbound link for a merchant.

    Falls back to the merchant's search page when no product URL exists.
    """
    m = MERCHANT_BY_ID.get(merchant_id)
    if m is None:              # merchant known only from a feed: its URL is already tracked
        return product_url or ""
    raw = product_url or m["search"].format(q=quote_plus(query or ""))
    net = NETWORKS[m["network"]]
    params = net["params"](m["country"])
    params["mid"] = m.get("mid", "")
    # Only wrap when the network is configured, otherwise send the plain link.
    required = [k for k in ("tag", "affid", "site_id") if ("{%s}" % k) in net["click"]]
    if any(not params.get(k) for k in required):
        return raw
    sep = "&" if "?" in raw else "?"
    return net["click"].format(raw_url=raw, url=quote_plus(raw), sep=sep, **params)


# How each country writes a price: (symbol before?, decimal separator, thousands separator, decimals)
PRICE_STYLE = {"US": (1, ".", ",", 2), "GB": (1, ".", ",", 2), "IE": (1, ".", ",", 2), "CA": (1, ".", ",", 2), "AU": (1, ".", ",", 2),
               "CH": (1, ".", "'", 2), "BR": (1, ",", ".", 2), "TR": (0, ",", ".", 0)}


def format_price(amount, country):
    """12.5 -> "12,50 €" / "£12.50" / "R$ 12,50" / "CHF 12.50", as the country writes it."""
    c = COUNTRIES[country]
    before, dec, thou, digits = PRICE_STYLE.get(country, (0, ",", ".", 2))
    num = f"{amount:,.{digits}f}".replace(",", "X").replace(".", dec).replace("X", thou)
    if thou == "." and country in ("PL", "SE", "FI", "DK", "RO", "FR"):   # these group with a space
        num = num.replace(".", " ") if dec == "," else num
    sym = c["symbol"]
    if before:
        return f"{sym} {num}" if sym.isalpha() or sym == "R$" else f"{sym}{num}"
    return f"{num} {sym}"
