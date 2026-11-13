"""giftdetect.com landing pages for search engines: a home page per country and gift lists.

    dist/index.html                           the detecting home page (hreflang x-default)
    dist/<cc>/index.html                      a country's home page in its language, with links to its lists
    dist/<cc>/<root>/<slug>/index.html        a gift list ("Geschenke für Papa"): intro, numbers, top products
    dist/<cc>/<root>/<slug>/<under-n>/        the same list under a price ceiling
    dist/sitemap-pages.xml                    all of them, with hreflang alternates

A list is a fixed search (LISTS below) run at build time, so the products are in the HTML
for crawlers; in the browser the page is the normal gift search with those filters set.
A list is only written for a country where at least MIN_PRODUCTS products fit it well.
Texts: content/lists/<lang>.json (README.md there). Product pages (/p/<id>) repeat the
shops' own texts and are kept out of the index; these pages are what we want found.
"""
import html
import json
import os
import re
import shutil
import statistics

import blog_pages

SITE = "https://giftdetect.com"
CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "lists")
MIN_PRODUCTS = 12        # fewer good matches than this: no page
MIN_MATCH = 70           # "fits well": the match badge the search shows, in percent
SHOWN = 36               # products in the HTML (one page of the search)
POOL = 1000              # how deep we look for good matches

# (id, group, search filters, blog article id or None, emoji)
LISTS = [
    ("for-her", "who", {"gender": "female"}, "birthday-gifts-for-her", "👩"),
    ("for-him", "who", {"gender": "male"}, "birthday-gifts-for-him", "👨"),
    ("for-mom", "who", {"gender": "female", "occasion": "mothers_day"}, "gifts-for-mom", "💐"),
    ("for-dad", "who", {"gender": "male", "occasion": "fathers_day"}, "gifts-for-dad", "👔"),
    ("for-girlfriend", "who", {"gender": "female", "occasion": "valentines"}, "valentines-day-gifts", "💝"),
    ("for-boyfriend", "who", {"gender": "male", "occasion": "valentines"}, "valentines-day-gifts", "💙"),
    ("for-kids", "who", {"age": "child"}, None, "🧒"),
    ("for-teens", "who", {"age": "teen"}, "gifts-for-teenagers", "🎧"),
    ("for-grandparents", "who", {"age": "senior"}, "gifts-for-grandparents", "👵"),
    ("birthday", "occasion", {"occasion": "birthday"}, None, "🎂"),
    ("christmas", "occasion", {"occasion": "christmas"}, "christmas-gift-ideas", "🎄"),
    ("valentines", "occasion", {"occasion": "valentines"}, "valentines-day-gifts", "❤️"),
    ("anniversary", "occasion", {"occasion": "anniversary"}, "anniversary-gifts", "💑"),
    ("wedding", "occasion", {"occasion": "wedding"}, None, "💍"),
    ("housewarming", "occasion", {"occasion": "housewarming"}, "housewarming-gifts", "🏡"),
    ("graduation", "occasion", {"occasion": "graduation"}, "graduation-gifts", "🎓"),
    ("retirement", "occasion", {"occasion": "retirement"}, "retirement-gifts", "🏖️"),
    ("new-baby", "occasion", {"occasion": "new_baby"}, "new-baby-gifts", "🍼"),
    ("thank-you", "occasion", {"occasion": "thank_you"}, None, "🙏"),
    ("get-well", "occasion", {"occasion": "get_well"}, None, "🌷"),
    ("birthday-for-her", "combo", {"gender": "female", "occasion": "birthday"}, "birthday-gifts-for-her", "🎂"),
    ("birthday-for-him", "combo", {"gender": "male", "occasion": "birthday"}, "birthday-gifts-for-him", "🎉"),
    ("birthday-for-kids", "combo", {"age": "child", "occasion": "birthday"}, None, "🎈"),
    ("birthday-for-teens", "combo", {"age": "teen", "occasion": "birthday"}, "gifts-for-teenagers", "🎧"),
    ("christmas-for-her", "combo", {"gender": "female", "occasion": "christmas"}, "christmas-gift-ideas", "🎄"),
    ("christmas-for-him", "combo", {"gender": "male", "occasion": "christmas"}, "christmas-gift-ideas", "🎅"),
    ("christmas-for-kids", "combo", {"age": "child", "occasion": "christmas"}, "christmas-gift-ideas", "🧸"),
    ("christmas-for-teens", "combo", {"age": "teen", "occasion": "christmas"}, "christmas-gift-ideas", "🎁"),
    ("tech", "interest", {"personality": "tech"}, None, "💻"),
    ("gamer", "interest", {"personality": "gamer"}, "gifts-for-gamers", "🎮"),
    ("foodie", "interest", {"personality": "foodie"}, None, "🍝"),
    ("coffee_tea", "interest", {"personality": "coffee_tea"}, "coffee-and-tea-gifts", "☕"),
    ("outdoor", "interest", {"personality": "outdoor"}, None, "🏕️"),
    ("fitness", "interest", {"personality": "fitness"}, None, "🏋️"),
    ("bookworm", "interest", {"personality": "bookworm"}, None, "📚"),
    ("artist", "interest", {"personality": "artist"}, None, "🎨"),
    ("music", "interest", {"personality": "music"}, None, "🎵"),
    ("traveler", "interest", {"personality": "traveler"}, "gifts-for-travelers", "✈️"),
    ("homebody", "interest", {"personality": "homebody"}, None, "🛋️"),
    ("fashion", "interest", {"personality": "fashion"}, None, "👗"),
    ("gardener", "interest", {"personality": "gardener"}, "gifts-for-gardeners", "🌱"),
    ("pet_lover", "interest", {"personality": "pet_lover"}, "gifts-for-pet-lovers", "🐾"),
    ("wellness", "interest", {"personality": "wellness"}, None, "🧖"),
    ("maker", "interest", {"personality": "maker"}, None, "🔧"),
]
GROUPS = ["who", "occasion", "combo", "interest"]
BY_ID = {l[0]: l for l in LISTS}
# lists that also get "under <price>" pages, and the three price ceilings per currency
# (the first three steps of the search bar's budget picker, web/ui.js BUDGETS)
BUDGET_LISTS = ["christmas", "birthday", "for-her", "for-him", "for-mom", "for-dad", "for-kids"]
TIERS = {"USD": [25, 50, 100], "EUR": [25, 50, 100], "GBP": [20, 40, 80], "CAD": [30, 60, 120], "AUD": [30, 70, 150],
         "CHF": [25, 50, 100], "PLN": [100, 200, 400], "SEK": [250, 500, 1000], "DKK": [200, 400, 750],
         "BRL": [100, 200, 500], "RON": [100, 250, 500]}
