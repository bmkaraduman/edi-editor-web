"""Gate before a deploy: refuse to publish a broken or shrunken build.

    MIN_PRODUCTS=3000 python3 scripts/check_dist.py dist
"""
import json
import os
import sys


def main(dest):
    problems = []
    for name in ("index.html", "data.json", "where.json", "_redirects", "sitemap.xml"):
        if not os.path.exists(os.path.join(dest, name)) or os.path.getsize(os.path.join(dest, name)) == 0:
            problems.append(f"{name} is missing or empty")
    if problems:
        sys.exit("not deploying: " + "; ".join(problems))
    data = json.load(open(os.path.join(dest, "data.json"), encoding="utf-8"))
    counts, real = data.get("counts", {}), data.get("real", [])
    total = sum(counts.get(cc, 0) for cc in real)
    need = int(os.environ.get("MIN_PRODUCTS", "3000"))
    print(f"countries with real products: {' '.join(real) or '-'}")
    print("products per country: " + ", ".join(f"{cc} {n}" for cc, n in sorted(counts.items())))
    print(f"real products: {total} (minimum {need})")
    if total < need:
        problems.append(f"only {total} real products, expected at least {need} (feeds down or secret incomplete?)")
    for cc in counts:
        path = os.path.join(dest, f"items-{cc}.json")
        if not os.path.exists(path):
            problems.append(f"items-{cc}.json is missing")
        elif os.path.getsize(path) > 25 * 1024 * 1024:
            problems.append(f"items-{cc}.json is over Cloudflare's 25 MB file limit: lower that country's INGEST_LIMITS")
    page = open(os.path.join(dest, "index.html"), encoding="utf-8").read()
    for needle in ('id="bar"', 'id="adv-toggle"', "/assets/app."):
        if needle not in page:
            problems.append(f"index.html lacks {needle}")
    if problems:
        sys.exit("not deploying: " + "; ".join(problems))
    print("build looks good")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist")
