"""giftdetect.com blog: content/blog/<lang>/<id>.md -> static pages with the gift search on top.

    dist/blog/index.html                 language hub (sends the visitor to their language)
    dist/blog/<lang>/index.html          the language's article list
    dist/blog/<lang>/<slug>/index.html   one article
    dist/sitemap-blog.xml                every page, with hreflang alternates

The page shell (styles, search bar, scripts) comes from export_static, so a blog page is the
gift search with an article under it: searching shows the results above the article.
File format: content/blog/README.md.
"""
import html
import json
import os
import re
from datetime import date

SITE = "https://giftdetect.com"
CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content", "blog")
# the languages of the countries the site shows; a blog page opens the search in its language
LANG_COUNTRY = {"en": "US", "de": "DE", "nl": "NL", "fr": "FR", "pl": "PL", "it": "IT", "es": "ES", "sv": "SE",
                "fi": "FI", "da": "DK", "pt": "BR", "ro": "RO"}
LOCALE = {"en": "en_US", "de": "de_DE", "nl": "nl_NL", "fr": "fr_FR", "pl": "pl_PL", "it": "it_IT", "es": "es_ES",
          "sv": "sv_SE", "fi": "fi_FI", "da": "da_DK", "pt": "pt_BR", "ro": "ro_RO"}
LANG_NAME = {"en": "English", "de": "Deutsch", "nl": "Nederlands", "fr": "Français", "pl": "Polski", "it": "Italiano",
             "es": "Español", "sv": "Svenska", "fi": "Suomi", "da": "Dansk", "pt": "Português (Brasil)", "ro": "Română"}
EMOJI = {"christmas-gift-ideas": "🎄", "secret-santa-gifts": "🎅", "gifts-for-dad": "👔", "gifts-for-mom": "💐",
         "valentines-day-gifts": "❤️", "birthday-gifts-for-her": "🎂", "birthday-gifts-for-him": "🎉", "gifts-for-teenagers": "🎧",
         "gifts-for-grandparents": "👵", "new-baby-gifts": "🍼", "housewarming-gifts": "🏡", "anniversary-gifts": "💑",
         "graduation-gifts": "🎓", "retirement-gifts": "🏖️", "gifts-for-gamers": "🎮", "coffee-and-tea-gifts": "☕",
         "gifts-for-travelers": "✈️", "gifts-for-gardeners": "🌱", "gifts-for-pet-lovers": "🐾", "how-to-choose-a-gift": "🎁"}
