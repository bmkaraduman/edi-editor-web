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

A combined feed can hold hundreds of thousands of rows from shops that mostly
sell non-gifts (office supplies, network cables ...). The download is streamed
and every advertiser gets at most `limit` products, picked by reservoir
sampling so the catalog gets a spread of each shop's range instead of its first
rows; rows whose text mentions a gift word ("Geschenk", "gift", "cadeau" ...)
are preferred.
"""
import csv
import gzip
import io
import os
import random

import requests

from ..config import COUNTRIES, GIFT_WORDS, MERCHANTS
from .base import Product, Source
from .csv_feed import parse_price, pick

csv.field_size_limit(1 << 30)     # some advertisers ship 25k-character descriptions
MAX_DESCRIPTION = 2000


def open_feed(url, timeout=120):
    """Stream a Create-a-Feed URL (or a local path) as decoded text, gunzipping on the fly."""
    if os.path.exists(url):
        buf = open(url, "rb")
    else:
        r = requests.get(url, stream=True, timeout=timeout)
        r.raise_for_status()
        r.raw.decode_content = True
        buf = io.BufferedReader(r.raw, 1 << 20)
    if buf.peek(2)[:2] == b"\x1f\x8b":
        buf = gzip.GzipFile(fileobj=buf)
    return io.TextIOWrapper(buf, encoding="utf-8", errors="ignore", newline="")


class Reservoir:
    """Keep a uniform random sample of at most `cap` items from a stream."""

    def __init__(self, cap, rng):
        self.cap, self.rng, self.items, self.seen = cap, rng, [], 0

    def add(self, item):
        self.seen += 1
        if len(self.items) < self.cap:
            self.items.append(item)
        else:
            j = self.rng.randrange(self.seen)
            if j < self.cap:
                self.items[j] = item


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
        """Yield up to `limit` products per advertiser from every configured feed."""
        cinfo = COUNTRIES[self.country]
        words = {w for q in queries for w in q.lower().split()}
        gift_words = GIFT_WORDS.get(cinfo["lang"], []) + GIFT_WORDS["en"]
        rng = random.Random(7)
        for feed_merchant, url in self.feeds.items():
            # merchant -> (rows mentioning a gift word, other matching rows)
            pools = {}
            for row in csv.DictReader(open_feed(url)):
                title = pick(row, "product_name", "title")
                desc = pick(row, "description", "product_short_description")
                image = pick(row, "merchant_image_url", "image_link", "aw_image_url", "large_image")
                if not title or not image:          # rule: a product without a picture is never shown
                    continue
                if feed_merchant == "*":
                    mid = pick(row, "merchant_id", "merchant_product_id_source")
                    merchant_id = self.by_mid.get(str(mid), f"awin_{mid}" if mid else "awin_unknown")
                else:
                    merchant_id = feed_merchant
                keywords = pick(row, "keywords")
                category = pick(row, "merchant_category", "category_name")
                category_path = pick(row, "merchant_product_category_path")
                product_type = pick(row, "product_type")
                text = f"{title} {desc} {keywords} {category} {category_path} {product_type}".lower()
                if not any(w in text for w in words):
                    continue
                price = parse_price(pick(row, "search_price", "store_price", "price", "sale_price"))
                if price is None:
                    continue
                rrp = parse_price(pick(row, "rrp_price", "product_price_old")) or 0.0
                images = []
                for col in ("large_image", "alternate_image", "alternate_image_two", "alternate_image_three", "alternate_image_four"):
                    u = pick(row, col)
                    if u and u != image and u not in images:
                        images.append(u)
                details = {k: pick(row, c) for k, c in (
                    ("colour", "colour"), ("condition", "condition"), ("model", "product_model"),
                    ("dimensions", "dimensions"), ("specifications", "specifications"),
                    ("delivery_cost", "delivery_cost"), ("promotion", "promotional_text"),
                    ("short_description", "product_short_description"))}
                details = {k: v[:400] for k, v in details.items() if v}
                product = Product(
                    id=Product.make_id(merchant_id, pick(row, "aw_product_id", "merchant_product_id", "id")),
                    country=self.country, lang=cinfo["lang"], merchant_id=merchant_id, title=title,
                    description=desc[:MAX_DESCRIPTION], price=price, currency=pick(row, "currency") or cinfo["currency"],
                    url=pick(row, "aw_deep_link", "link", "merchant_deep_link"), image=image,
                    brand=pick(row, "brand_name", "brand"), category=category,
                    source="awin", merchant_name=pick(row, "merchant_name"),
                    images=images, keywords=keywords, category_path=category_path, product_type=product_type,
                    rrp=rrp if rrp > price else 0.0, details=details,
                )
                if merchant_id not in pools:
                    pools[merchant_id] = (Reservoir(limit, rng), Reservoir(limit, rng))
                tier = 0 if any(g in text for g in gift_words) else 1
                pools[merchant_id][tier].add(product)
            for merchant_id, (gifts, rest) in pools.items():
                chosen = gifts.items + rest.items[:max(0, limit - len(gifts.items))]
                print(f"  awin {merchant_id}: {len(chosen)} of {gifts.seen + rest.seen} matching rows ({gifts.seen} mention a gift word)")
                yield from chosen
