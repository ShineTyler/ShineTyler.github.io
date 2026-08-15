"""One-off downloader that self-hosts Playfair Display + IBM Plex Mono.

Run: python src/scripts/fetch_fonts.py
Fetch the Google Fonts css2 payload with a woff2-capable UA, keep only the
latin subset, and save each woff2 into src/assets/fonts/ with a stable name:
  playfair-display-w400.woff2, playfair-display-w700-italic.woff2, ...
"""
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)

CSS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400;1,700"
    "&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400"
    "&display=swap"
)
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

FAMILY_MAP = {
    "Playfair Display": "playfair-display",
    "IBM Plex Mono": "ibm-plex-mono",
}


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> None:
    css = fetch_bytes(CSS_URL).decode("utf-8")
    pairs = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S)
    latin = [(subset, body) for subset, body in pairs if subset == "latin"]
    if not latin:
        print("no latin subset in response", file=sys.stderr)
        sys.exit(1)

    # Google serves variable families as one file shared by every weight,
    # so dedupe by (family, style) → url and name variable files accordingly.
    saved = 0
    seen: dict = {}
    for _subset, body in latin:
        family_match = re.search(r"font-family:\s*'([^']+)'", body)
        weight_match = re.search(r"font-weight:\s*(\d+)", body)
        style_match = re.search(r"font-style:\s*(\w+)", body)
        url_match = re.search(r"url\((https://[^)]+)\)", body)
        if not (family_match and weight_match and url_match):
            continue
        family = FAMILY_MAP.get(family_match.group(1))
        if not family:
            continue
        style = style_match.group(1) if style_match else "normal"
        url = url_match.group(1)
        key = (family, style)
        is_variable = key in seen and seen[key] != url
        seen[key] = url
        if is_variable:
            name = f"{family}-var-italic.woff2" if style == "italic" else f"{family}-var.woff2"
            if (OUT / name).exists():
                continue
        else:
            weight = weight_match.group(1)
            name = (
                f"{family}-w{weight}-italic.woff2"
                if style == "italic"
                else f"{family}-w{weight}.woff2"
            )
        binary = fetch_bytes(url)
        (OUT / name).write_bytes(binary)
        saved += 1
        print(f"  {name}  {len(binary)} bytes")

    print(f"saved {saved} latin subset files")


if __name__ == "__main__":
    main()
