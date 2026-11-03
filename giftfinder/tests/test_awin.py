import csv
import gzip
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.sources.awin import AwinSource  # noqa: E402

COLUMNS = ["aw_deep_link", "product_name", "aw_product_id", "description", "search_price",
           "merchant_name", "merchant_id", "currency", "merchant_image_url", "alternate_image", "brand_name", "rrp_price"]


def write_feed(path, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(rows)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write(buf.getvalue())


def test_combined_feed_samples_per_merchant_and_prefers_gifts(tmp_path, monkeypatch):
    rows = []
    for i in range(300):                      # big shop: 300 matching rows, 10 mention "Geschenk"
        rows.append({"aw_deep_link": f"https://awin1.com/{i}", "product_name": f"Whiteboard {i}",
                     "aw_product_id": str(i), "description": "Geschenk fürs Büro" if i % 30 == 0 else "Tafel fürs Büro",
                     "search_price": "9.99", "merchant_name": "Big Shop", "merchant_id": "15079", "currency": "EUR",
                     "merchant_image_url": f"https://img/{i}.jpg" if i != 7 else ""})
    rows.append({"aw_deep_link": "https://awin1.com/otto", "product_name": "Kaffeemaschine", "aw_product_id": "o1",
                 "description": "Geschenk für Kaffee Liebhaber", "search_price": "49,90", "merchant_name": "OTTO",
                 "merchant_id": "14336", "currency": "EUR", "merchant_image_url": "https://img/otto.jpg",
                 "alternate_image": "https://img/otto-2.jpg", "brand_name": "DeLonghi", "rrp_price": "79.90"})
    rows.append({"aw_deep_link": "https://awin1.com/x", "product_name": "Ohne Preis", "aw_product_id": "x1",
                 "description": "Geschenk", "search_price": "", "merchant_name": "Big Shop", "merchant_id": "15079", "currency": "EUR", "merchant_image_url": "https://img/x.jpg"})
    feed = tmp_path / "de.csv.gz"
    write_feed(feed, rows)
    monkeypatch.setenv("AWIN_FEED_ALL_DE", str(feed))

    src = AwinSource("DE")
    assert src.available()
    products = list(src.fetch(["geschenk", "büro kaffee"], limit=50))

    by_merchant = {}
    for p in products:
        by_merchant.setdefault(p.merchant_id, []).append(p)
    assert set(by_merchant) == {"awin_15079", "otto"}          # known mid -> config id, unknown -> awin_<mid>
    assert len(by_merchant["awin_15079"]) == 50                 # capped per advertiser, not first-N
    assert sum("Geschenk" in p.description for p in by_merchant["awin_15079"]) == 10   # gift rows always kept
    assert all(p.image for p in products) and all(p.title != "Whiteboard 7" for p in products)   # no picture, no listing
    assert {p.title for p in by_merchant["awin_15079"]} != {f"Whiteboard {i}" for i in range(50)}
    otto = by_merchant["otto"][0]
    assert otto.price == 49.9 and otto.url.startswith("https://awin1.com/") and otto.merchant_name == "OTTO"
    assert otto.images == ["https://img/otto-2.jpg"] and otto.brand == "DeLonghi" and otto.rrp == 79.9
    assert all(p.title != "Ohne Preis" for p in products)
