"""FastAPI application: JSON search API, affiliate redirect and the web UI.

    uvicorn app.main:app --reload
"""
import json
import os
import time
from typing import List, Optional

import html

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import ACTIVE_COUNTRIES, COUNTRIES, GA_MEASUREMENT_ID, MERCHANTS, affiliate_link
from .occasions import upcoming
from .taxonomy import UI_LABELS
from .ml.search import GiftSearch, facet_options
from .taxonomy import FACET_TITLES, clashes
from .i18n import web_script

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
CLICK_LOG = os.path.join(HERE, "data", "clicks.jsonl")

app = FastAPI(title="giftdetect.com", version="1.0")
engine = GiftSearch()


@app.get("/api/countries")
def countries():
    return {cc: {"name": c["name"], "lang": c["lang"], "currency": c["currency"], "flag": c["flag"], "locale": c["locale"],
                 "merchants": [m["name"] for m in MERCHANTS[cc]]} for cc, c in COUNTRIES.items() if cc in ACTIVE_COUNTRIES}


@app.get("/api/geo")
def geo(request: Request):
    """The visitor's country when a CDN in front of the app tells us (Cloudflare's CF-IPCountry)."""
    return {"country": request.headers.get("cf-ipcountry", "")}


@app.get("/api/upcoming")
def upcoming_occasion(country: str, limit: int = 8):
    """The next dated special day of a country and the gifts that fit it (home-page strip)."""
    country = country.upper()
    if country not in COUNTRIES:
        raise HTTPException(400, "unknown country")
    u = upcoming(country)
    u["label"] = UI_LABELS[u["occasion"]].get(u["lang"], u["occasion"])
    u.update(engine.search(country, occasion=[u["occasion"]], limit=min(limit, 24)))
    return u


@app.get("/api/options")
def options(lang: str = "en"):
    return {"facets": facet_options(lang), "titles": {k: v.get(lang, k) for k, v in FACET_TITLES.items()}, "clashes": clashes()}


@app.get("/api/search")
def search(country: str, q: str = "", gender: Optional[str] = None,
           age: List[str] = Query(default=[]), occasion: List[str] = Query(default=[]),
           personality: List[str] = Query(default=[]),
           price_min: Optional[float] = None, price_max: Optional[float] = None,
           limit: int = 36, offset: int = 0, sort: str = "relevance"):
    try:
        return engine.search(country, q=q, gender=gender, age=age, occasion=occasion,
                             personality=personality, price_min=price_min, price_max=price_max,
                             limit=min(limit, 60), offset=offset, sort=sort)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/product/{product_id}")
def product(product_id: str):
    d = engine.product(product_id)
    if d is None:
        raise HTTPException(404, "unknown product")
    return d


@app.post("/api/broken/{product_id}")
def broken_image(product_id: str):
    """The storefront reports a product whose picture failed to load; it is hidden from then on."""
    return {"hidden": engine.hide(product_id)}


@app.get("/api/stats")
def stats():
    report_path = os.path.join(HERE, "data", "models", "report.json")
    report = json.load(open(report_path)) if os.path.exists(report_path) else {}
    per_country = {cc: int((engine.country == cc).sum()) for cc in COUNTRIES}
    return {"products": len(engine.products), "per_country": per_country, "model": report}


@app.get("/go/{product_id}")
def go(product_id: str):
    p = engine.by_id.get(product_id)
    if not p:
        raise HTTPException(404, "unknown product")
    link = affiliate_link(p["merchant_id"], product_url=p.get("url") or None, query=p["title"])
    try:
        with open(CLICK_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": int(time.time()), "id": product_id, "merchant": p["merchant_id"],
                                "country": p["country"]}) + "\n")
    except OSError:
        pass
    return RedirectResponse(link, status_code=302)


def _page(title="giftdetect.com", description="giftdetect.com: a gift search engine. Pick who it is for, the occasion and their personality and get ranked gift ideas from shops in your country.", canonical="https://giftdetect.com/", image=None):
    """Assemble the storefront from the shared fragments in web/."""
    body = open(os.path.join(WEB, "body.html"), encoding="utf-8").read()
    og = f'<meta property="og:image" content="{html.escape(image)}">' if image else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(description)}">{og}
<link rel="canonical" href="{html.escape(canonical)}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700&family=Manrope:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/static/style.css"></head><body>{body}
<script>window.GA_ID={json.dumps(GA_MEASUREMENT_ID)};{web_script()}</script>
<script src="/static/provider_api.js"></script><script src="/static/ui.js"></script><script src="/static/analytics.js"></script></body></html>"""


PAGE_HTML = _page()


@app.get("/")
def index():
    return HTMLResponse(PAGE_HTML)


@app.get("/p/{product_id}")
def product_page(product_id: str):
    """Product detail: same single-page app, with the product's own title/meta for crawlers."""
    p = engine.by_id.get(product_id)
    if p is None:
        raise HTTPException(404, "unknown product")
    m = engine._render(p, 0.0, [], COUNTRIES[p["country"]]["lang"])
    desc = (p.get("details", {}).get("short_description") or p.get("description") or "")[:160]
    return HTMLResponse(_page(title=f"{p['title']} · {m['merchant']} · giftdetect.com", description=desc,
                              canonical=f"https://giftdetect.com/p/{product_id}", image=p.get("image") or None))


app.mount("/static", StaticFiles(directory=WEB), name="static")
