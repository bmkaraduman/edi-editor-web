"""Awin product-feed connector (Etsy, OTTO, Fnac, Cdiscount, Coolblue, Thalia,
Douglas, Nature & Découvertes ...).

Awin's "Create-a-Feed" gives a CSV download URL. Two ways to configure it:
  AWIN_FEED_<merchant_id>=<url>   one feed per merchant, e.g. AWIN_FEED_otto=...
  AWIN_FEED_ALL_<CC>=<url>        one combined feed with several advertisers for a
                                  country, e.g. AWIN_FEED_ALL_DE=...; rows are split by
                                  the feed's merchant_id column (matched to config `mid`,
                                  unknown advertisers become "awin_<id>" merchants)
AWIN_AFFILIATE_ID is used for click tracking of products without a deep link.
The feed's `aw_deep_link` is already a tracked URL, so it is kept as the product URL.
"""
import csv
import gzip
import io
import os

import requests

from ..config import COUNTRIES, MERCHANTS
from .base import Product, Source
from .csv_feed import parse_price, pick


class AwinSource(Source):
    name = "awin"

    def __init__(self, country):
        super().__init__(country)
        self.feeds = {m["id"]: os.environ.get(f"AWIN_FEED_{m['id']}")
                      for m in MERCHANTS[country] if m["network"] == "awin"}
        self.feeds = {k: v for k, v in self.feeds.items() if v}
        combined = os.environ.get(f"AWIN_FEED_ALL_{country}")
        if combined:
            self.feeds["*"] = combined
        self.by_mid = {m["mid"]: m["id"] for m in MERCHANTS[country] if m["network"] == "awin"}

    def available(self):
        return bool(self.feeds)

    def fetch(self, queries, limit=50):
        cinfo = COUNTRIES[self.country]
        words = {w for q in queries for w in q.lower().split()}
        for feed_merchant, url in self.feeds.items():
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            raw = r.content
            if url.endswith(".gz") or raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            n = 0
            for row in csv.DictReader(io.StringIO(raw.decode("utf-8", "ignore"))):
                title = pick(row, "product_name", "title")
                desc = pick(row, "description", "product_short_description")
                if feed_merchant == "*":
                    mid = pick(row, "merchant_id", "merchant_product_id_source")
                    merchant_id = self.by_mid.get(str(mid), f"awin_{mid}" if mid else "awin_unknown")
                else:
                    merchant_id = feed_merchant
                text = f"{title} {desc}".lower()
                if not any(w in text for w in words):
                    continue
                price = parse_price(pick(row, "search_price", "store_price", "price", "sale_price"))
                if price is None:
                    continue
                yield Product(
                    id=Product.make_id(merchant_id, pick(row, "aw_product_id", "merchant_product_id", "id")),
                    country=self.country, lang=cinfo["lang"], merchant_id=merchant_id, title=title,
                    description=desc, price=price, currency=pick(row, "currency") or cinfo["currency"],
                    url=pick(row, "aw_deep_link", "link", "merchant_deep_link"),
                    image=pick(row, "merchant_image_url", "image_link", "aw_image_url"),
                    brand=pick(row, "brand_name", "brand"), category=pick(row, "merchant_category", "product_type", "category_name"),
                    source="awin", merchant_name=pick(row, "merchant_name"),
                )
                n += 1
                if n >= limit:
                    break
