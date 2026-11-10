"""Fresh ingest of every active country, one after the other, for the deploy workflow.

    INGEST_LIMITS="US=60 GB=120 DE=270" python3 scripts/ci_ingest.py

INGEST_LIMITS gives the products per advertiser for the countries with many shops
(their items-<CC>.json is downloaded whole by the browser); the others use 500.
A country whose feed fails keeps the products it had: its rows are only replaced
once the new ones are in, and the run goes on with the next country.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

from app.config import ACTIVE_COUNTRIES  # noqa: E402
from app.sources import SOURCES  # noqa: E402

CATALOG = os.path.join(HERE, "..", "app", "data", "catalog.json")


def count(cc):
    with open(CATALOG, encoding="utf-8") as f:
        return sum(1 for p in json.load(f) if p["country"] == cc and p.get("source") not in ("seed", "manual"))


def main():
    limits = dict(x.split("=") for x in os.environ.get("INGEST_LIMITS", "").split() if "=" in x)
    failed, skipped = [], []
    for cc in ACTIVE_COUNTRIES:
        if not any(cls(cc).available() for cls in SOURCES):
            skipped.append(cc)
            continue
        before = count(cc)
        backup = open(CATALOG, "rb").read()
        env = dict(os.environ, INGEST_LIMIT=str(limits.get(cc, 500)))
        r = subprocess.run([sys.executable, os.path.join(HERE, "ingest.py"), cc, "--fresh"], env=env)
        after = count(cc) if r.returncode == 0 else 0
        # a feed that is down or half empty must not wipe a country off the site
        if r.returncode != 0 or (before and after < before * 0.5):
            open(CATALOG, "wb").write(backup)
            failed.append(cc)
            print(f"::warning::{cc}: ingest gave {after} products (had {before}); kept the previous ones")
        else:
            print(f"{cc}: {before} -> {after} feed products")
    if skipped:
        print("no feed configured for:", " ".join(skipped))
    if failed and len(failed) >= max(1, len(ACTIVE_COUNTRIES) - len(skipped)):
        sys.exit("every configured country failed; nothing was updated")


if __name__ == "__main__":
    main()
