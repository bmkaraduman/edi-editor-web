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
    image: str = ""
    brand: str = ""
    category: str = ""
    labels: dict = field(default_factory=dict)   # facet -> [label, ...]
    source: str = "feed"    # seed | amazon | awin | csv | ...

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