T = {
    "en": {"blog": "Blog", "title": "Gift guides and gift ideas", "intro": "Practical gift guides for every occasion and every kind of person, each with a direct way into the gift search.", "read": "Read the guide →", "min": "{n} min read", "related": "More gift guides", "cta": "Find matching gifts →", "home": "Gift search", "lead": "Find a gift right away"},
    "de": {"blog": "Blog", "title": "Geschenkratgeber und Geschenkideen", "intro": "Praktische Geschenkratgeber für jeden Anlass und jeden Typ Mensch, jeweils mit direktem Weg in die Geschenksuche.", "read": "Ratgeber lesen →", "min": "{n} Min. Lesezeit", "related": "Weitere Geschenkratgeber", "cta": "Passende Geschenke finden →", "home": "Geschenksuche", "lead": "Gleich ein Geschenk finden"},
    "nl": {"blog": "Blog", "title": "Cadeaugidsen en cadeau-ideeën", "intro": "Praktische cadeaugidsen voor elke gelegenheid en elk type persoon, telkens met een directe weg naar de cadeauzoeker.", "read": "Lees de gids →", "min": "{n} min lezen", "related": "Meer cadeaugidsen", "cta": "Passende cadeaus vinden →", "home": "Cadeauzoeker", "lead": "Meteen een cadeau vinden"},
    "fr": {"blog": "Blog", "title": "Guides cadeaux et idées cadeaux", "intro": "Des guides cadeaux pratiques pour chaque occasion et chaque personnalité, avec un accès direct à la recherche de cadeaux.", "read": "Lire le guide →", "min": "{n} min de lecture", "related": "Plus de guides cadeaux", "cta": "Trouver des cadeaux adaptés →", "home": "Recherche de cadeaux", "lead": "Trouver un cadeau tout de suite"},
    "pl": {"blog": "Blog", "title": "Poradniki prezentowe i pomysły na prezent", "intro": "Praktyczne poradniki prezentowe na każdą okazję i dla każdego typu osoby, z bezpośrednim przejściem do wyszukiwarki prezentów.", "read": "Czytaj poradnik →", "min": "{n} min czytania", "related": "Więcej poradników prezentowych", "cta": "Znajdź pasujące prezenty →", "home": "Wyszukiwarka prezentów", "lead": "Znajdź prezent od razu"},
    "it": {"blog": "Blog", "title": "Guide ai regali e idee regalo", "intro": "Guide pratiche ai regali per ogni occasione e ogni tipo di persona, ognuna con un accesso diretto alla ricerca regali.", "read": "Leggi la guida →", "min": "{n} min di lettura", "related": "Altre guide ai regali", "cta": "Trova regali adatti →", "home": "Ricerca regali", "lead": "Trova subito un regalo"},
    "es": {"blog": "Blog", "title": "Guías de regalos e ideas para regalar", "intro": "Guías de regalos prácticas para cada ocasión y cada tipo de persona, cada una con acceso directo al buscador de regalos.", "read": "Leer la guía →", "min": "{n} min de lectura", "related": "Más guías de regalos", "cta": "Encontrar regalos a medida →", "home": "Buscador de regalos", "lead": "Encuentra un regalo ahora"},
    "sv": {"blog": "Blogg", "title": "Presentguider och presenttips", "intro": "Praktiska presentguider för varje tillfälle och varje typ av person, var och en med en direkt väg in i presentsökningen.", "read": "Läs guiden →", "min": "{n} min läsning", "related": "Fler presentguider", "cta": "Hitta passande presenter →", "home": "Presentsök", "lead": "Hitta en present direkt"},
    "fi": {"blog": "Blogi", "title": "Lahjaoppaat ja lahjaideat", "intro": "Käytännöllisiä lahjaoppaita jokaiseen tilaisuuteen ja jokaiselle ihmistyypille, jokaisesta suora pääsy lahjahakuun.", "read": "Lue opas →", "min": "{n} min lukuaika", "related": "Lisää lahjaoppaita", "cta": "Löydä sopivat lahjat →", "home": "Lahjahaku", "lead": "Löydä lahja heti"},
    "da": {"blog": "Blog", "title": "Gaveguides og gaveideer", "intro": "Praktiske gaveguides til enhver anledning og enhver type person, hver med en direkte vej ind i gavesøgningen.", "read": "Læs guiden →", "min": "{n} min læsning", "related": "Flere gaveguides", "cta": "Find passende gaver →", "home": "Gavesøgning", "lead": "Find en gave med det samme"},
    "pt": {"blog": "Blog", "title": "Guias de presentes e ideias de presente", "intro": "Guias de presentes práticos para cada ocasião e cada tipo de pessoa, cada um com acesso direto à busca de presentes.", "read": "Ler o guia →", "min": "{n} min de leitura", "related": "Mais guias de presentes", "cta": "Encontrar presentes ideais →", "home": "Busca de presentes", "lead": "Encontre um presente agora"},
    "ro": {"blog": "Blog", "title": "Ghiduri de cadouri și idei de cadouri", "intro": "Ghiduri practice de cadouri pentru orice ocazie și orice tip de persoană, fiecare cu acces direct la căutarea de cadouri.", "read": "Citește ghidul →", "min": "{n} min de citit", "related": "Alte ghiduri de cadouri", "cta": "Găsește cadouri potrivite →", "home": "Căutare cadouri", "lead": "Găsește un cadou acum"},
}
SEARCH_KEYS = {"gender", "age", "occasion", "personality", "category", "max", "min"}
esc = lambda s: html.escape(str(s), quote=True)


