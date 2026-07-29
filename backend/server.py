import ast
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from recommender_tfidf import rec_hybrid, products as _all_products

import os
import uuid
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

try:
    from skin_analyzer import analyze_image
    YOLO_AVAILABLE = True
except Exception:
    YOLO_AVAILABLE = False

# Filter out delisted products (marked by mark_delisted.py).
# "active" defaults to True for products not yet checked.
products = [p for p in _all_products if p.get("active", True)]
print(f"Loaded {len(products)}/{len(_all_products)} active products "
      f"({len(_all_products) - len(products)} delisted filtered out).")

app = Flask(__name__)
CORS(app)

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

    recommendations = rec_hybrid(user, top_n=12, alpha=0.7)
    results = []

    for product, score in recommendations:
        active_ingredients = extract_active_ingredients(
            product.get("clean_ingreds", "[]")
        )

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

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if not YOLO_AVAILABLE:
        return jsonify({
            'error': 'AI scan is not available in the deployed version. Run locally to use this feature.'
        }), 503

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    try:
        result = analyze_image(save_path)
        return jsonify(result)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

@app.route("/save_results", methods=["POST"])
def save_results():
    data = request.json
    profile  = data.get("profile")
    products = data.get("products")

    if not profile or not products:
        return jsonify({"error": "Missing profile or products"}), 400

    # Generate a short readable ID — 8 chars is enough for a portfolio project
    result_id = uuid.uuid4().hex[:8]

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO consultations (id, profile, products) VALUES (%s, %s, %s)",
            (result_id, json.dumps(profile), json.dumps(products))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": result_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results/<result_id>", methods=["GET"])
def get_results(result_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            "SELECT profile, products, created_at FROM consultations WHERE id = %s",
            (result_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": "Results not found"}), 404

        profile, products, created_at = row
        return jsonify({
            "profile":    profile,
            "products":   products,
            "created_at": created_at.isoformat(),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)