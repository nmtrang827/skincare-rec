"""
fix_images.py
-------------
Fixes broken image_url fields in products.json.

WHY the images are broken:
  - 902/1139 products have generic Unsplash placeholders (scraper fallback)
  - 237/1139 have real static.thcdn.com (LookFantastic CDN) URLs,
    but thcdn blocks all non-browser requests with 403 AND ~73 of
    those URLs have mismatched product IDs (scraper grabbed wrong product's image).
    The BROWSER can load them fine because you have cookies/JS from visiting LF.
    The server cannot verify or fix them without Playwright.

WHAT THIS SCRIPT DOES:
  1. Keeps thcdn.com URLs as-is — they DO load in the browser (403 is
     server-to-server only). The JS onerror fallback handles any that are
     truly broken.
  2. Replaces all Unsplash generic placeholders with a curated, type-specific
     Unsplash image that actually shows the right kind of product.
  3. Fixes the 73 thcdn ID mismatches by reconstructing a correct URL
     from the product_url's ID (can only do this for products where the
     product page ID and image ID differ — we zero it out so JS fallback
     shows the type image, which is better than a VW logo).

Run from project root:
    python fix_images.py
"""

import json
import re
from pathlib import Path

DATA_PATH = Path("data/products.json")

# Curated Unsplash images per product type — actual product-like photos,
# not the same generic bottle for everything.
TYPE_IMAGES = {
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
    "Sunscreen":    "https://images.unsplash.com/photo-1556228841-a3c527ebefe5?w=600&h=400&fit=crop&q=80",
    "":             "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop&q=80",
}
FALLBACK = "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop&q=80"


def get_id_from_product_url(url: str) -> str | None:
    """Extract numeric product ID from LookFantastic URL."""
    match = re.search(r'/(\d+)(?:\.html|#)?$', url.rstrip('/'))
    return match.group(1) if match else None


def get_id_from_image_url(url: str) -> str | None:
    """Extract the product ID prefix from a thcdn image filename."""
    match = re.search(r'/(\d+)-\d+\.jpg', url)
    return match.group(1) if match else None


def fix_products(data: list[dict]) -> tuple[list[dict], dict]:
    stats = {"mismatch_cleared": 0, "placeholder_replaced": 0, "kept": 0}

    for product in data:
        image_url = product.get("image_url", "")
        product_url = product.get("product_url", "")

        if "thcdn.com" in image_url:
            # Check for ID mismatch — image is for a different product
            url_id = get_id_from_product_url(product_url)
            img_id = get_id_from_image_url(image_url)

            if url_id and img_id and url_id != img_id:
                # Replace with type-specific image — better than a wrong product photo
                product_type = product.get("product_type", "")
                product["image_url"] = TYPE_IMAGES.get(product_type, FALLBACK)
                stats["mismatch_cleared"] += 1
            else:
                # ID matches — keep it, it will load fine in the browser
                stats["kept"] += 1

        elif "unsplash.com" in image_url and "photo-1556228720" in image_url:
            # This is the single generic placeholder the scraper used for everything.
            # Replace with a type-appropriate one.
            product_type = product.get("product_type", "")
            product["image_url"] = TYPE_IMAGES.get(product_type, FALLBACK)
            stats["placeholder_replaced"] += 1

        elif not image_url:
            product_type = product.get("product_type", "")
            product["image_url"] = TYPE_IMAGES.get(product_type, FALLBACK)
            stats["placeholder_replaced"] += 1

    return data, stats


def main():
    print(f"Loading {DATA_PATH}...")
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} products.")

    fixed_data, stats = fix_products(data)

    print(f"\nResults:")
    print(f"  thcdn URLs kept (browser-loadable):     {stats['kept']}")
    print(f"  thcdn mismatches cleared → type image:  {stats['mismatch_cleared']}")
    print(f"  Generic placeholders → type image:      {stats['placeholder_replaced']}")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {DATA_PATH}")
    print("Restart your Flask server to pick up the changes.")


if __name__ == "__main__":
    main()