# ---------------------------------------------------------------- reading
def parse(path):
    text = open(path, encoding="utf-8").read().lstrip("﻿")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", text, re.S)
    if not m:
        raise ValueError(f"{path}: no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("id", "slug", "title", "description"):
        if not meta.get(k):
            raise ValueError(f"{path}: front matter lacks {k}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["slug"]):
        raise ValueError(f"{path}: slug {meta['slug']!r} must be lowercase ASCII with hyphens")
    meta["body"] = m.group(2).strip()
    meta["words"] = len(re.findall(r"\w+", meta["body"]))
    return meta


def load(content=CONTENT):
    """{lang: [article, ...]} in a stable order (EMOJI's topic order, then by id)."""
    out = {}
    for lang in LANG_COUNTRY:
        d = os.path.join(content, lang)
        if not os.path.isdir(d):
            continue
        arts = [parse(os.path.join(d, n)) for n in sorted(os.listdir(d)) if n.endswith(".md")]
        if arts:
            out[lang] = arts
    order = list(EMOJI)              # the topic order (seasonal guides first), then any new ids
    for lang, arts in out.items():
        arts.sort(key=lambda a: (order.index(a["id"]) if a["id"] in order else len(order), a["id"]))
        slugs = [a["slug"] for a in arts]
        if len(set(slugs)) != len(slugs):
            raise ValueError(f"{lang}: two articles share a slug")
    return out


# ---------------------------------------------------------------- markdown (the small subset of README.md)
def search_href(spec):
    q = []
    for part in spec.split():
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k in SEARCH_KEYS and re.fullmatch(r"[a-z0-9_,.]+", v):
            q.append(f"{k}={v}")
    return "/?" + "&".join(q) if q else "/"


def inline(s, lang, slugs):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)

    def link(m):
        text, url = m.group(1), html.unescape(m.group(2))
        if url.startswith("blog:"):
            slug = slugs.get(url[5:])
            return f'<a href="/blog/{lang}/{slug}/">{text}</a>' if slug else text
        if url.startswith("/"):
            return f'<a href="{esc(url)}">{text}</a>'
        return f'<a href="{esc(url)}" rel="noopener" target="_blank">{text}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)


def to_html(body, lang, slugs):
    """Return (html, faq) where faq is [(question, answer text)] from ### headings ending in '?'."""
    out, para, items, kind, faq = [], [], [], None, []
    q = None

    def flush():
        nonlocal para, items, kind
        if para:
            text = " ".join(para)
            out.append(f"<p>{inline(text, lang, slugs)}</p>")
            if q is not None and q[1] is None:
                q[1] = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).replace("**", "").replace("*", "")
            para = []
        if items:
            tag = "ol" if kind == "ol" else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i, lang, slugs)}</li>" for i in items) + f"</{tag}>")
            items, kind = [], None

    for raw in body.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush()
            continue
        m = re.fullmatch(r"\[\[search\s*(.*?)\|\s*(.+?)\s*\]\]", s)
        if m:
            flush()
            out.append(f'<p class="blog-cta-row"><a class="blog-cta" href="{esc(search_href(m.group(1)))}">{esc(m.group(2))}</a></p>')
            continue
        m = re.match(r"(#{2,3})\s+(.*)", s)
        if m:
            flush()
            level, text = len(m.group(1)), m.group(2).strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]
            out.append(f'<h{level} id="{esc(anchor)}">{inline(text, lang, slugs)}</h{level}>')
            if level == 3 and text.endswith("?"):
                q = [text, None]
                faq.append(q)
            else:
                q = None
            continue
        m = re.match(r"([-*]|\d+\.)\s+(.*)", s)
        if m and not s.startswith("**"):
            if para:
                flush()
            k = "ol" if m.group(1)[0].isdigit() else "ul"
            if items and kind != k:
                flush()
            kind = k
            items.append(m.group(2))
            continue
        if items:                        # a wrapped list line continues the item
            items[-1] += " " + s
            continue
        para.append(s)
    flush()
    return "\n".join(out), [(a, b) for a, b in faq if b]