# English reads "shops in the United Kingdom"; "mum" outside North America
EN_COUNTRY = {"US": "the United States", "GB": "the United Kingdom"}
MUM = {"GB", "IE", "AU"}
ROOT_TEXT = {
    "title": "giftdetect.com: gift finder with ideas from shops in your country",
    "description": "giftdetect.com is a gift search engine: choose who the gift is for, the occasion, their personality and your budget, and get matching ideas from shops in your country.",
}
esc = lambda s: html.escape(str(s), quote=True)


# ---------------------------------------------------------------- texts
def load(content=CONTENT):
    """{lang: texts} for every language that has a complete, valid file."""
    out = {}
    for name in sorted(os.listdir(content)) if os.path.isdir(content) else []:
        if not name.endswith(".json"):
            continue
        lang = name[:-5]
        d = json.load(open(os.path.join(content, name), encoding="utf-8"))
        slugs = [d["lists"][lid]["slug"] for lid in BY_ID]            # KeyError: a list is missing
        for s in slugs + [d["root"], d["under_slug"].replace("{n}", "1")]:
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s):
                raise ValueError(f"{name}: {s!r} must be lowercase ASCII with hyphens")
        if len(set(slugs)) != len(slugs):
            raise ValueError(f"{name}: two lists share a slug")
        out[lang] = d
    return out


def _mum(s):
    return re.sub(r"\bmom(s?)\b", r"mum\1", re.sub(r"\bMom(s?)\b", r"Mum\1", s))


def texts_for(cc, lang, texts):
    """The language's texts for one country (British English says "mum")."""
    t = texts[lang]
    if lang == "en" and cc in MUM:
        walk = lambda v: {k: walk(x) for k, x in v.items()} if isinstance(v, dict) else _mum(v)     # values only: ids stay
        t = walk(t)
    return t


def country_name(cc, lang, countries):
    return EN_COUNTRY.get(cc, countries[cc]["name"]) if lang == "en" else countries[cc]["name"]


