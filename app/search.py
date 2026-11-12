
from sqlalchemy import or_
from app.models import Product


def search_products(keyword=None, category=None):
    query = Product.query

    if keyword:
        keyword = keyword.strip()
        if keyword:
            pattern = f"%{keyword}%"

            query = query.filter(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                    Product.category.ilike(pattern)
                )
            )

    if category:
        query = query.filter(
            Product.category.ilike(f"%{category.strip()}%")
        )

    return query.order_by(Product.name.asc()).all()
