import csv
import gzip
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.sources.awin import AwinSource  # noqa: E402

COLUMNS = ["aw_deep_link", "product_name", "aw_product_id", "description", "search_price",
           "merchant_name", "merchant_id", "currency", "merchant_image_url", "alternate_image", "brand_name", "rrp_price", "category_id", "merchant_category"]


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
        rows.append({"aw_deep_link": f"https://awin1.com/{i}", "product_name": f"Kaffeebecher {i}",
                     "aw_product_id": str(i), "description": "Geschenk fürs Büro" if i % 30 == 0 else "Becher fürs Büro",
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
    assert all(p.image for p in products) and all(p.title != "Kaffeebecher 7" for p in products)   # no picture, no listing
    assert {p.title for p in by_merchant["awin_15079"]} != {f"Kaffeebecher {i}" for i in range(50)}
    otto = by_merchant["otto"][0]
    assert otto.price == 49.9 and otto.url.startswith("https://awin1.com/") and otto.merchant_name == "OTTO"
    assert otto.images == ["https://img/otto-2.jpg"] and otto.brand == "DeLonghi" and otto.rrp == 79.9
    assert all(p.title != "Ohne Preis" for p in products)


def test_google_format_feed_next_to_awin_feed(tmp_path, monkeypatch):
    """A country can list several feeds; Google-format feeds (BOM, advertiser_id, sale_price) parse too."""
    awin = tmp_path / "nl.csv.gz"
    write_feed(awin, [{"aw_deep_link": "https://awin1.com/s", "product_name": "Cadeau sokken", "aw_product_id": "s1",
                       "description": "Leuk cadeau", "search_price": "12.95", "merchant_name": "Sokken-Online",
                       "merchant_id": "128517", "currency": "EUR", "merchant_image_url": "https://img/s.jpg"}])
    google = tmp_path / "tulip.csv"
    google.write_text("﻿advertiser_id,advertiser_name,id,title,description,link,image_link,additional_image_link,"
                      "aw_deep_link,product_type,brand,price,sale_price\n"
                      '130659,TulipArt,t1,Tulpen schilderij,"Mooi cadeau voor moeder",https://shop/t1,https://img/t1.jpg,'
                      '"https://img/t1b.jpg,https://img/t1c.jpg",https://awin1.com/t1,Kunst > Schilderijen,TulipArt,59.00 EUR,39.00 EUR\n',
                      encoding="utf-8")
    monkeypatch.setenv("AWIN_FEED_ALL_NL", f"{awin} {google}")

    products = {p.merchant_id: p for p in AwinSource("NL").fetch(["cadeau"], limit=10)}
    assert set(products) == {"awin_128517", "awin_130659"}
    tulip = products["awin_130659"]
    assert tulip.merchant_name == "TulipArt" and tulip.url == "https://awin1.com/t1"
    assert tulip.price == 39.0 and tulip.rrp == 59.0
    assert tulip.images == ["https://img/t1b.jpg", "https://img/t1c.jpg"] and tulip.product_type == "Kunst > Schilderijen"


def test_non_gifts_never_enter_the_catalog(tmp_path, monkeypatch):
    """Rows in a never-a-present Awin category, or hit by a "not a present" rule, are skipped."""
    base = {"search_price": "9.95", "merchant_name": "Shop", "merchant_id": "1", "currency": "EUR", "description": "cadeau"}
    rows = [dict(base, aw_deep_link="https://awin1.com/1", product_name="Mok met naam", aw_product_id="1", merchant_image_url="https://img/1.jpg", category_id="596"),
            dict(base, aw_deep_link="https://awin1.com/2", product_name="Spaanplaatschroeven 4x40", aw_product_id="2", merchant_image_url="https://img/2.jpg"),
            dict(base, aw_deep_link="https://awin1.com/3", product_name="Keukenkraan RVS", aw_product_id="3", merchant_image_url="https://img/3.jpg", merchant_category="Badkamer"),
            dict(base, aw_deep_link="https://awin1.com/4", product_name="Cadeau sokken", aw_product_id="4", merchant_image_url="https://img/4.jpg", category_id="161")]
    feed = tmp_path / "nl.csv.gz"
    write_feed(feed, rows)
    monkeypatch.setenv("AWIN_FEED_ALL_NL", str(feed))
    assert [p.title for p in AwinSource("NL").fetch(["cadeau"], limit=10)] == ["Cadeau sokken"]
