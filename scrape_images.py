# import json
# import requests
# from bs4 import BeautifulSoup
# import time
# import re

# def get_product_image_url(product_url):
#     """Extract the main product image URL from a lookfantastic product page"""
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
#         response = requests.get(product_url, headers=headers, timeout=10)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Look for the main product image
#         images = soup.find_all('img')

#         for img in images:
#             src = img.get('src', '')
#             alt = img.get('alt', '')

#             # Look for the main product image (usually has the product name in alt text and is large)
#             if src and src.startswith('https://www.lookfantastic.com/images?url=https://static.thcdn.com/productimg/original/'):
#                 # Extract the core image URL
#                 match = re.search(r'url=(https://static\.thcdn\.com/productimg/original/[^&]+)', src)
#                 if match:
#                     core_url = match.group(1)
#                     # Return the direct image URL without parameters
#                     return core_url

#         return None

#     except Exception as e:
#         print(f"Error fetching {product_url}: {e}")
#         return None

# # Load products
# with open('data/products.json', 'r', encoding='utf-8') as f:
#     products = json.load(f)

# print(f"Processing {len(products)} products...")

# # Update products with real image URLs (limit to first 50 to avoid overwhelming server)
# updated_count = 0
# for i, product in enumerate(products[:50]):  # Process first 50 products
#     if i % 10 == 0:  # Progress indicator
#         print(f"Processed {i}/50 products...")

#     product_url = product['product_url']
#     current_image = product.get('image_url', '')

#     # Skip if already has a real image URL (not a placeholder)
#     if current_image and 'static.thcdn.com' in current_image:
#         continue

#     # Get real image URL
#     real_image_url = get_product_image_url(product_url)

#     if real_image_url:
#         product['image_url'] = real_image_url
#         updated_count += 1
#         print(f"Updated {product['product_name']}: {real_image_url}")
#     else:
#         print(f"Could not find image for {product['product_name']}")

#     # Be nice to the server
#     time.sleep(1)  # 1 second delay

# # Save updated products
# with open('data/products.json', 'w', encoding='utf-8') as f:
#     json.dump(products, f, indent=2, ensure_ascii=False)

# print(f"Updated {updated_count} products with real image URLs")