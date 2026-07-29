import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Load products ─────────────────────────────────────────────────────────────
import os

_data_path = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
_data_path = os.path.normpath(_data_path)

if not os.path.exists(_data_path):
    _data_path = os.path.join(os.path.dirname(__file__), "data", "products.json")
    _data_path = os.path.normpath(_data_path)

with open(_data_path, "r", encoding="utf-8") as f:
    products = json.load(f)

# Filter delisted products (marked by mark_delisted.py)
products = [p for p in products if p.get("active", True)]

# Normalize clean_ingreds to a list
for p in products:
    raw = p.get("clean_ingreds", "[]")
    if isinstance(raw, list):
        pass  # already parsed (shouldn't happen at load time, but safe)
    else:
        try:
            ingred_str = raw.replace("'", '"')
            p["clean_ingreds"] = json.loads(ingred_str)
        except (json.JSONDecodeError, AttributeError):
            p["clean_ingreds"] = []

# ── Clean prices ──────────────────────────────────────────────────────────────
def clean_price(price_val) -> float | None:
    if price_val is None:
        return None
    price_str = re.sub(r"[£$,\s]", "", str(price_val)).strip()
    if price_str.lower() in ("", "nan", "none", "null", "n/a"):
        return None
    try:
        return float(price_str)
    except ValueError:
        return None

for p in products:
    p["price"] = clean_price(p.get("price"))

# ── Ingredient knowledge base ─────────────────────────────────────────────────
ACTIVE_INGREDIENTS = {
    # acne
    "salicylic acid", "benzoyl peroxide", "niacinamide", "azelaic acid", "sulfur", "zinc",
    # hydration
    "hyaluronic acid", "glycerin", "ceramide", "ceramide np", "ceramide ap", "ceramide eop",
    "squalane", "panthenol", "beta-glucan",
    # pigmentation
    "ascorbic acid", "vitamin c", "alpha-arbutin", "kojic acid",
    # anti-aging
    "retinol", "bakuchiol", "peptides", "adenosine",
    # soothing
    "allantoin", "centella asiatica", "green tea", "chamomile", "colloidal oatmeal", "aloe vera",
    # exfoliants
    "glycolic acid", "lactic acid", "mandelic acid",
}

CONCERN_TO_INGREDIENTS = {
    "Acne_Severity":          ["salicylic acid", "benzoyl peroxide", "niacinamide", "azelaic acid", "sulfur", "zinc"],
    "Dryness_Severity":       ["hyaluronic acid", "glycerin", "ceramide", "ceramide np", "squalane", "panthenol"],
    "Pigmentation_Severity":  ["ascorbic acid", "vitamin c", "alpha-arbutin", "kojic acid", "niacinamide"],
    "Aging_Severity":         ["retinol", "bakuchiol", "peptides", "adenosine"],
    "Sensitivity_Severity":   ["allantoin", "centella asiatica", "green tea", "chamomile",
                               "colloidal oatmeal", "aloe vera", "panthenol"],
}

# Cache recognized active ingredients for faster scoring
for p in products:
    p["active_ingredients"] = [
        ing.lower().strip()
        for ing in p.get("clean_ingreds", [])
        if ing.lower().strip() in ACTIVE_INGREDIENTS
    ]

# ── TF-IDF matrix (built once over ALL products) ──────────────────────────────
products_texts = [" ".join(p["clean_ingreds"]) for p in products]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(products_texts)

# ── Scoring ───────────────────────────────────────────────────────────────────
def score_rule_based(product: dict, user: dict) -> float:
    score = 0.0
    for concern, ingredients in CONCERN_TO_INGREDIENTS.items():
        severity = float(user.get(concern, 0))
        for ing in product["active_ingredients"]:
            if ing in ingredients:
                score += severity
    return score


def rec_hybrid(user: dict, _products_ignored=None, top_n: int = 12,
               alpha: float = 0.5, beta: float = 0.1):
    # ── Resolve price range ───────────────────────────────────────────────────
    if "Price_Min" in user or "Price_Max" in user:
        price_min = float(user.get("Price_Min", 0))
        price_max = float(user.get("Price_Max", 9999))
    else:
        # Legacy Budget_Level support
        budget_map = {"Low": (0, 20), "Medium": (0, 50), "High": (0, 200)}
        price_min, price_max = budget_map.get(user.get("Budget_Level", "High"), (0, 9999))

    # ── Build TF-IDF query from active concerns ───────────────────────────────
    query_terms = []
    for concern, ingredients in CONCERN_TO_INGREDIENTS.items():
        severity = float(user.get(concern, 0))
        if severity > 1:
            query_terms.extend(ingredients)

    query_text = " ".join(query_terms) if query_terms else "moisturiser serum cleanser"
    query_vec = vectorizer.transform([query_text])

    # ── Score ALL products (keeps tfidf index aligned) ────────────────────────
    tfidf_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    scored = []
    for i, p in enumerate(products):
        price = p.get("price")
        if price is None:
            continue
        if not (price_min <= price <= price_max):
            continue

        rule_score  = score_rule_based(p, user)
        hybrid      = alpha * rule_score + (1 - alpha) * tfidf_scores[i]

        # Small bonus for products comfortably within budget
        if price <= price_max * 0.7:
            hybrid += beta

        if hybrid > 0:
            scored.append((p, hybrid))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]