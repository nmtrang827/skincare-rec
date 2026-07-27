"""
mark_delisted.py
----------------
HEAD-checks every product URL and adds an "active" field to products.json.
  active: true  → product page exists, safe to recommend
  active: false → 404/410, product delisted from LookFantastic

Run once from project root:
    pip install requests
    python mark_delisted.py

Takes ~10-15 min for 1139 products (0.5s delay, concurrent with ThreadPoolExecutor).
Progress is printed live and saved incrementally so a crash doesn't lose work.

After running, the recommender will automatically skip inactive products
(server.py filters on active != False at load time).
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

DATA_PATH = Path("data/products.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}
TIMEOUT = 8
WORKERS = 6      
SAVE_EVERY = 50  


def check_url(index: int, product: dict) -> tuple[int, bool, str]:
    """Returns (index, is_active, reason)."""
    url = product.get("product_url", "")
    if not url:
        return index, False, "no URL"
    try:
        resp = requests.head(
            url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True
        )
        if resp.status_code == 404:
            return index, False, "404"
        if resp.status_code == 410:
            return index, False, "410 Gone"
        if resp.status_code >= 400:
            return index, False, f"HTTP {resp.status_code}"
        return index, True, f"HTTP {resp.status_code}"
    except requests.Timeout:
        return index, True, "timeout (assumed active)"
    except requests.RequestException as e:
        return index, True, f"error (assumed active): {e}"


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        products = json.load(f)

    total = len(products)

    # Skip products already checked in a previous run
    to_check = [
        (i, p) for i, p in enumerate(products)
        if "active" not in p
    ]
    already_done = total - len(to_check)

    print(f"Total products: {total}")
    print(f"Already checked: {already_done}, To check now: {len(to_check)}")
    if not to_check:
        active = sum(1 for p in products if p.get("active", True))
        print(f"All done — {active} active, {total - active} delisted.")
        return

    completed = 0
    delisted = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(check_url, i, p): (i, p)
            for i, p in to_check
        }

        for future in as_completed(futures):
            index, is_active, reason = future.result()
            products[index]["active"] = is_active
            completed += 1

            if not is_active:
                delisted += 1
                name = products[index]["product_name"][:45]
                print(f"  [DELISTED] {name} — {reason}")

            if completed % 25 == 0 or completed == len(to_check):
                print(f"  Progress: {completed + already_done}/{total} "
                      f"({delisted} delisted so far)")

            # Save incrementally
            if completed % SAVE_EVERY == 0 or completed == len(to_check):
                with open(DATA_PATH, "w", encoding="utf-8") as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)

    # Final save
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    active_count = sum(1 for p in products if p.get("active", True))
    delisted_count = total - active_count
    print(f"\nDone.")
    print(f"  Active products:   {active_count}")
    print(f"  Delisted products: {delisted_count}")
    print(f"\nRestart Flask — delisted products will no longer appear in recommendations.")


if __name__ == "__main__":
    main()