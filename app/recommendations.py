
from app.models import Product


def get_recommendations(product_id=None, limit=4):
    query = Product.query.filter(Product.stock > 0)

    if product_id:
        current = db_product = Product.query.get(product_id)

        if current:
            query = query.filter(
                Product.category == current.category,
                Product.id != current.id
            )

    products = query.order_by(
        Product.created_at.desc()
    ).limit(limit).all()

    if len(products) < limit:
        existing_ids = [p.id for p in products]

        fallback = Product.query.filter(
            Product.stock > 0,
            ~Product.id.in_(existing_ids)
        ).order_by(Product.created_at.desc()).limit(
            limit - len(products)
        ).all()

        products.extend(fallback)

    return products
