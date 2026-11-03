"""Shared product model and the source interface every connector implements."""
from dataclasses import dataclass, field, asdict
import hashlib


@dataclass
class Product:
    id: str
    country: str
    lang: str
    merchant_id: str
    title: str
    description: str
    price: float            # in the country's currency
    currency: str
    url: str = ""           # deep product URL (empty -> merchant search page)
    image: str = ""         # main image; products without one are never shown
    brand: str = ""
    category: str = ""      # merchant's own category (leaf)
    labels: dict = field(default_factory=dict)   # facet -> [label, ...]
    source: str = "feed"    # seed | amazon | awin | csv | manual
    merchant_name: str = ""  # display name when merchant_id is not in config (combined feeds)
    images: list = field(default_factory=list)   # further images for the detail page
    keywords: str = ""      # feed keywords / tags, weighted like the title in the text index
    category_path: str = "" # "Kinder > Kinderstrumpfhosen"
    product_type: str = ""
    rrp: float = 0.0        # recommended retail price (0 = unknown); shown struck through
    details: dict = field(default_factory=dict)  # colour, condition, model, dimensions, specs, delivery, promo
    rules: list = field(default_factory=list)    # ids of the labelling rules that matched (see app/data/rules.py)
    gift: float = 0.5       # giftability prior 0..1 from the rules (1 = classic gift, ~0 = office supply)

    @staticmethod
    def make_id(merchant_id, external_id):
        return hashlib.sha1(f"{merchant_id}:{external_id}".encode()).hexdigest()[:16]

    def to_dict(self):
        return asdict(self)


class Source:
    """A connector pulls products for one country from one affiliate feed."""

    name = "base"

    def __init__(self, country):
        self.country = country

    def available(self):
        """True when the credentials/files needed by this source exist."""
        return False

    def fetch(self, queries, limit=50):
        """Yield Product objects. `queries` are search phrases in the
        country's language, produced from the taxonomy lexicon."""
        return []
