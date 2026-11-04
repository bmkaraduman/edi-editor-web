import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data.rules import match_rules  # noqa: E402
from app.ml.labeling import label_product, strong_text  # noqa: E402
from app.ml.search import dedupe_key  # noqa: E402
from app.main import engine  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
client = TestClient(app)


def test_category_rules_beat_description_noise():
    # scent notes mention tea, but the category says perfume
    labels = label_product(engine, "Black Opium – 2 ml Parfümprobe", "Kopfnoten: Kaffee, schwarzer Tee und Jasmin.",
                           {"category": "Fragrances > Perfume Samples & Decants"})
    assert "wellness" in labels["personality"] and "coffee_tea" not in labels["personality"]
    # strong-field cues decide gender, generic text does not
    labels = label_product(engine, "Socken aus Baumwolle – Beige", "Laserschnitt-Technik ohne Nähte.", {"category": "Herrensocken"})
    assert labels["gender"] == ["male"] and "tech" not in labels["personality"]


def test_office_stock_is_not_a_gift_but_a_pen_set_is():
    _, rules, gift = match_rules(strong_text("FRANKEN Weißwandtafel", category="office supplies"))
    assert "office" in rules and gift < 0.15
    _, rules, gift = match_rules(strong_text("PARKER Schreibgeräte-Set IM", category="office supplies"))
    assert "writing_set" in rules and gift >= 0.9
    _, rules, gift = match_rules(strong_text("Graue Glasflasche", category="Home & Garden, Bathroom Accessories"))
    assert "garden" not in rules


def test_variants_collapse_to_one_listing():
    a = dedupe_key({"title": "Socken aus Baumwolle – Beige – 43-46", "merchant_id": "m"})
    b = dedupe_key({"title": "Socken aus Baumwolle – Schwarz – 39-42", "merchant_id": "m"})
    c = dedupe_key({"title": "Dior Homme – 8 ml Parfüm-Abfüllung", "merchant_id": "m"})
    assert a == b != c
    assert dedupe_key({"title": "x", "merchant_id": "m", "concept_id": "mug"}) == "concept:mug"


def test_results_never_repeat_and_always_have_a_picture_when_real_products_exist():
    r = client.get("/api/search", params={"country": "DE", "gender": "female", "occasion": "birthday", "limit": 60}).json()
    assert not r["demo"]
    keys = [dedupe_key(engine.by_id[x["id"]]) for x in r["results"]]
    assert len(keys) == len(set(keys))
    assert all(x["image"] for x in r["results"])
    # office stock never surfaces through filters alone, only through a typed search
    assert not any("Patchkabel" in x["title"] for x in r["results"])
    typed = client.get("/api/search", params={"country": "DE", "q": "patchkabel cat7", "limit": 5}).json()
    assert any("Patchkabel" in x["title"] for x in typed["results"])


def test_product_page_and_similar():
    hit = client.get("/api/search", params={"country": "DE", "q": "dior homme", "limit": 1}).json()["results"][0]
    d = client.get(f"/api/product/{hit['id']}").json()
    assert d["images"] and d["brand"] and d["labels"]["gender"][0]["id"] == "male"
    assert d["similar"] and all(s["id"] != d["id"] for s in d["similar"])
    assert all("Scento" in s["merchant"] or "Parf" in s["title"] for s in d["similar"][:3])
    page = client.get(f"/p/{hit['id']}")
    assert page.status_code == 200 and "Dior Homme" in page.text and "og:image" in page.text
    assert client.get("/api/product/nope").status_code == 404


def test_upcoming_occasion_and_active_countries():
    import datetime as dt
    from app.occasions import upcoming, fathers_day
    assert fathers_day(2026, "DE") == dt.date(2026, 5, 14)          # Christi Himmelfahrt
    u = upcoming("DE", dt.date(2026, 11, 3))
    assert u["occasion"] == "christmas" and u["date"] == "2026-12-24" and u["days"] == 51
    r = client.get("/api/upcoming", params={"country": "DE"}).json()
    assert r["label"] and r["results"] and all(x["image"] for x in r["results"])
    assert set(client.get("/api/countries").json()) == {"DE", "NL", "FR", "US"}     # TR waits for a feed
    nl = upcoming("NL", dt.date(2026, 11, 3))
    assert nl["date"] == "2026-12-05" and upcoming("NL", dt.date(2026, 12, 6))["date"] == "2026-12-24"   # Sinterklaas, then Kerst


def test_same_article_from_two_shops_is_one_listing():
    from app.ml.search import dedupe_keys
    a = dedupe_keys({"title": "Holly Jolly Kerstmis Kerstsok met Sneeuw", "merchant_id": "awin_38874", "image": "https://a/1.jpg"})
    b = dedupe_keys({"title": "Holly Jolly Kerstmis Kerstsok met Sneeuw", "merchant_id": "awin_69308", "image": "https://b/1.jpg"})
    c = dedupe_keys({"title": "Carolina Herrera 212 Women Eau de Toilette 100 ml", "merchant_id": "awin_69308", "image": "https://b/2.jpg"})
    assert a & b and not (a & c)


def test_same_picture_or_family_is_one_listing_and_shops_are_capped():
    from app.ml.search import dedupe_keys, MERCHANT_CAP, BLOCK
    a = dedupe_keys({"title": "Chateau Purcari Pinot Noir 2024", "merchant_id": "w", "image": "https://i/1.jpg"})
    b = dedupe_keys({"title": "Chateau Purcari Rose 2025", "merchant_id": "w", "image": "https://i/2.jpg"})
    c = dedupe_keys({"title": "LED Neon Flex 16x16", "merchant_id": "w", "image": "https://i/3.jpg"})
    d = dedupe_keys({"title": "LED Einbaustrahler 6W", "merchant_id": "w", "image": "https://i/3.jpg"})
    assert a & b and not (a & c) and c & d          # family / nothing shared / same photo
    r = client.get("/api/search", params={"country": "DE", "occasion": "christmas", "limit": 36}).json()["results"]
    for start in range(0, len(r), BLOCK):
        block = r[start:start + BLOCK]
        for m in {x["merchant"] for x in block}:
            assert sum(x["merchant"] == m for x in block) <= MERCHANT_CAP
    up = client.get("/api/upcoming", params={"country": "DE", "limit": 8}).json()["results"]
    fams = [" ".join(x["title"].lower().split()[:2]) for x in up]
    assert len(fams) == len(set(fams))


def test_broken_picture_report_hides_the_product():
    hit = client.get("/api/search", params={"country": "DE", "q": "wein", "limit": 1}).json()["results"][0]
    try:
        assert client.post(f"/api/broken/{hit['id']}").json()["hidden"] is True
        assert client.post(f"/api/broken/{hit['id']}").json()["hidden"] is False      # idempotent
        assert client.get(f"/api/product/{hit['id']}").status_code == 200              # detail still answers
        ids = [x["id"] for x in client.get("/api/search", params={"country": "DE", "q": "wein", "limit": 5}).json()["results"]]
        assert hit["id"] not in ids
    finally:
        engine.hidden.discard(hit["id"]); engine.visible[engine.pos[hit["id"]]] = True
        import os; from app.ml.search import HIDDEN_FILE
        if os.path.exists(HIDDEN_FILE):
            os.remove(HIDDEN_FILE)
