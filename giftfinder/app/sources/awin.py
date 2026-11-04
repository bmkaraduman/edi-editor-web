"""Awin product-feed connector (Etsy, OTTO, Fnac, Cdiscount, Coolblue, Thalia,
Douglas, Nature & Découvertes ...).

Awin's "Create-a-Feed" gives a CSV download URL. Two ways to configure it:
  AWIN_FEED_<merchant_id>=<url>   one feed per merchant, e.g. AWIN_FEED_otto=...
  AWIN_FEED_ALL_<CC>=<url> [<url> ...]
                                  combined feeds with several advertisers for a country,
                                  separated by spaces (Create-a-Feed URLs contain commas),
                                  e.g. one Awin-format Create-a-Feed URL plus the
                                  Google-format feeds of shops that only offer that format;
                                  rows are split by the merchant_id / advertiser_id column
                                  (matched to config `mid`, unknown advertisers become
                                  "awin_<id>" merchants)
AWIN_AFFILIATE_ID is used for click tracking of products without a deep link.
The feed's `aw_deep_link` is already a tracked URL, so it is kept as the product URL.

A combined feed can hold hundreds of thousands of rows from shops that mostly
sell non-gifts (office supplies, network cables ...). The download is streamed
and every advertiser gets at most `limit` products, picked by reservoir
sampling so the catalog gets a spread of each shop's range instead of its first
rows; rows whose text mentions a gift word ("Geschenk", "gift", "cadeau" ...)
are preferred.

Non-gifts never enter the catalog: rows in an Awin category that is never a present
(NOT_GIFT_CATEGORIES) are skipped, and so are rows whose title / category / keywords
hit a "not a present" rule (screws, taps, cables, spare parts ... see
app/data/rules.py). Create-a-Feed ignores its category filter once advertisers are
picked, so both checks run here.
"""
import csv
import gzip
import html
import io
import os
import random

import requests

from ..config import COUNTRIES, GIFT_WORDS, MERCHANTS
from ..data.rules import GIFT_FLOOR, match_rules
from ..ml.labeling import strong_text
from .base import Product, Source
from .csv_feed import parse_price, pick

csv.field_size_limit(1 << 30)     # some advertisers ship 25k-character descriptions
MAX_DESCRIPTION = 2000

# Awin taxonomy ids (category_id column) of ranges that are never a present.
NOT_GIFT_CATEGORIES = {
    596: "Office Supplies", 209: "Printer Consumables", 210: "Printers", 211: "Scanners", 68: "Software",
    130: "Cables", 537: "Cables, Parts & Power Supplies", 62: "Computer Components", 71: "CPUs", 75: "Graphics Cards",
    603: "RAM", 69: "Storage Media", 220: "Hard Drives", 226: "Networking", 224: "Bluetooth Adapters", 228: "Wireless Adapters",
    65: "Input Devices", 85: "Monitors", 83: "Computers", 84: "Laptops", 64: "Hardware", 348: "Mobile Phones",
    349: "Other Telephones", 358: "House Telephones", 360: "Video Conferencing", 86: "Headsets", 475: "Home Security",
    563: "In-Car Entertainment", 633: "Appliance Spares", 375: "Vacuum Cleaners", 616: "Cleaning",
    121: "Health", 594: "Oral Health", 123: "Nutrition", 125: "Vitamins & Supplements", 127: "Diet", 255: "Support Aids",
    422: "Bathrooms & Accessories", 436: "Bespoke Bathrooms", 426: "General Household", 470: "House Accessories",
    450: "Tables", 448: "Chairs", 449: "Sofas", 424: "Furniture", 452: "Storage", 469: "Furniture Accessories",
    459: "Garden Tools", 425: "Garden", 457: "Garden & Leisure", 458: "Sheds & Garden Furniture", 428: "DIY",
}


def is_gift(product):
    """False when a "not a present" rule decides the product (gift prior below GIFT_FLOOR)."""
    strong = strong_text(product.title, product.keywords, product.category, product.category_path, product.product_type, product.brand)
    return match_rules(strong)[2] >= GIFT_FLOOR


