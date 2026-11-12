
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    current_app
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from app import db, bcrypt
from app.models import User, Product, Order, OrderItem
from app.search import search_products
from app.recommendations import get_recommendations
from app.ai_chatbot import get_chat_response


main = Blueprint("main", __name__)


# ==========================================
# HOME PAGE
# ==========================================

@main.route("/")
def index():

    products = Product.query.filter(
        Product.stock > 0
    ).order_by(
        Product.created_at.desc()
    ).limit(8).all()

    recommendations = get_recommendations(limit=4)

    categories = [
        row[0]
        for row in db.session.query(
            Product.category
        ).distinct().all()
    ]

    return render_template(
        "index.html",
        products=products,
        recommendations=recommendations,
        categories=categories
    )


# ==========================================
# PRODUCT LISTING AND SEARCH
# ==========================================

@main.route("/products")
def products():

    keyword = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    product_list = search_products(keyword, category)

    categories = [
        row[0]
        for row in db.session.query(
            Product.category
        ).distinct().order_by(Product.category).all()
    ]

    return render_template(
        "products.html",
        products=product_list,
        q=keyword,
        keyword=keyword,
        category=category,
        categories=categories
    )


# ==========================================
# PRODUCT DETAILS
# ==========================================

@main.route("/product/<int:product_id>")
def product_detail(product_id):

    product = db.get_or_404(Product, product_id)

    related_products = get_recommendations(
        product_id=product.id,
        limit=4
    )

    return render_template(
        "product_detail.html",
        product=product,
        related_products=related_products
    )


# ==========================================
# USER REGISTRATION
# ==========================================

@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or len(password) < 8:

            flash(
                "Enter all details. Password must be at least 8 characters.",
                "danger"
            )

            return redirect(url_for("main.register"))

        if User.query.filter_by(email=email).first():

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(url_for("main.register"))

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(user)
            db.session.commit()

            flash(
                "Registration successful. Please log in.",
                "success"
            )

            return redirect(url_for("main.login"))

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "Registration failed"
            )

            flash(
                "Registration failed. Please try again.",
                "danger"
            )

    return render_template("register.html")


# ==========================================
# USER LOGIN
# ==========================================

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash(
                "Welcome back!",
                "success"
            )

            return redirect(url_for("main.index"))

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template("login.html")


# ==========================================
# USER LOGOUT
# ==========================================

@main.route("/logout")
@login_required
def logout():

    logout_user()

    session.pop("cart", None)

    flash(
        "You have logged out.",
        "success"
    )

    return redirect(url_for("main.index"))


# ==========================================
# SHOPPING CART
# ==========================================

@main.route("/cart")
def cart():

    cart_data = session.get("cart", {})

    cart_items = []
    subtotal = 0.0

    for product_id, quantity in cart_data.items():

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity <= 0:
            continue

        product = db.session.get(Product, product_id)

        if product:

            item_subtotal = product.price * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": item_subtotal
            })

            subtotal += item_subtotal

    total = subtotal

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        total=total
    )


# ==========================================
# ADD PRODUCT TO CART
# ==========================================

@main.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    product = db.get_or_404(Product, product_id)

    if product.stock <= 0:

        flash(
            "This product is out of stock.",
            "danger"
        )

        return redirect(
            request.referrer or url_for("main.products")
        )

    try:
        requested_quantity = int(
            request.form.get("quantity", 1)
        )
    except (TypeError, ValueError):

        flash(
            "Please enter a valid quantity.",
            "danger"
        )

        return redirect(
            url_for("main.product_detail", product_id=product.id)
        )

    if requested_quantity <= 0:

        flash(
            "Quantity must be at least 1.",
            "danger"
        )

        return redirect(
            url_for("main.product_detail", product_id=product.id)
        )

    cart_data = session.get("cart", {})

    key = str(product_id)

    try:
        current_quantity = int(cart_data.get(key, 0))
    except (TypeError, ValueError):
        current_quantity = 0

    new_quantity = current_quantity + requested_quantity

    if new_quantity > product.stock:

        flash(
            f"Only {product.stock} units are available.",
            "warning"
        )

    else:

        cart_data[key] = new_quantity

        session["cart"] = cart_data
        session.modified = True

        flash(
            "Product added to cart successfully.",
            "success"
        )

    return redirect(
        request.referrer or url_for("main.products")
    )


# ==========================================
# REMOVE PRODUCT FROM CART
# ==========================================

@main.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    cart_data = session.get("cart", {})

    cart_data.pop(str(product_id), None)

    session["cart"] = cart_data
    session.modified = True

    flash(
        "Product removed from cart.",
        "success"
    )

    return redirect(url_for("main.cart"))


# ==========================================
# CHECKOUT
# ==========================================

@main.route("/checkout", methods=["POST"])
@login_required
def checkout():

    cart_data = session.get("cart", {})

    if not cart_data:

        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect(url_for("main.cart"))

    try:

        order_items = []
        total = 0.0

        # Validate products and quantities first.

        for product_id, quantity in cart_data.items():

            try:
                product_id = int(product_id)
                quantity = int(quantity)
            except (TypeError, ValueError):

                raise ValueError(
                    "Invalid product or quantity in your cart."
                )

            product = db.session.get(Product, product_id)

            if (
                not product
                or quantity <= 0
                or product.stock < quantity
            ):

                raise ValueError(
                    "A product is unavailable or has insufficient stock."
                )

            item_total = product.price * quantity

            total += item_total

            order_items.append(
                (product, quantity)
            )

        # Create the order.

        order = Order(
            user_id=current_user.id,
            total_amount=total,
            status="Pending"
        )

        db.session.add(order)

        db.session.flush()

        # Create order items and update stock.

        for product, quantity in order_items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )

            db.session.add(order_item)

            product.stock -= quantity

        db.session.commit()

        session.pop("cart", None)

        flash(
            f"Order #{order.id} placed successfully!",
            "success"
        )

        return redirect(url_for("main.my_orders"))

    except ValueError as error:

        db.session.rollback()

        flash(
            str(error),
            "danger"
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Checkout failed"
        )

        flash(
            "Checkout failed. Please try again.",
            "danger"
        )

    return redirect(url_for("main.cart"))


# ==========================================
# MY ORDERS
# ==========================================

@main.route("/my-orders")
@login_required
def my_orders():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )


# ==========================================
# AI CHATBOT API
# ==========================================

@main.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    message = data.get("message", "")

    if (
        not isinstance(message, str)
        or not message.strip()
        or len(message) > 1000
    ):

        return jsonify({
            "reply": "Please enter a valid message."
        }), 400

    try:

        reply = get_chat_response(message)

        return jsonify({
            "reply": reply
        })

    except Exception:

        current_app.logger.exception(
            "Chat request failed"
        )

        return jsonify({
            "reply": "Sorry, something went wrong. Please try again."
        }), 500


# ==========================================
# PRODUCT SEARCH API
# ==========================================

@main.route("/api/search")
def api_search():

    keyword = request.args.get("q", "").strip()

    results = search_products(keyword)[:10]

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "image_url": product.image_url
        }

        for product in results
    ])


# ==========================================
# PRODUCT RECOMMENDATIONS API
# ==========================================

@main.route("/api/recommendations/<int:product_id>")
def api_recommendations(product_id):

    results = get_recommendations(
        product_id,
        limit=4
    )

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "image_url": product.image_url
        }

        for product in results
    ])
