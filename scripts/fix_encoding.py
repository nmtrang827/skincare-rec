"""
fix_encoding.py
---------------
Fixes mojibake (double-encoded UTF-8) in products.json.

The symptom: accented characters appear as garbled ASCII sequences.
  AvÃ¨ne   →  Avène
  TolÃ©rance → Tolérance
  ExtrÃªme  → Extrême

This happened because the original scraper read the page as latin-1 (Windows-1252)
but the bytes were actually UTF-8, so each multi-byte character got misread as
two separate latin-1 characters and then re-encoded into UTF-8 as garbage.

Fix: encode the garbled string back to latin-1 bytes, then decode as UTF-8.

Run from project root AFTER scrape_images.py finishes:
    python fix_encoding.py
"""

import json
from pathlib import Path

DATA_PATH = Path("data/products.json")
TEXT_FIELDS = ["product_name", "product_type", "product_url"]


def fix_mojibake(s: str) -> str:
    """
    Attempt to fix a mojibake string.
    If the string contains non-ASCII that looks garbled, re-encode as latin-1
    and decode as UTF-8. If that fails or makes it worse, return original.
    """
    try:
        fixed = s.encode("latin-1").decode("utf-8")
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s  # already fine, or unfixable


def looks_garbled(s: str) -> bool:
    """Heuristic: mojibake typically contains Ã followed by a symbol/letter."""
    return "Ã" in s or "â€" in s or "Â" in s


def fix_products(data: list[dict]) -> tuple[list[dict], int]:
    fixed_count = 0
    for product in data:
        for field in TEXT_FIELDS:
            val = product.get(field, "")
            if isinstance(val, str) and looks_garbled(val):
                fixed = fix_mojibake(val)
                if fixed != val:
                    product[field] = fixed
                    fixed_count += 1
    return data, fixed_count


def main():
    print(f"Loading {DATA_PATH}...")
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    data, fixed_count = fix_products(data)
    print(f"Fixed {fixed_count} garbled strings across {len(data)} products.")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved. Restart Flask to see clean product names.")


if __name__ == "__main__":
    main()