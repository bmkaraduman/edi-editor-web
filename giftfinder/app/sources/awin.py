"""Awin product-feed connector (Etsy, OTTO, Fnac, Cdiscount, Coolblue, Thalia,
Douglas, Nature & Découvertes ...).

Awin's "Create-a-Feed" gives a CSV download URL per advertiser. Set
  AWIN_FEED_<merchant_id>=<url>   e.g. AWIN_FEED_otto=https://productdata.awin.com/...
and AWIN_AFFILIATE_ID for click tracking. The feed already contains
`aw_deep_link`, which is a tracked URL, so we keep it as the product URL.
"""
import csv
import gzip
import io
import os

import requests

from ..config import COUNTRIES, MERCHANTS
from .base import Product, Source
from .csv_feed import pick


class AwinSource(Source):
    name = "awin"

    def __init__(self, country):
        super().__init__(country)
        self.feeds = {m["id"]: os.environ.get(f"AWIN_FEED_{m['id']}")
                      for m in MERCHANTS[country] if m["network"] == "awin"}
        self.feeds = {k: v for k, v in self.feeds.items() if v}

    def available(self):
        return bool(self.feeds)

    def fetch(self, queries, limit=50):
        cinfo = COUNTRIES[self.country]
        words = {w for q in queries for w in q.lower().split()}
        for merchant_id, url in self.feeds.items():
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            raw = r.content
            if url.endswith(".gz") or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            n = 0
            for row in csv.DictReader(io.StringIO(raw.decode("utf-8", "ignore"))):
                title = pick(row, "product_name", "title")
                desc = pick(row, "description", "product_short_description")
                text = f"{title} {desc}".lower()
                if not any(w in text for w in words):
                    continue
                price = pick(row, "search_price", "store_price", "price")
                try:
                    price = float(str(price).replace(",", "."))
                except (TypeError, ValueError):
                    continue
                yield Product(
                    id=Product.make_id(merchant_id, pick(row, "aw_product_id", "merchant_product_id")),
                    country=self.country, lang=cinfo["lang"], merchant_id=merchant_id, title=title,
                    description=desc, price=price, currency=pick(row, "currency") or cinfo["currency"],
                    url=pick(row, "aw_deep_link", "merchant_deep_link"),
                    image=pick(row, "merchant_image_url", "aw_image_url"),
                    brand=pick(row, "brand_name"), category=pick(row, "merchant_category", "category_name"),
                    source="awin",
                )
                n += 1
                if n >= limit:
                    break
