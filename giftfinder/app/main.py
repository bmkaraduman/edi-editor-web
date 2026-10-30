"""FastAPI application: JSON search API, affiliate redirect and the web UI.

    uvicorn app.main:app --reload
"""
import json
import os
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import COUNTRIES, MERCHANTS, affiliate_link
from .ml.search import GiftSearch, facet_options
from .taxonomy import FACET_TITLES

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
CLICK_LOG = os.path.join(HERE, "data", "clicks.jsonl")

app = FastAPI(title="GiftFinder", version="1.0")
engine = GiftSearch()


@app.get("/api/countries")
def countries():
    return {cc: {"name": c["name"], "lang": c["lang"], "currency": c["currency"], "flag": c["flag"],
                 "merchants": [m["name"] for m in MERCHANTS[cc]]} for cc, c in COUNTRIES.items()}


@app.get("/api/options")
def options(lang: str = "en"):
    return {"facets": facet_options(lang), "titles": {k: v.get(lang, k) for k, v in FACET_TITLES.items()}}


@app.get("/api/search")
def search(country: str, q: str = "", gender: Optional[str] = None,
           age: List[str] = Query(default=[]), occasion: List[str] = Query(default=[]),
           personality: List[str] = Query(default=[]),
           price_min: Optional[float] = None, price_max: Optional[float] = None,
           limit: int = 24, offset: int = 0):
    try:
        return engine.search(country, q=q, gender=gender, age=age, occasion=occasion,
                             personality=personality, price_min=price_min, price_max=price_max,
                             limit=min(limit, 60), offset=offset)
    except ValueError as e:
        raise HTTPException(400, str(e))


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


@app.get("/")
def index():
    return FileResponse(os.path.join(WEB, "index.html"))


app.mount("/static", StaticFiles(directory=WEB), name="static")
