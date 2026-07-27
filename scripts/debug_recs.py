# import json
# import codecs
# from backend.recommender_tfidf import rec_hybrid, products

# # Use the processed products from the recommender module
# print(f'Total products loaded: {len(products)}')

# # Test recommendation
# user = {
#     'Budget_Level': 'Medium',
#     'Acne_Severity': 3,
#     'Dryness_Severity': 5,
#     'Pigmentation_Severity': 2,
#     'Aging_Severity': 1,
#     'Sensitivity_Severity': 2
# }

# recommendations = rec_hybrid(user, products, top_n=3)
# print('Recommended products and their image URLs:')
# for i, (product, score) in enumerate(recommendations):
#     print(f'{i+1}. {product["product_name"]}')
#     print(f'   Image URL: {product.get("image_url", "No URL")}')
#     print(f'   Score: {score:.3f}')
#     print()