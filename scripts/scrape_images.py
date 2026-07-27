"""
scrape_images.py
----------------
Fetches real product images from LookFantastic and updates products.json.

WHY THE OLD SCRAPER FAILED:
  1. LookFantastic changed their image src format.
     Old:  src="https://www.lookfantastic.com/images?url=https://static.thcdn.com/..."
     New:  src="https://static.thcdn.com/productimg/..." (direct, or inside a JSON blob)
  2. It skipped products that already had thcdn URLs — including the ~72
     mismatched ones (wrong product's image, e.g. the VW logo).
  3. LookFantastic now serves pages via JS rendering, so BeautifulSoup on
     raw HTML often finds no images. We use their internal JSON data blob
     (__NEXT_DATA__ or schema.org) which IS in the raw HTML.

WHAT THIS SCRIPT DOES:
  - Targets only products that need fixing:
      a) Unsplash placeholders (no real image at all)
      b) thcdn URLs where the product ID in the image doesn't match the URL
  - Tries two extraction methods per page:
      1. __NEXT_DATA__ JSON blob (Next.js site — most reliable)
      2. og:image meta tag (fast fallback)
      3. schema.org Product JSON-LD
  - Writes progress incrementally so a crash doesn't lose work.
  - Respects the server with a delay between requests.

USAGE (run from project root):
    pip install requests beautifulsoup4
    python scrape_images.py

    To scrape ALL products (slow, ~20 min):
    python scrape_images.py --all
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup

DATA_PATH = Path("data/products.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.lookfantastic.com/",
}
REQUEST_DELAY = 1.5   # seconds between requests — be polite
TIMEOUT = 12


# ── Helpers ──────────────────────────────────────────────────────────────────

def product_url_id(url: str) -> str | None:
    """Extract numeric ID from a LookFantastic product URL."""
    m = re.search(r"/(\d+)(?:\.html)?(?:#.*)?$", url.rstrip("/"))
    return m.group(1) if m else None


def image_url_id(url: str) -> str | None:
    """Extract the product-ID prefix from a thcdn image filename."""
    m = re.search(r"/(\d+)-\d+\.jpg", url)
    return m.group(1) if m else None


def needs_fix(product: dict) -> bool:
    """Return True if this product's image_url should be refreshed."""
    img = product.get("image_url", "")
    if not img or "unsplash.com" in img:
        return True
    if "thcdn.com" in img:
        pid = product_url_id(product.get("product_url", ""))
        iid = image_url_id(img)
        if pid and iid and pid != iid:
            return True   # ID mismatch — wrong product's image
    return False


# ── Image extraction strategies ──────────────────────────────────────────────

def extract_from_next_data(soup: BeautifulSoup) -> str | None:
    """
    LookFantastic is a Next.js app. The full product data (including images)
    is embedded in a <script id="__NEXT_DATA__"> JSON blob.
    """
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None
    try:
        data = json.loads(tag.string)
        # Path varies by page version — search recursively for thcdn URLs
        text = json.dumps(data)
        urls = re.findall(r"https://static\.thcdn\.com/productimg/[^\"'\\s]+", text)
        # Filter out thumbnails / swatches — prefer 'original' or largest size
        originals = [u for u in urls if "/original/" in u or "/960/" in u]
        return originals[0] if originals else (urls[0] if urls else None)
    except (json.JSONDecodeError, KeyError):
        return None


def extract_from_og(soup: BeautifulSoup) -> str | None:
    """og:image is usually the main product photo — fast and reliable."""
    tag = soup.find("meta", property="og:image")
    if not tag:
        return None
    url = tag.get("content", "")
    if "thcdn.com" in url or "lookfantastic.com" in url:
        # Unwrap LF image proxy if present
        m = re.search(r"url=(https://static\.thcdn\.com/[^&]+)", url)
        return m.group(1) if m else url
    return None


def extract_from_schema(soup: BeautifulSoup) -> str | None:
    """schema.org Product JSON-LD sometimes has the image."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string)
            if isinstance(data, list):
                data = next((d for d in data if d.get("@type") == "Product"), {})
            if data.get("@type") == "Product":
                img = data.get("image")
                if isinstance(img, list):
                    img = img[0]
                if img and ("thcdn" in img or "lookfantastic" in img):
                    return img
        except (json.JSONDecodeError, AttributeError):
            continue
    return None


def extract_from_img_tags(soup: BeautifulSoup) -> str | None:
    """
    Last resort: scan all <img> tags for thcdn URLs.
    Handles both old proxy format and new direct format.
    """
    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")

        # New format: direct thcdn URL
        if "static.thcdn.com/productimg" in src:
            m = re.search(r"url=(https://static\.thcdn\.com/[^&]+)", src)
            return m.group(1) if m else src

        # Old proxy format (still appears on some cached pages)
        if "lookfantastic.com/images" in src and "thcdn.com" in src:
            m = re.search(r"url=(https://static\.thcdn\.com/[^&]+)", src)
            if m:
                return m.group(1)

    return None


def get_product_image(product_url: str) -> str | None:
    """Try all extraction strategies for a given product page URL."""
    try:
        resp = requests.get(product_url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ✗ Request failed: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    for strategy in [extract_from_next_data, extract_from_og,
                     extract_from_schema, extract_from_img_tags]:
        result = strategy(soup)
        if result:
            return result.split("?")[0]  # strip query params

    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true",
                        help="Scrape all products, not just broken ones")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max products to process (0 = no limit)")
    args = parser.parse_args()

    with open(DATA_PATH, encoding="utf-8") as f:
        products = json.load(f)

    targets = [(i, p) for i, p in enumerate(products)
               if args.all or needs_fix(p)]

    if args.limit:
        targets = targets[: args.limit]

    print(f"Found {len(targets)} products to update "
          f"({'all' if args.all else 'broken/missing only'}).")
    if not targets:
        print("Nothing to do — all images look correct.")
        return

    updated, failed = 0, 0

    for n, (i, product) in enumerate(targets, 1):
        name = product["product_name"][:45]
        url = product["product_url"]
        print(f"[{n}/{len(targets)}] {name}")

        image_url = get_product_image(url)

        if image_url:
            products[i]["image_url"] = image_url
            updated += 1
            print(f"    ✓ {image_url}")
        else:
            failed += 1
            print(f"    ✗ No image found — keeping existing value")

        # Save after every product so a crash doesn't lose progress
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        if n < len(targets):
            time.sleep(REQUEST_DELAY)

    print(f"\nDone. Updated: {updated}, Failed: {failed}")
    print("Restart your Flask server to pick up the new images.")


if __name__ == "__main__":
    main() 