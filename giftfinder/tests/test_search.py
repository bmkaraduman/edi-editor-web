import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.config import affiliate_link
from app.ml.labeling import label_product
from app.ml.weak_labels import weak_labels
from app.main import app, engine

client = TestClient(app)


def test_weak_labels_turkish():
    labels = weak_labels("Babalar günü için mangal seti, kamp ve doğa severlere")
    assert "fathers_day" in labels["occasion"]
    assert "foodie" in labels["personality"] or "outdoor" in labels["personality"]


def test_classifier_generalises_to_unseen_text():
    labels = label_product(engine, "Casque audio Bluetooth pour les amateurs de musique", "Idéal pour la fête des pères.")
    assert "music" in labels["personality"] or "tech" in labels["personality"]
    assert "fathers_day" in labels["occasion"]


@pytest.mark.parametrize("country", ["US", "DE", "TR", "NL", "FR"])
def test_search_each_country(country):
    r = client.get("/api/search", params={"country": country, "gender": "male", "occasion": "fathers_day", "personality": "outdoor"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    top = data["results"][0]
    assert top["merchant"] and top["price_text"] and top["link"].startswith("/go/")


def test_free_text_hint_drives_ranking():
    r = client.get("/api/search", params={"country": "US", "q": "my dad who loves fishing"}).json()
    titles = " ".join(x["title"].lower() for x in r["results"][:5])
    assert "fishing" in titles or "bbq" in titles or "multi-tool" in titles


def test_budget_filter():
    r = client.get("/api/search", params={"country": "TR", "price_max": 800}).json()
    assert all(x["price"] <= 800 for x in r["results"])


def test_redirect_goes_to_merchant():
    pid = engine.products[0]["id"]
    r = client.get(f"/go/{pid}", follow_redirects=False)
    assert r.status_code == 302
    assert "http" in r.headers["location"]


def test_affiliate_link_wraps_when_configured(monkeypatch):
    monkeypatch.setenv("AMAZON_TAG_DE", "test-21")
    assert "tag=test-21" in affiliate_link("amazon_de", query="Geschenk")
    monkeypatch.setenv("AWIN_AFFILIATE_ID", "12345")
    assert "awin1.com" in affiliate_link("otto", product_url="https://www.otto.de/p/1")
