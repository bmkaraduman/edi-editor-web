"""Generic CSV / Google-Shopping-style feed connector.

Covers networks that hand out product feeds as files instead of APIs:
Trendyol and Hepsiburada partner feeds, Gelirortakları, Daisycon, impact.com,
bol.com's product feed, or a feed you export yourself.

Drop the files in feeds/<CC>/<merchant_id>.csv (or set FEED_DIR). Column
names are matched loosely: title/name, description, price, link/url, image.
A CSV downloaded by hand from Awin's Create-a-Feed works as is.
"""
import csv
import glob
import os

from ..config import COUNTRIES, MERCHANT_BY_ID
from .base import Product, Source

FEED_DIR = os.environ.get("FEED_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "feeds"))


def pick(row, *keys):
    low = {k.lower().strip(): v for k, v in row.items() if k}
    for k in keys:
        if k in low and low[k] not in (None, ""):
            return low[k]
    return ""


class CsvFeedSource(Source):
    name = "csv"

    def __init__(self, country):
        super().__init__(country)
        self.files = glob.glob(os.path.join(FEED_DIR, country, "*.csv"))

    def available(self):
        return bool(self.files)

    def fetch(self, queries, limit=50):
        cinfo = COUNTRIES[self.country]
        words = {w for q in queries for w in q.lower().split()}
        for path in self.files:
            merchant_id = os.path.splitext(os.path.basename(path))[0]
            if merchant_id not in MERCHANT_BY_ID:
                print(f"skip {path}: unknown merchant id")
                continue
            with open(path, encoding="utf-8", newline="") as f:
                sample = f.read(4096)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                n = 0
                for row in csv.DictReader(f, dialect=dialect):
                    title = pick(row, "title", "name", "product_name", "urun_adi", "ürün adı")
                    desc = pick(row, "description", "aciklama", "açıklama", "product_description", "product_short_description")
                    text = f"{title} {desc}".lower()
                    if words and not any(w in text for w in words):
                        continue
                    price = pick(row, "price", "sale_price", "search_price", "store_price", "fiyat", "satis_fiyati")
                    try:
                        price = float(str(price).replace("TL", "").replace("₺", "").replace(".", "").replace(",", ".")
                                      if cinfo["currency"] == "TRY" else str(price).replace(",", "."))
                    except (TypeError, ValueError):
                        continue
                    ext = pick(row, "id", "product_id", "aw_product_id", "merchant_product_id", "sku", "urun_kodu", "link", "url")
                    yield Product(
                        id=Product.make_id(merchant_id, ext or title), country=self.country, lang=cinfo["lang"],
                        merchant_id=merchant_id, title=title, description=desc, price=price,
                        currency=cinfo["currency"], url=pick(row, "aw_deep_link", "link", "url", "product_url", "deeplink", "merchant_deep_link"),
                        image=pick(row, "image_link", "image", "image_url", "merchant_image_url", "aw_image_url", "gorsel"),
                        brand=pick(row, "brand", "brand_name", "marka"), category=pick(row, "product_type", "category", "merchant_category", "category_name", "kategori"),
                        source="csv",
                    )
                    n += 1
                    if n >= limit:
                        break
