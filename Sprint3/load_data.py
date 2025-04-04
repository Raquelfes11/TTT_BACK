import requests

dummy_url = "https://dummyjson.com/products?limit=100"
res = requests.get(dummy_url)
data = res.json()["products"]

category_set = {}
auction_commands = []
category_commands = []
bid_commands = []

# CATEGORY
for product in data:
    cat_name = product.get("category", "Unknown").capitalize()  # Default to "Unknown" if no category
    if cat_name not in category_set:
        category_set[cat_name] = f"Category(name='{cat_name}')"

# Convert categories to commands
for i, (cat_name, cmd) in enumerate(category_set.items()):
    category_commands.append(f"cat_{i} = {cmd}\ncat_{i}.save()  # ID -> {i + 1}")

# Map category name to variable name
category_var_map = {name: f"cat_{i}" for i, name in enumerate(category_set)}

# AUCTIONS
for i, product in enumerate(data):
    title = product.get("title", "").replace("'", "\\'")
    description = product.get("description", "").replace("'", "\\'")
    price = product.get("price", 0)
    rating = product.get("rating", 0)
    stock = product.get("stock", 0)
    brand = product.get("brand", "Unknown").replace("'", "\\'")  # Default to "Unknown" if no brand
    thumbnail = product.get("thumbnail", "").replace("'", "\\'")  # Escape any single quotes in the URL
    category_var = category_var_map.get(product.get("category", "").capitalize(), "cat_0")  # Default to first category
    
    auction_commands.append(
        f"""a_{i} = Auction(
    title='{title}',
    description='{description}',
    price={price},
    rating={rating},
    stock={stock},
    brand='{brand}',
    category={category_var},
    thumbnail='{thumbnail}',
    closing_date=timezone.now() + timedelta(days=5)
)
a_{i}.save()"""
    )

# PUJAS (opcional: 2 por auction)
for i in range(len(data)):
    bid_commands.append(
        f"""Bid(auction=a_{i}, price=a_{i}.price + 2, bidder='usuario1').save()
Bid(auction=a_{i}, price=a_{i}.price + 5, bidder='usuario2').save()"""
    )

# Combine all
with open("load_data_commands.txt", "w", encoding="utf-8") as f:
    f.write("from auctions.models import Category, Auction, Bid\n")
    f.write("from django.utils import timezone\n")
    f.write("from datetime import timedelta\n\n")
    
    f.write("# ---- CATEGORÍAS ----\n")
    f.write("\n".join(category_commands))
    f.write("\n\n# ---- SUBASTAS ----\n")
    f.write("\n\n".join(auction_commands))
    f.write("\n\n# ---- PUJAS ----\n")
    f.write("\n\n".join(bid_commands))



