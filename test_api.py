# import requests
# import json

# # Test the API
# url = 'http://127.0.0.1:5000/recommend_tfidf'
# data = {
#     'Budget_Level': 'Medium',
#     'Acne_Severity': 3,
#     'Dryness_Severity': 5,
#     'Pigmentation_Severity': 2,
#     'Aging_Severity': 1,
#     'Sensitivity_Severity': 2
# }

# try:
#     response = requests.post(url, json=data)
#     result = response.json()
#     print('API Response:')
#     for i, product in enumerate(result[:3]):  # Show first 3 products
#         print(f'{i+1}. {product["name"]}')
#         print(f'   Image URL: {product.get("image_url", "No image URL")}')
#         print(f'   Price: {product["price"]}')
#         print()
# except Exception as e:
#     print(f'Error: {e}')