def fill(s, **kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def search_qs(filters, price_max=None):
    q = [f"{k}={v}" for k, v in filters.items()]
    if price_max:
        q.append(f"max={price_max}")
    return "&".join(q)


# ---------------------------------------------------------------- html pieces
def card(r, link, view, eager=False):
    """The search's result card (web/ui.js card()), as static HTML."""
    pid = esc(r["id"])
    thumb = (f'<img src="{esc(r["image"])}" alt="{esc(r["title"])}"{"" if eager else " loading=\"lazy\""} '
             f'onerror="this.closest(\'article\').remove()">' if r.get("image") else f'<span aria-hidden="true">{esc(r.get("emoji") or "🎁")}</span>')
    was = f' <s class="was">{esc(r["rrp_text"])}</s>' if r.get("rrp_text") else ""
    return (f'<article class="card"><a class="thumb" href="/p/{pid}" data-id="{pid}">{thumb}<span class="badge shop">{esc(r["merchant"])}</span></a>'
            f'<div class="body"><h4><a href="/p/{pid}" data-id="{pid}">{esc(r["title"])}</a></h4><div class="desc">{esc((r.get("description") or "")[:300])}</div>'
            f'<div class="foot"><span class="price">{esc(r["price_text"])}{was}</span>'
            f'<a class="buy" href="{esc(link)}" target="_blank" rel="nofollow sponsored noopener">{esc(view)} →</a></div></div></article>')


def chip(url, label, emoji=""):
    return f'<a class="chip-link" href="{url}">{f"<span aria-hidden=\"true\">{emoji}</span> " if emoji else ""}{esc(label)}</a>'


def hreflang_tags(alts, default=None):
    """alts: {(lang, cc): url}. Each country gets lang-CC; a language's main country also gets the bare lang."""
    tags = [f'<link rel="alternate" hreflang="{l}-{cc}" href="{u}">' for (l, cc), u in alts.items()]
    for (l, cc), u in alts.items():
        if blog_pages.LANG_COUNTRY.get(l) == cc:
            tags.append(f'<link rel="alternate" hreflang="{l}" href="{u}">')
    if default:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{default}">')
    return "\n".join(tags)


def sitemap_links(alts, default=None):
    out = "".join(f'<xhtml:link rel="alternate" hreflang="{l}-{cc}" href="{u}"/>' for (l, cc), u in alts.items())
    out += "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for (l, cc), u in alts.items() if blog_pages.LANG_COUNTRY.get(l) == cc)
    return out + (f'<xhtml:link rel="alternate" hreflang="x-default" href="{default}"/>' if default else "")


# ---------------------------------------------------------------- build
def build(dest, render, engine, links, shown, countries, format_price):
    """Write the home pages, the list pages and sitemap-pages.xml; returns the sitemap's name.

    render(lang, head, blog_html, cfg, slots) -> page;  links: {product id: shop link};
    shown: the countries with products;  countries: app.config.COUNTRIES."""
    texts = load()
    shown = [cc for cc in shown if countries[cc]["lang"] in texts]
    blog = blog_pages.load()
    blog_by = {lang: {a["id"]: a for a in arts} for lang, arts in blog.items()}

    # 1) run every list's search in every country --------------------------------------
    pages = {}                               # (cc, list id, tier index or None) -> page data
    for cc in shown:
        lang = countries[cc]["lang"]
        t = texts_for(cc, lang, texts)
        tiers = TIERS.get(countries[cc]["currency"], [])
        for lid, group, filters, guide, emoji in LISTS:
            for ti in [None] + (list(range(len(tiers))) if lid in BUDGET_LISTS else []):
                ceiling = None if ti is None else tiers[ti]
                res = engine.search(cc, gender=filters.get("gender"), age=[filters.get("age")], occasion=[filters.get("occasion")],
                                    personality=[filters.get("personality")], price_max=ceiling, limit=POOL)
                good = [r for r in res["results"] if (r.get("match") or 0) >= MIN_MATCH]
                if len(good) < MIN_PRODUCTS:
                    continue
                url = f"/{cc.lower()}/{t['root']}/{t['lists'][lid]['slug']}/"
                if ti is not None:
                    url += t["under_slug"].replace("{n}", str(ceiling)) + "/"
                prices = sorted(r["price"] for r in good)
                pages[(cc, lid, ti)] = {
                    "url": url, "results": good[:SHOWN], "n": len(good), "shops": len({r["merchant"] for r in good}),
                    "min": format_price(prices[0], cc), "max": format_price(prices[-1], cc),
                    "median": format_price(statistics.median(prices), cc), "price": None if ti is None else re.sub(r"[.,]00(?!\d)", "", format_price(ceiling, cc)),     # "under £40", not "£40.00"
                }
    # an "under" page needs its base page (breadcrumb, budget links)
    pages = {k: v for k, v in pages.items() if k[2] is None or (k[0], k[1], None) in pages}

    def h1_of(cc, lid, ti):
        t = texts_for(cc, countries[cc]["lang"], texts)
        h1 = t["lists"][lid]["h1"]
        return h1 if ti is None else fill(t["under_h1"], h1=h1, price=pages[(cc, lid, ti)]["price"])

    for cc in {k[0] for k in pages} | set(shown):
        shutil.rmtree(os.path.join(dest, cc.lower()), ignore_errors=True)

    def write(url, text):
        path = os.path.join(dest, url.strip("/"), "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)

    homes = {(countries[cc]["lang"], cc): f"{SITE}/{cc.lower()}/" for cc in shown}
    country_links = "".join(chip(f"/{cc.lower()}/", countries[cc]["name"], countries[cc]["flag"]) for cc in shown)
    urls = [(f"{SITE}/", homes, f"{SITE}/")]

    def list_chips(cc, keys):
        return "".join(chip(pages[k]["url"], h1_of(*k), BY_ID[k[1]][4]) for k in keys if k in pages)

    # 2) list pages ------------------------------------------------------------------------
    for (cc, lid, ti), p in pages.items():
        lang = countries[cc]["lang"]
        t = texts_for(cc, lang, texts)
        ui, L = t["ui"], t["lists"][lid]
        _, group, filters, guide, emoji = BY_ID[lid]
        cname = country_name(cc, lang, countries)
        h1 = h1_of(cc, lid, ti)
        nums = dict(n=p["n"], shops=p["shops"], country=cname, min=p["min"], max=p["max"], median=p["median"], price=p["price"] or "", h1=L["h1"])
        title = L["title"] if ti is None else h1
        desc = L["description"] if ti is None else fill(t["under_description"], **nums)
        url = SITE + p["url"]
        alts = {(countries[c]["lang"], c): SITE + pages[(c, lid, ti)]["url"] for c in shown if (c, lid, ti) in pages}
        default = alts.get(("en", "US"))
        urls.append((url, alts, default))
        base = pages[(cc, lid, None)]
        crumbs = [("giftdetect.com", f"/{cc.lower()}/"), (L["h1"], base["url"])] + ([(p["price"], p["url"])] if ti is not None else [])
        ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": lang,
               "mainEntity": {"@type": "ItemList", "numberOfItems": len(p["results"]), "itemListElement": [
                   {"@type": "ListItem", "position": i + 1, "name": r["title"], "url": f"{SITE}/p/{r['id']}"} for i, r in enumerate(p["results"])]}},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]}]
        head = blog_pages.head(lang, title if "giftdetect" in title else f"{title} | giftdetect.com", desc, url, hreflang_tags(alts, default), ld=ld)
        tier_keys = [(cc, lid, i) for i in range(3)]
        budget = list_chips(cc, [k for k in tier_keys if k != (cc, lid, ti)])
        if ti is not None:
            budget = chip(base["url"], L["h1"], emoji) + budget
        top = f"""<div class="list-head gutter" id="list-head"><div class="list-in">
<nav class="crumbs" aria-label="breadcrumb">{'<span>›</span>'.join(f'<a href="{u}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span aria-current="page">{esc(n)}</span>' for i, (n, u) in enumerate(crumbs))}</nav>
<h1><span aria-hidden="true">{emoji}</span> {esc(h1)}</h1>
<p class="list-intro">{esc(L['intro'])}</p>
<p class="list-stats">{esc(fill(ui['stats'], **nums))}{' ' + esc(fill(ui['under_intro'], **nums)) if ti is not None else ''}</p>
{f'<p class="chips"><b>{esc(ui["budget"])}</b> {budget}</p>' if budget else ''}
</div></div>"""
        art = blog_by.get(lang, {}).get(guide) if guide else None
        guide_html = (f'<p class="list-guide"><a href="/blog/{lang}/{art["slug"]}/">📖 {esc(fill(ui["guide"], title=art["title"]))}</a></p>' if art else "")
        same = [(cc, x[0], None) for x in LISTS if x[1] == group and x[0] != lid]
        other = [(cc, x[0], None) for x in LISTS if x[1] != group and x[1] != "combo"]
        related = filters.get("occasion") or filters.get("gender") or filters.get("age")
        combos = [(cc, x[0], None) for x in LISTS if x[1] == "combo" and x[0] != lid and related and related in x[2].values()]
        after = f"""<div class="blog gutter" id="blog-wrap"><div class="list-in">
{guide_html}
<aside class="hub"><h2>{esc(ui['more'])}</h2>
<p class="chips">{list_chips(cc, combos + same)}</p>
<p class="chips">{list_chips(cc, other)}</p>
<p class="chips"><a class="chip-link" href="/{cc.lower()}/">🎁 {esc(ui['home'])}</a>{f'<a class="chip-link" href="/blog/{lang}/">📖 {esc(ui["blog"])}</a>' if lang in blog else ''}</p>
</aside></div></div>"""
        cards = "".join(card(r, links.get(r["id"], f"/p/{r['id']}"), ui["view"], eager=i < 4) for i, r in enumerate(p["results"]))
        cfg = {"lang": lang, "country": cc, "fixed": True, "root": f"/{cc.lower()}/", "sel": search_qs(filters, None if ti is None else TIERS[countries[cc]["currency"]][ti])}
        write(p["url"], render(lang, head, after, cfg, {"before_results": top, "results": cards, "title": ui["picks"]}))

    # 3) country home pages ----------------------------------------------------------------
    for cc in shown:
        lang = countries[cc]["lang"]
        t = texts_for(cc, lang, texts)
        ui, H = t["ui"], t["home"]
        cname = country_name(cc, lang, countries)
        url = f"{SITE}/{cc.lower()}/"
        groups = "".join(
            f'<h3>{esc(ui[g])}</h3><p class="chips">{chips}</p>'
            for g in GROUPS for chips in [list_chips(cc, [(cc, x[0], None) for x in LISTS if x[1] == g])] if chips)
        budget = list_chips(cc, [(cc, lid, i) for lid in BUDGET_LISTS for i in range(3)])
        if budget:
            groups += f'<h3>{esc(ui["budget"])}</h3><p class="chips">{budget}</p>'
        hub = f"""<div class="blog gutter" id="blog-wrap"><div class="list-in"><aside class="hub">
{f'<h2>{esc(ui["popular"])}</h2>{groups}' if groups else ''}
{f'<p class="chips"><a class="chip-link" href="/blog/{lang}/">📖 {esc(ui["blog"])}</a></p>' if lang in blog else ''}
<h3>{esc(ui['countries'])}</h3><p class="chips">{country_links}</p>
</aside></div></div>"""
        ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "giftdetect.com", "url": url, "inLanguage": lang}]
        head = blog_pages.head(lang, fill(H["title"], country=cname), fill(H["description"], country=cname), url, hreflang_tags(homes, f"{SITE}/"), ld=ld)
        cfg = {"lang": lang, "country": cc, "fixed": True, "home": True, "root": f"/{cc.lower()}/"}
        write(f"/{cc.lower()}/", render(lang, head, hub, cfg, {"hero": (fill(H["h1"], country=cname), fill(H["sub"], country=cname))}))

    # 4) the detecting home page (x-default) -------------------------------------------------
    en = texts.get("en")
    hub = (f'<div class="blog gutter" id="blog-wrap"><div class="list-in"><aside class="hub">'
           f'<h3>{esc(en["ui"]["countries"] if en else "giftdetect.com")}</h3><p class="chips">{country_links}</p></aside></div></div>')
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": "giftdetect.com", "url": f"{SITE}/"}]
    head = blog_pages.head("en", ROOT_TEXT["title"], ROOT_TEXT["description"], f"{SITE}/", hreflang_tags(homes, f"{SITE}/"), ld=ld)
    with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as f:
        f.write(render("en", head, hub, None, None))

    # 5) sitemap ---------------------------------------------------------------------------
    for cc in shown:
        urls.append((f"{SITE}/{cc.lower()}/", homes, f"{SITE}/"))
    with open(os.path.join(dest, "sitemap-pages.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
        for loc, alts, default in urls:
            f.write(f"<url><loc>{loc}</loc>{sitemap_links(alts, default)}</url>\n")
        f.write("</urlset>\n")
    per = {cc: sum(1 for k in pages if k[0] == cc) for cc in shown}
    print(f"lists: {len(pages)} pages in {len(shown)} countries ({', '.join(f'{cc} {n}' for cc, n in per.items())})")
    return "sitemap-pages.xml"
