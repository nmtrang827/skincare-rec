# import json
# import requests
# from bs4 import BeautifulSoup
# import re

# def get_image(url):
#     try:
#         response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         for img in soup.find_all('img'):
#             src = img.get('src', '')
#             if 'static.thcdn.com/productimg/original/' in src:
#                 match = re.search(r'url=(https://static\.thcdn\.com/productimg/original/[^&]+)', src)
#                 if match:
#                     return match.group(1)
#     except:
#         pass
#     return None

# # Load and update products
# products = json.load(open('data/products.json', encoding='utf-8'))

# # Update the top recommended products
# targets = [
#     'COSRX AC Collection Blemish Spot Clearing Serum 40ml',
#     'Holika Holika Good Cera Super Ceramide Toner',
#     'Benton Fermentation Eye Cream 30g'
# ]

# for p in products:
#     if p['product_name'] in targets:
#         print(f'Updating: {p["product_name"]}')
#         image = get_image(p['product_url'])
#         if image:
#             p['image_url'] = image
#             print(f'Set image: {image}')
#         else:
#             print('No image found')

# # Save
# json.dump(products, open('data/products.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
# print('Updated products.json with real images for top recommendations')