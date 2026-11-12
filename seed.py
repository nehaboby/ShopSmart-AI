
from app import create_app, db
from app.models import Product

app = create_app()

sample_products = [
    {
        "name": "Wireless Headphones",
        "description": "Premium wireless headphones with noise cancellation.",
        "category": "Electronics",
        "price": 2499,
        "image_url": "https://placehold.co/600x400?text=Headphones",
        "stock": 20
    },
    {
        "name": "Smart Watch",
        "description": "Smart watch with fitness and health tracking features.",
        "category": "Electronics",
        "price": 3499,
        "image_url": "https://placehold.co/600x400?text=Smart+Watch",
        "stock": 15
    },
    {
        "name": "Running Shoes",
        "description": "Comfortable lightweight running shoes.",
        "category": "Fashion",
        "price": 1999,
        "image_url": "https://placehold.co/600x400?text=Shoes",
        "stock": 25
    },
    {
        "name": "Travel Backpack",
        "description": "Durable backpack with multiple storage compartments.",
        "category": "Accessories",
        "price": 1299,
        "image_url": "https://placehold.co/600x400?text=Backpack",
        "stock": 30
    },
    {
        "name": "Bluetooth Speaker",
        "description": "Portable speaker with rich sound and long battery life.",
        "category": "Electronics",
        "price": 1599,
        "image_url": "https://placehold.co/600x400?text=Speaker",
        "stock": 18
    },
    {
        "name": "Women's Handbag",
        "description": "Elegant everyday handbag with spacious storage.",
        "category": "Fashion",
        "price": 1799,
        "image_url": "https://placehold.co/600x400?text=Handbag",
        "stock": 12
    },
    {
        "name": "Mechanical Keyboard",
        "description": "Mechanical keyboard suitable for work and gaming.",
        "category": "Electronics",
        "price": 2899,
        "image_url": "https://placehold.co/600x400?text=Keyboard",
        "stock": 10
    },
    {
        "name": "Sunglasses",
        "description": "Stylish sunglasses with UV protection.",
        "category": "Accessories",
        "price": 999,
        "image_url": "https://placehold.co/600x400?text=Sunglasses",
        "stock": 40
    }
]


with app.app_context():
    db.create_all()

    if Product.query.count() == 0:
        for item in sample_products:
            db.session.add(Product(**item))

        db.session.commit()
        print("Sample products inserted successfully!")

    else:
        print("Products already exist. No duplicate records added.")