def teaser(body, n=170):
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if b and not b.startswith(("#", "[[", "-", "*", "1.")):
            t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b).replace("**", "").replace("*", "")
            t = " ".join(t.split())
            return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"
    return ""


# ---------------------------------------------------------------- pages
def alternates(urls_by_lang, default_lang="en"):
    tags = [f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in urls_by_lang.items()]
    if default_lang in urls_by_lang:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{urls_by_lang[default_lang]}">')
    return "\n".join(tags)


def head(lang, title, description, url, alt, og_type="website", ld=None, robots=None):
    ld_tags = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f"""<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{alt}
{f'<meta name="robots" content="{robots}">' if robots else ''}
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="giftdetect.com">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}"><meta property="og:locale" content="{LOCALE.get(lang, 'en_US')}">
<meta name="twitter:card" content="summary">
{ld_tags}"""


def card(a, lang):
    t = T[lang]
    return (f'<a class="post-card" href="/blog/{lang}/{a["slug"]}/"><span class="pc-emoji" aria-hidden="true">{EMOJI.get(a["id"], "🎁")}</span>'
            f'<h3>{esc(a["title"])}</h3><p>{esc(teaser(a["body"]))}</p><span class="pc-more">{esc(t["read"])}</span></a>')


def article_page(a, lang, arts, by_id):
    t = T[lang]
    slugs = {x["id"]: x["slug"] for x in arts}
    body, faq = to_html(a["body"], lang, slugs)
    url = f"{SITE}/blog/{lang}/{a['slug']}/"
    alt = alternates({l: f"{SITE}/blog/{l}/{x['slug']}/" for l, x in by_id[a["id"]].items()})
    minutes = max(1, round(a["words"] / 200))
    day = a.get("date") or date.today().isoformat()
    main_cta = f'<p class="blog-cta-row big"><a class="blog-cta" href="{esc(search_href(a.get("search", "")))}">{esc(t["cta"])}</a></p>'
    i = arts.index(a)
    related = [arts[(i + k) % len(arts)] for k in range(1, 4) if len(arts) > 1]
    ld = [{
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"], "description": a["description"],
        "inLanguage": lang, "datePublished": day, "dateModified": day, "mainEntityOfPage": url, "url": url,
        "author": {"@type": "Organization", "name": "giftdetect.com", "url": SITE},
        "publisher": {"@type": "Organization", "name": "giftdetect.com", "url": SITE}, "wordCount": a["words"],
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "giftdetect.com", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": t["blog"], "item": f"{SITE}/blog/{lang}/"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]}]
    if len(faq) >= 2:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q_, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q_, ans in faq]})
    page = f"""<div class="blog gutter" id="blog-wrap"><div class="blog-in">
<nav class="crumbs" aria-label="breadcrumb"><a href="/">giftdetect.com</a><span>›</span><a href="/blog/{lang}/">{esc(t['blog'])}</a><span>›</span><span aria-current="page">{esc(a['title'])}</span></nav>
<article class="post">
<p class="post-kicker"><span aria-hidden="true">{EMOJI.get(a['id'], '🎁')}</span> {esc(t['min'].format(n=minutes))} · <time datetime="{day}">{day}</time></p>
<h1>{esc(a['title'])}</h1>
{body}
{main_cta}
</article>
<aside class="related"><h2>{esc(t['related'])}</h2><div class="post-grid">{''.join(card(x, lang) for x in related)}</div></aside>
</div></div>"""
    return head(lang, f"{a['title']} | giftdetect.com", a["description"], url, alt, "article", ld), page


