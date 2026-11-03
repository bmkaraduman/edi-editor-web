"""List the Awin programmes this publisher has joined and check them against
app/config.py, so the `mid` values used for click tracking are correct.

    AWIN_API_TOKEN=... AWIN_AFFILIATE_ID=3142976 python3 scripts/awin_programmes.py

The token is the OAuth2 token from Awin: Settings -> API Credentials.
"""
import os
import sys

import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.config import MERCHANT_BY_ID  # noqa: E402


def main():
    token = os.environ.get("AWIN_API_TOKEN")
    pub = os.environ.get("AWIN_AFFILIATE_ID")
    if not token or not pub:
        sys.exit("set AWIN_API_TOKEN and AWIN_AFFILIATE_ID")
    r = requests.get(f"https://api.awin.com/publishers/{pub}/programmes",
                     params={"relationship": "joined"}, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    r.raise_for_status()
    joined = r.json()
    ours = {m["mid"]: mid for mid, m in MERCHANT_BY_ID.items() if m["network"] == "awin"}
    print(f"{len(joined)} joined programmes\n")
    print(f"{'awin id':>8}  {'region':6}  {'name':40}  config")
    for p in sorted(joined, key=lambda x: x["name"]):
        pid = str(p["id"])
        print(f"{pid:>8}  {p.get('primaryRegion', {}).get('countryCode', ''):6}  {p['name'][:40]:40}  {ours.get(pid, '-- not in config')}")
    missing = [mid for mid, m in MERCHANT_BY_ID.items() if m["network"] == "awin" and m["mid"] not in {str(p["id"]) for p in joined}]
    if missing:
        print("\nconfigured merchants with no joined programme (check the mid or join the programme):", ", ".join(missing))


if __name__ == "__main__":
    main()
