#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EDI referans bölümünü üretir.

Veri kaynakları:
  - locales/*.json   segment, kod, eleman ve mesaj tipi açıklamaları (7 dil)
  - tools/content.py elle yazılmış açıklamalar, örnekler ve rehber yazıları

Çıktı (repo köküne yazılır):
  edi/index.html                TR hub
  edi/segment/<kod>.html        TR segment sayfaları
  edi/message/<tip>.html        TR mesaj tipi sayfaları
  edi/guide/<slug>.html         TR rehber yazıları
  edi/en/...                    aynısının İngilizcesi
  sitemap.xml, robots.txt

Kullanım:  python3 tools/build_reference.py
"""

import json
import os
import re
import shutil
import html as htmllib
from datetime import date

import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES = os.path.join(ROOT, 'locales')
OUT = os.path.join(ROOT, 'edi')
SITE = 'https://ediviewer.net'
LANGS = ['tr', 'en']

# Segment kodu gibi görünen anahtarlar: seg_ABC (üç büyük harf)
SEG_RE = re.compile(r'^seg_([A-Z]{3})$')
SEG_LOWER_RE = re.compile(r'^seg_([a-z]{3})$')
ELEM_RE = re.compile(r'^elem_([A-Z]{3})_(\d{2})$')
TYPE_RE = re.compile(r'^type_([A-Z]{4,6})$')


def esc(s):
    return htmllib.escape(str(s), quote=True)


def load(lang):
    with open(os.path.join(LOCALES, f'{lang}.json'), encoding='utf-8') as f:
        return json.load(f)


# =========================================================================
# VERİ TOPLAMA
# =========================================================================

def collect(d):
    """Sözlükten segment / eleman / kod / mesaj tipi verisini çıkarır."""
    segments, alt_titles, elements, codes, types = {}, {}, {}, {}, {}

    for k, v in d.items():
        m = SEG_RE.match(k)
        if m:
            segments[m.group(1)] = v
            continue
        m = SEG_LOWER_RE.match(k)
        if m:
            # Bazı segmentlerin yalnızca küçük harfli anahtarı var (seg_unz gibi)
            alt_titles[m.group(1).upper()] = v
            continue
        m = ELEM_RE.match(k)
        if m:
            elements.setdefault(m.group(1), []).append((int(m.group(2)), v))
            continue
        m = TYPE_RE.match(k)
        if m and m.group(1) != 'UNKNOWN':
            types[m.group(1)] = v
            continue
        if k.startswith('code_'):
            # code_<SEG>_<KOD>  ya da  code_<SEG>_<ALT>_<KOD>
            parts = k[5:].split('_')
            if len(parts) >= 2 and re.fullmatch(r'[A-Z]{3}', parts[0]):
                codes.setdefault(parts[0], []).append(('_'.join(parts[1:]), v))

    for seg in elements:
        elements[seg].sort()
    return segments, alt_titles, elements, codes, types


# =========================================================================
# ŞABLON
# =========================================================================

def page(lang, title, desc, body, depth, canonical, alt_href=None, alt_rel=None):
    """Ortak sayfa iskeleti. depth = kökten kaç klasör aşağıda."""
    up = '../' * depth
    ui = C.UI[lang]
    other = 'en' if lang == 'tr' else 'tr'
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — ediviewer</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{canonical}">
{f'<link rel="alternate" hreflang="{other}" href="{SITE}{alt_href}">' if alt_href else ''}
<link rel="stylesheet" href="{up}css/styles.css">
<link rel="stylesheet" href="{up}css/doc.css">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<meta name="google-adsense-account" content="ca-pub-7507702503844486">
</head>
<body>

<header class="doc-header">
  <a class="brand" href="{up}index.html" title="ediviewer">
    <span class="brand-mark" aria-hidden="true">e</span>
    <span class="brand-logo"><span class="lg-a">edi</span><span class="lg-b">viewer</span></span>
  </a>
  <nav class="doc-langs">
    <a href="{up}edi/index.html">{esc(ui['back_to_ref'])}</a>
    {f'<a href="{alt_rel}">{esc(ui["other_lang"])}</a>' if alt_rel else ''}
  </nav>
</header>

<main class="doc">
{body}
</main>

<section class="doc-footer">
  <div class="app-cta">
    <div>
      <div class="app-cta-title">{esc(ui['app_cta_title'])}</div>
      <div class="app-cta-text">{esc(ui['app_cta_text'])}</div>
    </div>
    <a class="app-cta-btn" href="{up}index.html">{esc(ui['app_cta_btn'])}</a>
  </div>
  <p><a href="{up}edi/index.html">{esc(ui['back_to_ref'])}</a> &middot;
     <a href="{up}{'gizlilik' if lang == 'tr' else 'privacy'}.html">{'Gizlilik Politikası' if lang == 'tr' else 'Privacy Policy'}</a></p>
</section>

</body>
</html>
"""


def md(text):
    """Rehber gövdeleri için küçük bir Markdown alt kümesi."""
    out, lines = [], text.strip().split('\n')
    i, in_code, in_table, in_list = 0, False, False, False
    para = []

    def flush_para():
        """Ardışık satırlar tek paragrafta birleşir; satır sonu boşluk demektir."""
        if para:
            out.append(f'<p>{" ".join(para)}</p>')
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False

    def close_table():
        nonlocal in_table
        if in_table:
            out.append('</tbody></table>')
            in_table = False

    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            flush_para(); close_list(); close_table()
            if not in_code:
                out.append('<pre class="doc-code"><code>')
                in_code = True
            else:
                out.append('</code></pre>')
                in_code = False
            i += 1
            continue
        if in_code:
            out.append(esc(ln))
            i += 1
            continue

        if ln.startswith('## '):
            flush_para(); close_list(); close_table()
            out.append(f'<h2>{esc(ln[3:].strip())}</h2>')
        elif ln.startswith('- '):
            flush_para(); close_table()
            if not in_list:
                out.append('<ul>'); in_list = True
            out.append(f'<li>{inline(ln[2:])}</li>')
        elif ln.startswith('|'):
            flush_para(); close_list()
            cells = [c.strip() for c in ln.strip('|').split('|')]
            if i + 1 < len(lines) and set(lines[i + 1].replace('|', '').strip()) <= set('-: '):
                out.append('<table class="doc-table"><thead><tr>'
                           + ''.join(f'<th>{inline(c)}</th>' for c in cells)
                           + '</tr></thead><tbody>')
                in_table = True
                i += 2
                continue
            out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
        elif ln.strip() == '':
            flush_para(); close_list(); close_table()
        else:
            close_list(); close_table()
            para.append(inline(ln.strip()))
        i += 1

    flush_para(); close_list(); close_table()
    return '\n'.join(out)


def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return s


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


# =========================================================================
# SAYFA ÜRETİCİLER
# =========================================================================

def seg_dir(lang):
    return 'segment'


def msg_dir(lang):
    return 'message'


def gd_dir(lang):
    return 'guide'


def base(lang):
    return '/edi/' if lang == 'tr' else '/edi/en/'


def outdir(lang):
    return OUT if lang == 'tr' else os.path.join(OUT, 'en')


def depth(lang):
    return 2 if lang == 'tr' else 3   # edi/segment/x.html -> ../../


def guide_slug(g, lang):
    return g['slug'] if lang == 'tr' else g['slug_en']


def build_segment(lang, code, segs, elems, codes, urls):
    ui = C.UI[lang]
    d = C.SEGMENTS.get(code, {})
    loc = d.get(lang, {})
    title_txt = segs[code].title() if segs[code].isupper() else segs[code]
    h1 = f'{code} — {title_txt}'
    purpose = loc.get('purpose')
    desc = purpose[:155] if purpose else f'{code} {ui["segment_of"]}: {title_txt}'

    b = [f'<h1>{esc(h1)}</h1>']
    b.append(f'<div class="updated">EDIFACT {ui["segment_of"]}</div>')
    if purpose:
        b.append(f'<div class="doc-callout"><span class="ico">📘</span><p>{esc(purpose)}</p></div>')

    if d.get('example'):
        b.append(f'<h2>{esc(ui["example"])}</h2>')
        b.append(f'<pre class="doc-code"><code>{esc(d["example"])}</code></pre>')

    rows = elems.get(code, [])
    b.append(f'<h2>{esc(ui["elements"])}</h2>')
    if rows:
        b.append(f'<table class="doc-table"><thead><tr><th>{esc(ui["position"])}</th>'
                 f'<th>{esc(ui["description"])}</th></tr></thead><tbody>')
        for pos, txt in rows:
            b.append(f'<tr><td><code>{pos:02d}</code></td><td>{esc(txt)}</td></tr>')
        b.append('</tbody></table>')
    else:
        b.append(f'<p>{esc(ui["no_elements"])}</p>')

    cl = sorted(codes.get(code, []))
    if cl:
        b.append(f'<h2>{esc(ui["codes"])}</h2>')
        b.append(f'<table class="doc-table"><thead><tr><th>{esc(ui["code"])}</th>'
                 f'<th>{esc(ui["meaning"])}</th></tr></thead><tbody>')
        for c, txt in cl:
            b.append(f'<tr><td><code>{esc(c)}</code></td><td>{esc(txt)}</td></tr>')
        b.append('</tbody></table>')

    if loc.get('note'):
        b.append(f'<h2>{"Dikkat" if lang == "tr" else "Watch out"}</h2>')
        b.append(f'<p>{esc(loc["note"])}</p>')

    b.append(f'<p style="margin-top:30px"><a href="../index.html">&larr; {esc(ui["all_segments"])}</a></p>')

    canon = f'{base(lang)}{seg_dir(lang)}/{code.lower()}.html'
    alt = (f'/edi/en/segment/{code.lower()}.html' if lang == 'tr'
           else f'/edi/segment/{code.lower()}.html')
    rel = (f'../en/segment/{code.lower()}.html' if lang == 'tr'
           else f'../../segment/{code.lower()}.html')
    urls.append(canon)
    write(os.path.join(outdir(lang), seg_dir(lang), f'{code.lower()}.html'),
          page(lang, h1, desc, '\n'.join(b), depth(lang), canon, alt, rel))


def build_message(lang, code, types, urls):
    ui = C.UI[lang]
    d = C.MESSAGES.get(code, {})
    loc = d.get(lang, {})
    title_txt = types[code]
    h1 = f'{code} — {title_txt}'
    used = loc.get('used_for')
    desc = used[:155] if used else title_txt

    b = [f'<h1>{esc(h1)}</h1>']
    b.append(f'<div class="updated">EDIFACT {ui["messages"][:-1] if lang == "en" else "mesaj tipi"}</div>')
    if used:
        b.append(f'<div class="doc-callout"><span class="ico">📄</span><p>{esc(used)}</p></div>')
    if loc.get('sender'):
        b.append(f'<h2>{esc(ui["who_sends"])}</h2><p>{esc(loc["sender"])}</p>')
    if loc.get('body'):
        b.append(md(loc['body']))
    if d.get('flow'):
        b.append(f'<h2>{esc(ui["typical_flow"])}</h2>')
        b.append('<p class="flow">' + ' &rarr; '.join(
            f'<a href="../{seg_dir(lang)}/{s.lower()}.html"><code>{s}</code></a>'
            for s in d['flow']) + '</p>')
    b.append(f'<p style="margin-top:30px"><a href="../index.html">&larr; {esc(ui["all_messages"])}</a></p>')

    canon = f'{base(lang)}{msg_dir(lang)}/{code.lower()}.html'
    alt = (f'/edi/en/message/{code.lower()}.html' if lang == 'tr'
           else f'/edi/message/{code.lower()}.html')
    rel = (f'../en/message/{code.lower()}.html' if lang == 'tr'
           else f'../../message/{code.lower()}.html')
    urls.append(canon)
    write(os.path.join(outdir(lang), msg_dir(lang), f'{code.lower()}.html'),
          page(lang, h1, desc, '\n'.join(b), depth(lang), canon, alt, rel))


def build_guide(lang, g, urls):
    loc = g[lang]
    b = [f'<h1>{esc(loc["title"])}</h1>',
         f'<div class="updated">{esc(loc["summary"])}</div>',
         md(loc['body'])]
    slug = guide_slug(g, lang)
    canon = f'{base(lang)}{gd_dir(lang)}/{slug}.html'
    alt = (f'/edi/en/guide/{g["slug_en"]}.html' if lang == 'tr'
           else f'/edi/guide/{g["slug"]}.html')
    rel = (f'../en/guide/{g["slug_en"]}.html' if lang == 'tr'
           else f'../../guide/{g["slug"]}.html')
    urls.append(canon)
    write(os.path.join(outdir(lang), gd_dir(lang), f'{slug}.html'),
          page(lang, loc['title'], loc['summary'], '\n'.join(b), depth(lang), canon, alt, rel))


def build_hub(lang, segs, types, urls):
    ui = C.UI[lang]
    b = [f'<h1>{esc(ui["hub_title"])}</h1>',
         f'<div class="updated">{esc(ui["hub_tagline"])}</div>']

    b.append(f'<h2>{esc(ui["guides"])}</h2><ul class="link-list">')
    for g in C.GUIDES:
        loc = g[lang]
        b.append(f'<li><a href="{gd_dir(lang)}/{guide_slug(g, lang)}.html">'
                 f'<strong>{esc(loc["title"])}</strong>'
                 f'<span>{esc(loc["summary"])}</span></a></li>')
    b.append('</ul>')

    b.append(f'<h2>{esc(ui["messages"])}</h2><div class="chip-grid">')
    for code in sorted(types):
        if code in C.MESSAGES:
            b.append(f'<a class="chip" href="{msg_dir(lang)}/{code.lower()}.html">'
                     f'<code>{code}</code><span>{esc(types[code])}</span></a>')
    b.append('</div>')

    b.append(f'<h2>{esc(ui["segments"])}</h2><div class="chip-grid">')
    for code in sorted(segs):
        t = segs[code]
        b.append(f'<a class="chip" href="{seg_dir(lang)}/{code.lower()}.html">'
                 f'<code>{code}</code><span>{esc(t.title() if t.isupper() else t)}</span></a>')
    b.append('</div>')

    canon = base(lang) + 'index.html'
    alt = '/edi/en/index.html' if lang == 'tr' else '/edi/index.html'
    rel = 'en/index.html' if lang == 'tr' else '../index.html'
    urls.append(canon)
    write(os.path.join(outdir(lang), 'index.html'),
          page(lang, ui['hub_title'], ui['hub_tagline'], '\n'.join(b),
               1 if lang == 'tr' else 2, canon, alt, rel))


# =========================================================================
# ANA AKIŞ
# =========================================================================

def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    urls = []
    stats = {}
    for lang in LANGS:
        d = load(lang)
        segs, alt_titles, elems, codes, types = collect(d)
        types = {k: v for k, v in types.items() if k in C.MESSAGES}

        # Sayfası olması gereken segmentler: elle içerik yazdıklarımız,
        # eleman/kod verisi olanlar ve mesaj akışlarında adı geçenler.
        flow_codes = {s for m in C.MESSAGES.values() for s in m.get('flow', [])}
        wanted = (set(C.SEGMENTS) | set(elems) | set(codes) | flow_codes) & (
                  set(segs) | set(alt_titles) | set(C.SEGMENTS))
        segs = {c: segs.get(c) or alt_titles.get(c) or c for c in wanted}

        for code in segs:
            build_segment(lang, code, segs, elems, codes, urls)
        for code in types:
            build_message(lang, code, types, urls)
        for g in C.GUIDES:
            build_guide(lang, g, urls)
        build_hub(lang, segs, types, urls)
        stats[lang] = (len(segs), len(types), len(C.GUIDES))

    # sitemap + robots
    today = date.today().isoformat()
    extra = ['/index.html', '/gizlilik.html', '/privacy.html']
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in extra + sorted(urls):
        loc = SITE + ('/' if u == '/index.html' else u)
        sm.append(f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>')
    sm.append('</urlset>')
    write(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(sm) + '\n')
    write(os.path.join(ROOT, 'robots.txt'),
          f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')

    total = len(urls)
    for lang, (s, m, g) in stats.items():
        print(f'  {lang}: {s} segment + {m} mesaj tipi + {g} rehber')
    print(f'  sitemap.xml: {total + len(extra)} URL')
    print(f'  TOPLAM {total} sayfa uretildi -> edi/')


if __name__ == '__main__':
    main()
