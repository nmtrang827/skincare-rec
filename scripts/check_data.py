import json
import sys
sys.path.insert(0, 'backend')

with open('data/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f'Total products: {len(products)}')

# Image URL breakdown
unsplash = [p for p in products if 'unsplash' in p.get('image_url', '')]
thcdn    = [p for p in products if 'thcdn'    in p.get('image_url', '')]
empty    = [p for p in products if not p.get('image_url', '')]
print(f'Real images (thcdn):   {len(thcdn)}')
print(f'Placeholders (unsplash): {len(unsplash)}')
print(f'Empty:                 {len(empty)}')

# Show a few of each
print('\nSample real images:')
for p in thcdn[:3]:
    print(f'  {p["product_name"][:45]} -> {p["image_url"]}')

print('\nSample placeholders:')
for p in unsplash[:3]:
    print(f'  {p["product_name"][:45]} -> {p["image_url"]}')

# Test recommender
from recommender_tfidf import rec_hybrid

user = {
    'Price_Min': 0,
    'Price_Max': 50,
    'Acne_Severity': 3,
    'Dryness_Severity': 5,
    'Pigmentation_Severity': 2,
    'Aging_Severity': 1,
    'Sensitivity_Severity': 2,
}

recommendations = rec_hybrid(user, top_n=3)
print('\nSample recommendations:')
for product, score in recommendations:
    img = product.get('image_url', '')
    img_type = 'thcdn' if 'thcdn' in img else ('unsplash' if 'unsplash' in img else 'empty')
    print(f'  [{img_type}] {product["product_name"][:45]} — £{product["price"]} (score {score:.3f})')