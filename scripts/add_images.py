# import json
# import codecs

# # Read the products
# with codecs.open('data/products.json', 'r', encoding='utf-8') as f:
#     # products = json.load(f)

# print(f'Original products: {len(products)}')

# # Different skincare images for variety
# skincare_images = [
#     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1631730359585-38a4935cb0b6?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400&h=300&fit=crop&crop=center",
#     "https://images.unsplash.com/photo-1631730359585-38a4935cb0b6?w=400&h=300&fit=crop&crop=center"
# ]

# # Add image URLs to products that don't have them
# for i, product in enumerate(products):
#     if 'image_url' not in product:
#         # Cycle through the images
#         image_index = i % len(skincare_images)
#         product['image_url'] = skincare_images[image_index]

# products_with_images = [p for p in products if 'image_url' in p]
# print(f'Products with image_url after update: {len(products_with_images)}')

# # Write back to file
# with codecs.open('data/products.json', 'w', encoding='utf-8') as f:
#     json.dump(products, f, indent=2, ensure_ascii=False)

# print('Updated products.json with image URLs for all products')