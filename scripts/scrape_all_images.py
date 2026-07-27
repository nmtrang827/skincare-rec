# import json
# import requests
# from bs4 import BeautifulSoup
# import re
# import time
# import random

# def get_product_image_url(product_url, product_name):
#     """Extract the main product image URL from a lookfantastic product page"""
#     try:
#         # Add random delay to be respectful
#         time.sleep(random.uniform(1, 3))

#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Accept-Encoding': 'gzip, deflate',
#             'Connection': 'keep-alive',
#         }

#         response = requests.get(product_url, headers=headers, timeout=15)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Look for product images in multiple ways
#         images = soup.find_all('img')

#         # First, try to find images with product in alt text or src
#         for img in images:
#             src = img.get('src', '')
#             alt = img.get('alt', '').lower()

#             # Look for main product image
#             if src and 'static.thcdn.com/productimg/original/' in src:
#                 # Extract the core image URL
#                 match = re.search(r'url=(https://static\.thcdn\.com/productimg/original/[^&]+)', src)
#                 if match:
#                     core_url = match.group(1)
#                     print(f"  ✓ Found image for {product_name}")
#                     return core_url

#         # If no image found, try alternative patterns
#         for img in images:
#             src = img.get('src', '')
#             if src and 'thcdn.com' in src and ('product' in src.lower() or 'image' in src.lower()):
#                 if src.startswith('//'):
#                     src = 'https:' + src
#                 elif not src.startswith('http'):
#                     continue
#                 print(f"  ✓ Found alternative image for {product_name}")
#                 return src

#         print(f"  ✗ No image found for {product_name}")
#         return None

#     except requests.exceptions.RequestException as e:
#         print(f"  ✗ Request error for {product_name}: {e}")
#         return None
#     except Exception as e:
#         print(f"  ✗ Error processing {product_name}: {e}")
#         return None

# # Load products
# print("Loading products...")
# with open('data/products.json', 'r', encoding='utf-8') as f:
#     products = json.load(f)

# print(f"Found {len(products)} products")

# # Process all products that don't have real images
# updated_count = 0
# error_count = 0

# for i, product in enumerate(products):
#     product_name = product['product_name']
#     current_image = product.get('image_url', '')

#     # Skip if already has a real image
#     if current_image and 'static.thcdn.com' in current_image:
#         continue

#     print(f"[{i+1}/{len(products)}] Processing: {product_name[:50]}...")

#     # Get real image URL
#     real_image_url = get_product_image_url(product['product_url'], product_name)

#     if real_image_url:
#         product['image_url'] = real_image_url
#         updated_count += 1
#     else:
#         error_count += 1
#         # Keep existing image or set a default
#         if not current_image:
#             product['image_url'] = 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop&crop=center'

#     # Save progress every 50 products
#     if (i + 1) % 50 == 0:
#         with open('data/products.json', 'w', encoding='utf-8') as f:
#             json.dump(products, f, indent=2, ensure_ascii=False)
#         print(f"  Progress saved: {updated_count} updated, {error_count} errors so far")

# # Final save
# with open('data/products.json', 'w', encoding='utf-8') as f:
#     json.dump(products, f, indent=2, ensure_ascii=False)

# print("\n✅ COMPLETED!")
# print(f"Updated {updated_count} products with real images")
# print(f"Errors: {error_count}")
# print(f"Total products: {len(products)}")

# # Final stats
# real_images = [p for p in products if p.get('image_url', '').startswith('https://static.thcdn.com')]
# print(f"Products with real images: {len(real_images)}/{len(products)}")