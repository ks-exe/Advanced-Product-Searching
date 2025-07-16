from collections import defaultdict
import bisect
from models import Product

# Initialize data structures
products = []
products_by_id = {}
products_by_brand = defaultdict(list)
products_by_category = defaultdict(list)
products_by_price = []  # Sorted list of (price, pid, product)
product_names = []  # For fuzzy name search

product_id_counter = 1

def generate_products():
    global product_id_counter

    initial_products = [
        # Electronics (10)
        ("Apple iPhone 14 Pro", "Apple", 419999, "In Stock", "Latest iPhone with A16 Bionic chip.", "Electronics", 5),
        ("Samsung Galaxy S23 Ultra", "Samsung", 389999, "In Stock", "Flagship Samsung phone.", "Electronics", 4),
        ("Sony WH-1000XM5", "Sony", 84999, "In Stock", "Noise-canceling headphones.", "Electronics", 5),
        ("Xiaomi Redmi Note 12", "Xiaomi", 74999, "Out of Stock", "Budget phone with great performance.", "Electronics", 4),
        ("Dell 27-inch Monitor", "Dell", 44000, "In Stock", "Full HD UltraSharp monitor.", "Electronics", 4),
        ("Canon EOS 1500D", "Canon", 115000, "In Stock", "DSLR Camera with 24.1MP CMOS Sensor.", "Electronics", 4),
        ("JBL Flip 5 Speaker", "JBL", 14999, "In Stock", "Waterproof portable Bluetooth speaker.", "Electronics", 5),
        ("Samsung Galaxy Tab S8", "Samsung", 119999, "Out of Stock", "Android flagship tablet.", "Electronics", 4),
        ("Apple AirPods Pro", "Apple", 49999, "In Stock", "Active noise cancellation wireless earbuds.", "Electronics", 5),
        ("Mi Power Bank 3i", "Xiaomi", 2999, "In Stock", "20000mAh fast charging power bank.", "Electronics", 4),

        # Laptops (10)
        ("Dell XPS 13", "Dell", 289999, "In Stock", "Premium ultrabook laptop.", "Laptops", 5),
        ("HP Spectre x360", "HP", 259999, "In Stock", "Convertible 2-in-1 laptop.", "Laptops", 4),
        ("Apple MacBook Air M2", "Apple", 329999, "In Stock", "Lightweight MacBook with M2 chip.", "Laptops", 5),
        ("Lenovo ThinkPad X1 Carbon", "Lenovo", 275000, "In Stock", "Business ultrabook, durable and light.", "Laptops", 4),
        ("Asus ROG Zephyrus G14", "Asus", 209999, "In Stock", "Gaming laptop with Ryzen 9.", "Laptops", 5),
        ("Acer Aspire 7", "Acer", 99999, "In Stock", "Budget gaming and productivity laptop.", "Laptops", 4),
        ("MSI Modern 15", "MSI", 119999, "In Stock", "Sleek design, powerful performance.", "Laptops", 4),
        ("HP Pavilion 14", "HP", 84999, "In Stock", "Affordable everyday laptop.", "Laptops", 3),
        ("Dell Inspiron 15", "Dell", 79999, "In Stock", "15-inch laptop for students.", "Laptops", 4),
        ("Apple MacBook Pro M3", "Apple", 459999, "Out of Stock", "High-end MacBook for professionals.", "Laptops", 5),

        # Clothing (10)
        ("Levi's 501 Jeans", "Levi's", 7999, "In Stock", "Classic straight-fit jeans.", "Clothing", 4),
        ("Nike Air Max", "Nike", 15999, "Out of Stock", "Popular running shoes.", "Clothing", 5),
        ("Adidas Tiro 21 Track Pants", "Adidas", 4999, "In Stock", "Comfortable football pants.", "Clothing", 4),
        ("Zara Casual Shirt", "Zara", 2999, "In Stock", "Slim fit printed shirt.", "Clothing", 4),
        ("H&M Basic T-shirt", "H&M", 1299, "In Stock", "Soft cotton t-shirt.", "Clothing", 3),
        ("Uniqlo Ultra Light Down Jacket", "Uniqlo", 5999, "In Stock", "Warm, light winter jacket.", "Clothing", 5),
        ("Puma Men's Hoodie", "Puma", 3499, "In Stock", "Classic black pullover hoodie.", "Clothing", 4),
        ("Levi's Trucker Jacket", "Levi's", 8999, "Out of Stock", "Iconic denim jacket.", "Clothing", 5),
        ("Allen Solly Formal Trousers", "Allen Solly", 2499, "In Stock", "Slim fit formal pants.", "Clothing", 3),
        ("Adidas Ultraboost Shoes", "Adidas", 19999, "In Stock", "High performance running shoes.", "Clothing", 5),

        # Grocery (10)
        ("Nestle Milk Pack", "Nestle", 200, "In Stock", "1 liter milk pack.", "Grocery", 3),
        ("Tata Salt", "Tata", 60, "In Stock", "Iodized salt 1kg.", "Grocery", 4),
        ("Amul Butter", "Amul", 105, "In Stock", "100g salted butter.", "Grocery", 5),
        ("Kissan Mixed Fruit Jam", "Kissan", 145, "In Stock", "500g fruit jam.", "Grocery", 4),
        ("Tropicana Orange Juice", "Tropicana", 120, "In Stock", "1 liter orange juice.", "Grocery", 4),
        ("Aashirvaad Atta", "Aashirvaad", 400, "In Stock", "10kg whole wheat flour.", "Grocery", 5),
        ("Fortune Sunflower Oil", "Fortune", 160, "In Stock", "1 liter cooking oil.", "Grocery", 4),
        ("MTR Masala", "MTR", 70, "In Stock", "100g garam masala powder.", "Grocery", 3),
        ("Brook Bond Red Label Tea", "Brook Bond", 120, "In Stock", "250g tea pack.", "Grocery", 4),
        ("Britannia Good Day Biscuits", "Britannia", 35, "Out of Stock", "200g pack of biscuits.", "Grocery", 4),

        # Books (10)
        ("Python Crash Course", "Eric Matthes", 2500, "In Stock", "Best-selling Python programming book.", "Books", 5),
        ("The Alchemist", "Paulo Coelho", 1200, "In Stock", "International bestseller novel.", "Books", 4),
        ("Atomic Habits", "James Clear", 1800, "In Stock", "Guide to building good habits.", "Books", 5),
        ("Ikigai", "Hector Garcia", 1400, "In Stock", "Japanese secret to a long and happy life.", "Books", 4),
        ("The Lean Startup", "Eric Ries", 2100, "In Stock", "Entrepreneurship and innovation guide.", "Books", 5),
        ("Think and Grow Rich", "Napoleon Hill", 1100, "In Stock", "Classic self-help book.", "Books", 4),
        ("Deep Work", "Cal Newport", 1700, "In Stock", "Rules for focused success.", "Books", 5),
        ("To Kill a Mockingbird", "Harper Lee", 900, "In Stock", "Pulitzer Prize-winning novel.", "Books", 5),
        ("Rich Dad Poor Dad", "Robert Kiyosaki", 1600, "Out of Stock", "Personal finance classic.", "Books", 4),
        ("The Psychology of Money", "Morgan Housel", 1950, "In Stock", "Timeless lessons on wealth.", "Books", 5),
    ]

    for item in initial_products:
        add_product_obj(Product(product_id_counter, *item))
        product_id_counter += 1

