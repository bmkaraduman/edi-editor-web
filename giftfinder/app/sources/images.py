"""Image verification: a feed row may carry an image URL that no longer resolves
(Shopify rotates product photos, shops delete listings). Rule: a product is only
listed when its picture really loads, so every candidate image is fetched once at
ingest time and broken ones are dropped. Gallery images that fail are removed; a
product whose main image fails is skipped (the first working gallery image takes
over when there is one).

Set VERIFY_IMAGES=0 to skip (offline tests / dry runs)."""
import os
from concurrent.futures import ThreadPoolExecutor

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; giftdetect.com feed check)", "Accept": "image/*,*/*;q=0.5"}


def image_ok(url, timeout=12):
    """True when the URL answers 200 with an image content type."""
    if not url or not url.startswith(("http://", "https://")):
        return False
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True, allow_redirects=True)
        ctype = r.headers.get("content-type", "").lower()
        ok = r.status_code == 200 and ("image" in ctype or ctype == "application/octet-stream")
        if ok:
            ok = len(r.raw.read(64) or b"") > 0     # a 200 with an empty body is no picture either
        r.close()
        return ok
    except requests.RequestException:
        return False


def verify_images(products, workers=32, log=print):
    """Filter a list of Product objects to those with a working main image."""
    if os.environ.get("VERIFY_IMAGES", "1") == "0":
        return products
    urls = {}
    for p in products:
        for u in [p.image] + list(p.images):
            if u:
                urls.setdefault(u, None)
    log(f"  checking {len(urls)} image urls for {len(products)} products ...")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for u, ok in zip(urls, pool.map(image_ok, urls)):
            urls[u] = ok
    kept = []
    for p in products:
        candidates = [u for u in [p.image] + list(p.images) if u and urls.get(u)]
        if not candidates:
            continue
        p.image, p.images = candidates[0], candidates[1:]
        kept.append(p)
    log(f"  {len(kept)} products with a working picture ({len(products) - len(kept)} dropped)")
    return kept
