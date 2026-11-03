"""Amazon Product Advertising API 5.0 connector (US, DE, FR, NL, TR).

Needs an approved Associates account per marketplace:
  AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY and AMAZON_TAG_<CC> (e.g. AMAZON_TAG_DE).
Requests are signed with AWS Signature V4; no SDK needed.
"""
import datetime as dt
import hashlib
import hmac
import json
import os

import requests

from ..config import COUNTRIES
from .base import Product, Source

MARKETPLACES = {
    "US": ("webservices.amazon.com", "us-east-1", "www.amazon.com", "amazon_us"),
    "DE": ("webservices.amazon.de", "eu-west-1", "www.amazon.de", "amazon_de"),
    "FR": ("webservices.amazon.fr", "eu-west-1", "www.amazon.fr", "amazon_fr"),
    "NL": ("webservices.amazon.nl", "eu-west-1", "www.amazon.nl", "amazon_nl"),
    "TR": ("webservices.amazon.com.tr", "eu-west-1", "www.amazon.com.tr", "amazon_tr"),
}


def _sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


class AmazonSource(Source):
    name = "amazon"

    def __init__(self, country):
        super().__init__(country)
        self.access = os.environ.get("AMAZON_ACCESS_KEY", "")
        self.secret = os.environ.get("AMAZON_SECRET_KEY", "")
        self.tag = os.environ.get(f"AMAZON_TAG_{country}", os.environ.get("AMAZON_TAG", ""))
        self.host, self.region, self.site, self.merchant_id = MARKETPLACES[country]

    def available(self):
        return bool(self.access and self.secret and self.tag)

    def _request(self, payload):
        target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"
        path = "/paapi5/searchitems"
        body = json.dumps(payload)
        now = dt.datetime.now(dt.timezone.utc)
        amz_date, date_stamp = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
        headers = {
            "content-encoding": "amz-1.0", "content-type": "application/json; charset=utf-8",
            "host": self.host, "x-amz-date": amz_date, "x-amz-target": target,
        }
        signed = ";".join(sorted(headers))
        canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted(headers))
        canonical = "\n".join(["POST", path, "", canonical_headers, signed, hashlib.sha256(body.encode()).hexdigest()])
        scope = f"{date_stamp}/{self.region}/ProductAdvertisingAPI/aws4_request"
        to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
        k = _sign(("AWS4" + self.secret).encode(), date_stamp)
        k = _sign(k, self.region)
        k = _sign(k, "ProductAdvertisingAPI")
        k = _sign(k, "aws4_request")
        sig = hmac.new(k, to_sign.encode(), hashlib.sha256).hexdigest()
        headers["Authorization"] = (f"AWS4-HMAC-SHA256 Credential={self.access}/{scope}, "
                                    f"SignedHeaders={signed}, Signature={sig}")
        r = requests.post(f"https://{self.host}{path}", data=body, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def fetch(self, queries, limit=50):
        cinfo = COUNTRIES[self.country]
        seen = set()
        for q in queries:
            payload = {
                "Keywords": q, "SearchIndex": "All", "ItemCount": 10, "PartnerTag": self.tag,
                "PartnerType": "Associates", "Marketplace": self.site,
                "Resources": ["ItemInfo.Title", "ItemInfo.Features", "ItemInfo.ByLineInfo",
                              "Images.Primary.Large", "Offers.Listings.Price"],
            }
            try:
                data = self._request(payload)
            except Exception as e:  # keep going with the next query
                print(f"amazon {self.country} '{q}': {e}")
                continue
            for item in data.get("SearchResult", {}).get("Items", []):
                asin = item.get("ASIN")
                if not asin or asin in seen:
                    continue
                seen.add(asin)
                info = item.get("ItemInfo", {})
                title = info.get("Title", {}).get("DisplayValue", "")
                features = " ".join(info.get("Features", {}).get("DisplayValues", []))
                listing = (item.get("Offers", {}).get("Listings") or [{}])[0]
                price = listing.get("Price", {}).get("Amount")
                if not title or price is None:
                    continue
                yield Product(
                    id=Product.make_id(self.merchant_id, asin), country=self.country, lang=cinfo["lang"],
                    merchant_id=self.merchant_id, title=title, description=features, price=float(price),
                    currency=cinfo["currency"], url=item.get("DetailPageURL", ""),
                    image=item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL", ""),
                    brand=info.get("ByLineInfo", {}).get("Brand", {}).get("DisplayValue", ""),
                    source="amazon",
                )
                if len(seen) >= limit:
                    return
