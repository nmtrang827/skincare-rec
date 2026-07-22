from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from recommender_tfidf import rec_hybrid, products

app = Flask(__name__)
CORS(app)

@app.route("/recommend_tfidf", methods=["POST"])
def recommend_tfidf():
    user = request.json
    recommendations = rec_hybrid(user, products, top_n=8, alpha=0.7)
    results = []

    for product, score in recommendations:
        results.append({
            "name": product["product_name"],
            "type": product["product_type"],
            "price": product["price"],
            "active_ingredients": product["active_ingredients"],
            "url": product["product_url"],
            "image_url": product.get("image_url", "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop&crop=center")
        })
    
    return jsonify(results)

@app.route("/proxy-image")
def proxy_image():
    """Proxy endpoint to fetch images from external URLs, avoiding CORS issues"""
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        # Fetch the image from the external URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with appropriate headers
        return Response(
            response.content,
            content_type=response.headers.get('content-type', 'image/jpeg'),
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Access-Control-Allow-Origin': '*'
            }
        )
    except requests.RequestException as e:
        # Return a fallback image or error
        return jsonify({"error": f"Failed to fetch image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)