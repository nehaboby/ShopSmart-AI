
from datetime import datetime, timezone

from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    orders = db.relationship(
        "Order",
        backref="user",
        lazy=True
    )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    items = db.relationship(
        "OrderItem",
        backref="order",
        cascade="all, delete-orphan",
        lazy=True
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
