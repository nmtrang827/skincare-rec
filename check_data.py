# import json

# with open('data/products.json', 'r') as f:
#     products = json.load(f)

# print(f'Total products: {len(products)}')
# products_with_images = [p for p in products if 'image_url' in p]
# print(f'Products with image_url: {len(products_with_images)}')

# # Show first few products with images
# for i, p in enumerate(products_with_images[:5]):
#     print(f'{i+1}. {p["product_name"]} - {p.get("image_url", "No URL")}')

# # Show what products are being recommended
# from backend.recommender_tfidf import rec_hybrid
# user = {
#     'Budget_Level': 'Medium',
#     'Acne_Severity': 3,
#     'Dryness_Severity': 5,
#     'Pigmentation_Severity': 2,
#     'Aging_Severity': 1,
#     'Sensitivity_Severity': 2
# }

# recommendations = rec_hybrid(user, products, top_n=3)
# print('\nRecommended products:')
# for product, score in recommendations:
#     has_image = 'image_url' in product
#     print(f'- {product["product_name"]} (has image: {has_image})')