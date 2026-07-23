"""
scrape_images_playwright.py
---------------------------
Uses Playwright (real Chromium browser) to scrape product images from
LookFantastic. Bypasses Cloudflare and JS-rendered content that broke
the requests+BeautifulSoup scraper.

Install once:
    pip install playwright
    playwright install chromium

Run from project root:
    python scrape_images_playwright.py

Options:
    --limit 20       only process first N products (for testing)
    --all            re-scrape everything, not just placeholders
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path

DATA_PATH = Path("data/products.json")

TYPE_FALLBACKS = {
    "Moisturiser":  "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=400&fit=crop&q=80",
    "Serum":        "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=600&h=400&fit=crop&q=80",
    "Cleanser":     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=400&fit=crop&q=80",
    "Toner":        "https://images.unsplash.com/photo-1601049541271-25cf5f3bfa72?w=600&h=400&fit=crop&q=80",
    "Mask":         "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=400&fit=crop&q=80",
    "Oil":          "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=400&fit=crop&q=80",
    "Bath Oil":     "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=400&fit=crop&q=80",
    "Mist":         "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&h=400&fit=crop&q=80",
    "Balm":         "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=600&h=400&fit=crop&q=80",
    "Peel":         "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&h=400&fit=crop&q=80",
    "Eye Care":     "https://images.unsplash.com/photo-1631390003047-4a858b4e4b5a?w=600&h=400&fit=crop&q=80",
    "Exfoliator":   "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=600&h=400&fit=crop&q=80",
    "Bath Salts":   "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600&h=400&fit=crop&q=80",
    "Body Wash":    "https://images.unsplash.com/photo-1631390003047-4a858b4e4b5a?w=600&h=400&fit=crop&q=80",
}
FALLBACK_DEFAULT = "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop&q=80"


def needs_fix(product: dict) -> bool:
    img = product.get("image_url", "")
    return not img or "unsplash.com" in img


def extract_image_from_page(page) -> str | None:
    """Try multiple strategies to find the main product image."""

    # Strategy 1: __NEXT_DATA__ JSON blob (most reliable)
    try:
        next_data = page.evaluate("""
            () => {
                const el = document.getElementById('__NEXT_DATA__');
                return el ? el.textContent : null;
            }
        """)
        if next_data:
            urls = re.findall(
                r'https://static\\.thcdn\\.com/productimg/[^"\'\\\\s]+', next_data
            )
            originals = [u for u in urls if "/original/" in u or "/1600/" in u]
            if originals:
                return originals[0].split("?")[0]
            if urls:
                return urls[0].split("?")[0]
    except Exception:
        pass

    # Strategy 2: og:image meta tag
    try:
        og = page.get_attribute('meta[property="og:image"]', "content")
        if og and "thcdn.com" in og:
            m = re.search(r"url=(https://static\.thcdn\.com/[^&]+)", og)
            return (m.group(1) if m else og).split("?")[0]
    except Exception:
        pass

    # Strategy 3: largest visible <img> pointing to thcdn
    try:
        imgs = page.eval_on_selector_all("img[src*='thcdn.com']", """
            els => els.map(el => ({
                src: el.src,
                w: el.naturalWidth || el.width
            }))
        """)
        if imgs:
            imgs.sort(key=lambda x: x.get("w", 0), reverse=True)
            src = imgs[0]["src"]
            m = re.search(r"url=(https://static\.thcdn\.com/[^&]+)", src)
            return (m.group(1) if m else src).split("?")[0]
    except Exception:
        pass

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("Playwright not installed. Run:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    with open(DATA_PATH, encoding="utf-8") as f:
        products = json.load(f)

    targets = [(i, p) for i, p in enumerate(products)
               if args.all or needs_fix(p)]
    if args.limit:
        targets = targets[:args.limit]

    print(f"Found {len(targets)} products to fix.")
    if not targets:
        print("Nothing to do.")
        return

    updated, failed, skipped_404 = 0, 0, 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-GB",
        )
        page = context.new_page()

        # Block fonts/analytics to speed up page loads
        page.route(
            re.compile(r"\.(woff2?|ttf|eot)$|google-analytics|googletagmanager|hotjar"),
            lambda route: route.abort()
        )

        for n, (i, product) in enumerate(targets, 1):
            name = product["product_name"][:50]
            url  = product["product_url"]
            print(f"[{n}/{len(targets)}] {name}")

            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=15000)

                if resp and resp.status == 404:
                    print(f"    ✗ 404 — product delisted")
                    products[i]["active"] = False
                    skipped_404 += 1
                    continue

                # Wait briefly for JS to hydrate the image
                try:
                    page.wait_for_selector("img[src*='thcdn.com']", timeout=5000)
                except PWTimeout:
                    pass  # image might still be in __NEXT_DATA__

                image_url = extract_image_from_page(page)

                if image_url:
                    products[i]["image_url"] = image_url
                    updated += 1
                    print(f"    ✓ {image_url}")
                else:
                    # Use type-appropriate fallback — better than a generic placeholder
                    ptype = product.get("product_type", "")
                    products[i]["image_url"] = TYPE_FALLBACKS.get(ptype, FALLBACK_DEFAULT)
                    failed += 1
                    print(f"    ✗ No image found — type fallback applied")

            except PWTimeout:
                failed += 1
                print(f"    ✗ Timed out")
            except Exception as e:
                failed += 1
                print(f"    ✗ Error: {e}")

            # Save after every product
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            # LookFantastic has rate limiting
            if n < len(targets):
                time.sleep(1.2)

        context.close()
        browser.close()

    print(f"\nDone. Updated: {updated}, Failed: {failed}, 404s: {skipped_404}")
    print("Restart Flask to pick up the new images.")


if __name__ == "__main__":
    main()