def add_product_obj(product):
    # Add to master list
    products.append(product)
    # Index by ID
    products_by_id[product.pid] = product
    # Index by brand
    products_by_brand[product.brand.lower()].append(product)
    # Index by category
    products_by_category[product.category.lower()].append(product)
    # Index by price (maintain sorted order - add pid for unique key)
    bisect.insort(products_by_price, (product.price, product.pid, product))
    # Store names for fuzzy search
    product_names.append(product.name)

def remove_product_obj(pid):
    """Remove a product from all data structures."""
    if pid not in products_by_id:
        return False
    
    product = products_by_id[pid]
    
    # Remove from master list
    products.remove(product)
    
    # Remove from ID index
    del products_by_id[pid]
    
    # Remove from brand index
    brand_products = products_by_brand[product.brand.lower()]
    brand_products.remove(product)
    if not brand_products:
        del products_by_brand[product.brand.lower()]
    
    # Remove from category index
    category_products = products_by_category[product.category.lower()]
    category_products.remove(product)
    if not category_products:
        del products_by_category[product.category.lower()]
    
    # Remove from price index
    for i, (price, prod_id, p) in enumerate(products_by_price):
        if p.pid == pid:
            del products_by_price[i]
            break
    
    # Remove from names list
    product_names.remove(product.name)
    
    return True

# Generate initial products
generate_products()

# Search Functions
def search_by_id(pid):
    return [products_by_id[pid]] if pid in products_by_id else []

def search_by_name(keyword):
    keyword = keyword.lower()
    return [p for p in products if keyword in p.name.lower()]

def search_by_brand(keyword):
    keyword = keyword.lower()
    return products_by_brand.get(keyword, [])

def search_by_category(keyword):
    keyword = keyword.lower()
    return products_by_category.get(keyword, [])

def search_by_price_range(min_price, max_price):
    # products_by_price is sorted by price, pid
    idx_start = bisect.bisect_left(products_by_price, (min_price, -float('inf')))
    idx_end = bisect.bisect_right(products_by_price, (max_price, float('inf')))
    return [p for _, _, p in products_by_price[idx_start:idx_end]]

def search_by_top_ratings(top_n=3):
    return sorted(products, key=lambda x: x.rating, reverse=True)[:top_n] 