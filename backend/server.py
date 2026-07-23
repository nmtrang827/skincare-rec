import ast
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from recommender_tfidf import rec_hybrid, products as _all_products

# Filter out delisted products (marked by mark_delisted.py).
# "active" defaults to True for products not yet checked.
products = [p for p in _all_products if p.get("active", True)]
print(f"Loaded {len(products)}/{len(_all_products)} active products "
      f"({len(_all_products) - len(products)} delisted filtered out).")

app = Flask(__name__)
CORS(app)

# Known "active" ingredients to highlight — everything else in clean_ingreds
# is a carrier/base. Extend this list as needed.
ACTIVE_KEYWORDS = {
    "niacinamide", "retinol", "retinal", "tretinoin", "bakuchiol",
    "vitamin c", "ascorbic acid", "ascorbyl glucoside",
    "hyaluronic acid", "sodium hyaluronate",
    "glycolic acid", "lactic acid", "mandelic acid", "salicylic acid",
    "azelaic acid", "tranexamic acid", "kojic acid", "phytic acid",
    "ceramide", "ceramide np", "ceramide ap", "ceramide eop",
    "peptide", "palmitoyl tripeptide", "acetyl hexapeptide",
    "squalane", "centella asiatica", "madecassoside", "cica",
    "zinc", "zinc pca", "sulfur",
    "arbutin", "alpha arbutin",
    "resveratrol", "coenzyme q10", "ferulic acid",
    "allantoin", "panthenol", "beta-glucan",
    "adenosine", "epidermal growth factor", "egf",
    "tocopherol", "tocopheryl acetate",
    "tea tree", "melaleuca alternifolia",
}

def extract_active_ingredients(clean_ingreds) -> list[str]:
    """
    Handles three possible shapes for clean_ingreds coming from the recommender:
      1. Already a list  → use directly (recommender parsed it internally)
      2. A stringified Python list ("['niacinamide', ...]") → ast.literal_eval
      3. Anything else   → split on comma as last resort
    Then filters to known actives; falls back to first 5 if none match.
    """
    if isinstance(clean_ingreds, list):
        ingreds = clean_ingreds
    elif isinstance(clean_ingreds, str):
        try:
            ingreds = ast.literal_eval(clean_ingreds)
        except (ValueError, SyntaxError):
            ingreds = [i.strip().strip("'\"[]") for i in clean_ingreds.split(",")]
    else:
        ingreds = []

    actives = [i for i in ingreds if any(kw in i.lower() for kw in ACTIVE_KEYWORDS)]

    # Fall back to first 5 ingredients if none matched the active list
    return actives if actives else ingreds[:5]


@app.route("/recommend_tfidf", methods=["POST"])
def recommend_tfidf():
    user = request.json

    # Price range filter — new slider sends Price_Min / Price_Max in £.
    # Falls back to Budget_Level for backwards compatibility.
    price_min = float(user.get("Price_Min", 0))
    price_max = float(user.get("Price_Max", 9999))

    # If old Budget_Level is sent instead, map it to price bands
    if "Budget_Level" in user and "Price_Min" not in user:
        budget_map = {"Low": (0, 20), "Medium": (20, 50), "High": (50, 9999)}
        price_min, price_max = budget_map.get(user["Budget_Level"], (0, 9999))

    # Pre-filter products to the selected price range before scoring
    def parse_price(p):
        try:
            return float(str(p.get("price", "0")).replace("\xa3", "").replace("£", "").strip())
        except ValueError:
            return 0.0

    price_filtered = [p for p in products if price_min <= parse_price(p) <= price_max]

    if not price_filtered:
        return jsonify([])

    recommendations = rec_hybrid(user, price_filtered, top_n=8, alpha=0.7)
    results = []

    for product, score in recommendations:
        # BUG FIX: active_ingredients key doesn't exist in products.json.
        # Parse it from clean_ingreds instead.
        active_ingredients = extract_active_ingredients(
            product.get("clean_ingreds", "[]")
        )

        # BUG FIX: Use real image_url from data; fall back to a generic only if missing.
        image_url = product.get("image_url", "")
        if not image_url:
            image_url = "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop&crop=center"

        results.append({
            "name": product["product_name"],
            "type": product["product_type"],
            "price": product["price"],
            "active_ingredients": active_ingredients,
            "url": product["product_url"],
            "image_url": image_url,
        })

    return jsonify(results)


@app.route("/proxy-image")
def proxy_image():
    """
    Proxy endpoint to fetch images from external CDNs, bypassing browser CORS.
    Use as: /proxy-image?url=https://static.thcdn.com/...
    """
    image_url = request.args.get("url")
    if not image_url:
        return jsonify({"error": "No URL provided"}), 400

    # Basic SSRF guard — only allow known image CDNs
    ALLOWED_HOSTS = {"static.thcdn.com", "images.unsplash.com"}
    from urllib.parse import urlparse
    host = urlparse(image_url).netloc
    if host not in ALLOWED_HOSTS:
        return jsonify({"error": f"Host not allowed: {host}"}), 403

    try:
        resp = requests.get(
            image_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SkincarePicker/1.0)"},
        )
        resp.raise_for_status()
        return Response(
            resp.content,
            content_type=resp.headers.get("content-type", "image/jpeg"),
            headers={
                "Cache-Control": "public, max-age=86400",  # cache 24h
                "Access-Control-Allow-Origin": "*",
            },
        )
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch image: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)