def open_feed(url, timeout=120):
    """Stream a Create-a-Feed URL (or a local path) as decoded text, gunzipping on the fly."""
    if os.path.exists(url):
        buf = open(url, "rb")
    else:
        r = requests.get(url, stream=True, timeout=timeout)
        r.raise_for_status()
        r.raw.decode_content = True
        r.raw.auto_close = False      # gzip peeks past the last member; a closed stream would raise
        buf = io.BufferedReader(r.raw, 1 << 20)
    if buf.peek(2)[:2] == b"\x1f\x8b":
        buf = gzip.GzipFile(fileobj=buf)
    return io.TextIOWrapper(buf, encoding="utf-8-sig", errors="ignore", newline="")   # Google-format feeds start with a BOM


class Reservoir:
    """Keep a uniform random sample of at most `cap` items from a stream."""

    def __init__(self, cap, rng):
        self.cap, self.rng, self.items, self.seen = cap, rng, [], 0

    def add(self, item, keep=None):
        """`keep(item)` is only asked when the item would enter the sample (it can be
        slow); a rejected item leaves the slot as it was, so the sample stays uniform
        over the kept items."""
        self.seen += 1
        if len(self.items) < self.cap:
            if keep is None or keep(item):
                self.items.append(item)
        else:
            j = self.rng.randrange(self.seen)
            if j < self.cap and (keep is None or keep(item)):
                self.items[j] = item


class AwinSource(Source):
    name = "awin"

    def __init__(self, country):
        super().__init__(country)
        self.feeds = {m["id"]: os.environ.get(f"AWIN_FEED_{m['id']}")
                      for m in MERCHANTS[country] if m["network"] == "awin"}
        self.feeds = {k: v for k, v in self.feeds.items() if v}
        combined = os.environ.get(f"AWIN_FEED_ALL_{country}")
        for i, url in enumerate((combined or "").split()):
            self.feeds[f"*{i}"] = url
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
                title = html.unescape(pick(row, "product_name", "title")).strip()
                desc = html.unescape(pick(row, "description", "product_short_description"))
                image = pick(row, "merchant_image_url", "image_link", "aw_image_url", "large_image")
                if not title or not image:          # rule: a product without a picture is never shown
                    continue
                if pick(row, "category_id").isdigit() and int(pick(row, "category_id")) in NOT_GIFT_CATEGORIES:
                    continue
                if feed_merchant.startswith("*"):
                    mid = pick(row, "merchant_id", "advertiser_id", "merchant_product_id_source")
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
                sale = parse_price(pick(row, "sale_price"))
                if sale and sale < price:          # Google format: price is the list price
                    rrp, price = price, sale
                images = []
                extra = [pick(row, c) for c in ("large_image", "alternate_image", "alternate_image_two", "alternate_image_three", "alternate_image_four")]
                extra += pick(row, "additional_image_link").split(",")     # Google format: comma-separated list
                for u in (x.strip() for x in extra):
                    if u and u != image and u not in images:
                        images.append(u)
                images = images[:6]
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
                    source="awin", merchant_name=pick(row, "merchant_name", "advertiser_name"),
                    images=images, keywords=keywords, category_path=category_path, product_type=product_type,
                    rrp=rrp if rrp > price else 0.0, details=details,
                )
                if merchant_id not in pools:
                    pools[merchant_id] = (Reservoir(limit, rng), Reservoir(limit, rng))
                tier = 0 if any(g in text for g in gift_words) else 1
                pools[merchant_id][tier].add(product, keep=is_gift)
            for merchant_id, (gifts, rest) in pools.items():
                chosen = gifts.items + rest.items[:max(0, limit - len(gifts.items))]
                print(f"  awin {merchant_id}: {len(chosen)} of {gifts.seen + rest.seen} matching rows ({gifts.seen} mention a gift word)")
                yield from chosen