def index_page(lang, arts, langs):
    t = T[lang]
    url = f"{SITE}/blog/{lang}/"
    alt = alternates({l: f"{SITE}/blog/{l}/" for l in langs})
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": f"giftdetect.com {t['blog']}", "url": url, "inLanguage": lang,
           "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": f"{url}{a['slug']}/"} for a in arts]}]
    others = " · ".join(f'<a href="/blog/{l}/" hreflang="{l}" lang="{l}">{esc(LANG_NAME[l])}</a>' for l in langs if l != lang)
    page = f"""<div class="blog gutter" id="blog-wrap"><div class="blog-in">
<header class="blog-head"><h1>{esc(t['title'])}</h1><p>{esc(t['intro'])}</p></header>
<div class="post-grid">{''.join(card(a, lang) for a in arts)}</div>
<p class="blog-langs">{others}</p>
</div></div>"""
    return head(lang, f"{t['title']} | giftdetect.com {t['blog']}", t["intro"], url, alt, ld=ld), page


def hub_page(langs):
    """/blog/: sends the visitor to the blog in their browser language; lists every language for crawlers."""
    alt = alternates({l: f"{SITE}/blog/{l}/" for l in langs})
    links = "".join(f'<a class="post-card" href="/blog/{l}/" hreflang="{l}" lang="{l}"><h3>{esc(T[l]["title"])}</h3><p>{esc(LANG_NAME[l])}</p></a>' for l in langs)
    page = f"""<div class="blog gutter" id="blog-wrap"><div class="blog-in">
<header class="blog-head"><h1>giftdetect.com Blog</h1></header>
<div class="post-grid">{links}</div></div></div>
<script>(function(){{var l=(navigator.language||"en").slice(0,2).toLowerCase(),ok={json.dumps(langs)};location.replace("/blog/"+(ok.indexOf(l)>=0?l:"en")+"/");}})();</script>"""
    return head("en", "giftdetect.com Blog: gift guides", T["en"]["intro"], f"{SITE}/blog/", alt, robots="noindex, follow"), page


def build(dest, render):
    """Write every blog page with `render(lang, head_html, blog_html, blog_cfg) -> full page`.
    Returns the sitemap file name (to add to sitemap.xml) or None when there is no content."""
    data = load()
    if not data:
        return None
    langs = list(data)
    by_id = {}
    for lang, arts in data.items():
        for a in arts:
            by_id.setdefault(a["id"], {})[lang] = a
    root = os.path.join(dest, "blog")
    if os.path.isdir(root):
        import shutil
        shutil.rmtree(root)

    def write(rel, text):
        path = os.path.join(root, rel, "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)

    urls = []
    h, p = hub_page(langs)
    write("", render("en", h, p, {"lang": "en", "country": LANG_COUNTRY["en"], "hub": True}))
    for lang, arts in data.items():
        cfg = {"lang": lang, "country": LANG_COUNTRY[lang]}
        h, p = index_page(lang, arts, langs)
        write(lang, render(lang, h, p, cfg))
        urls.append((f"{SITE}/blog/{lang}/", {l: f"{SITE}/blog/{l}/" for l in langs}))
        for a in arts:
            h, p = article_page(a, lang, arts, by_id)
            write(os.path.join(lang, a["slug"]), render(lang, h, p, cfg))
            urls.append((f"{SITE}/blog/{lang}/{a['slug']}/", {l: f"{SITE}/blog/{l}/{x['slug']}/" for l, x in by_id[a["id"]].items()}))
    with open(os.path.join(dest, "sitemap-blog.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
        for loc, alts in urls:
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in alts.items())
            if "en" in alts:
                links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts["en"]}"/>'
            f.write(f"<url><loc>{loc}</loc>{links}</url>\n")
        f.write("</urlset>\n")
    print(f"blog: {sum(len(a) for a in data.values())} articles in {len(langs)} languages ({', '.join(f'{l} {len(a)}' for l, a in data.items())})")
    return "sitemap-blog.xml"
