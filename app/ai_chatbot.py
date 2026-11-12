
import re

from flask import current_app
from app.models import Product


def normalize_word(word):
    """Normalize simple plurals for product matching."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"

    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]

    return word


def get_chat_response(message):
    message = message.strip()

    if not message:
        return "Please enter a shopping question."

    # Get products that are currently in stock.
    products = Product.query.filter(
        Product.stock > 0
    ).order_by(Product.price.asc()).limit(100).all()

    if not products:
        return "Sorry, there are currently no products available."

    # Prepare the product catalog for the AI.
    product_context = "\n".join(
        [
            (
                f"Name: {p.name}, "
                f"Category: {p.category}, "
                f"Price: Rs. {p.price:.2f}, "
                f"Stock: {p.stock}, "
                f"Description: {p.description}"
            )
            for p in products
        ]
    )

    # Try OpenAI when an API key is configured.
    api_key = current_app.config.get("OPENAI_API_KEY")

    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=current_app.config.get(
                    "AI_MODEL", "gpt-4.1-mini"
                ),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are ShopSmart AI, a friendly "
                            "e-commerce shopping assistant.\n\n"
                            "Use only the supplied product catalog. "
                            "Never invent products, prices or stock.\n"
                            "Only recommend products that genuinely "
                            "match the customer's request.\n"
                            "If a requested product is not in the "
                            "catalog, clearly say it is unavailable. "
                            "Do not recommend unrelated products.\n"
                            "When recommending products, mention "
                            "their names and prices.\n"
                            "Never claim to process payments or "
                            "place orders.\n\n"
                            f"PRODUCT CATALOG:\n{product_context}"
                        )
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=400
            )

            answer = response.choices[0].message.content

            if answer:
                return answer.strip()

        except Exception:
            current_app.logger.exception(
                "OpenAI chatbot error. Using local product search."
            )

    # Local fallback chatbot.
    # This works without an OpenAI API key.

    query = message.lower()

    # Identify greetings.
    greetings = [
        "hello", "hi", "hey", "good morning",
        "good afternoon", "good evening"
    ]

    if query.strip(" !?.") in greetings:
        return (
            "Hello! Welcome to ShopSmart AI. "
            "I can help you find products, explore categories "
            "and discover products within your budget. "
            "What are you looking for today?"
        )

    # Identify budget.
    budget = None

    budget_match = re.search(
        r"(?:under|below|less than|within|maximum|max|upto|up to)"
        r"\s*(?:rs\.?|₹|inr)?\s*([\d,]+)",
        query
    )

    if budget_match:
        budget = float(
            budget_match.group(1).replace(",", "")
        )

    # Identify requested category.
    category_keywords = {
        "electronics": [
            "electronics", "electronic", "gadgets",
            "tech", "technology"
        ],
        "fashion": [
            "fashion", "clothes", "clothing",
            "shoes", "handbag", "bags"
        ],
        "accessories": [
            "accessories", "sunglasses", "backpack",
            "accessory"
        ]
    }

    selected_category = None

    for category, keywords in category_keywords.items():
        if any(word in query for word in keywords):
            selected_category = category
            break

    # Start with all available products.
    matching = products

    # Apply budget filter.
    if budget is not None:
        matching = [
            p for p in matching
            if p.price <= budget
        ]

    # Apply category filter.
    if selected_category:
        matching = [
            p for p in matching
            if p.category.lower() == selected_category
        ]

    # Identify product search keywords.
    product_keywords = re.findall(
        r"[a-zA-Z]+",
        query
    )

    ignored_words = {
        "the", "and", "for", "with", "under", "below",
        "less", "than", "within", "maximum", "max",
        "upto", "from", "some", "suggest", "recommend",
        "recommendation", "show", "find", "want", "need",
        "looking", "search", "products", "product",
        "please", "give", "me", "what", "are", "can",
        "you", "help", "best", "good", "price", "cheap",
        "affordable", "rupees", "inr", "electronics",
        "electronic", "fashion", "accessories", "gadgets",
        "tech", "technology", "clothes", "clothing",
        "hello", "hi", "hey", "do", "does", "have",
        "any", "there", "is", "available", "available",
        "want", "would", "like", "some", "please",
        "your", "our", "shop", "under", "within"
    }

    search_terms = [
        normalize_word(word)
        for word in product_keywords
        if word not in ignored_words and len(word) > 2
    ]

    # Search only for products that match the requested terms.
    if search_terms:
        keyword_matches = []

        for product in matching:
            product_text = (
                f"{product.name} {product.description or ''}"
            ).lower()

            product_words = {
                normalize_word(word)
                for word in re.findall(
                    r"[a-zA-Z]+",
                    product_text
                )
            }

            if any(
                term in product_words
                for term in search_terms
            ):
                keyword_matches.append(product)

        # IMPORTANT:
        # Even if no products match, keep the result empty.
        # Never show unrelated products.
        matching = keyword_matches

    # Return matching product recommendations.
    if matching:
        matching = sorted(
            matching,
            key=lambda p: p.price
        )[:5]

        response_lines = [
            "Here are some products I recommend:"
        ]

        for product in matching:
            response_lines.append(
                f"- {product.name} "
                f"({product.category}) - "
                f"Rs. {product.price:.2f}"
            )

        if budget is not None:
            response_lines.append(
                f"\nAll listed products are within your "
                f"Rs. {budget:,.0f} budget."
            )

        return "\n".join(response_lines)

    # Helpful response when no product matches.
    if budget is not None:
        return (
            f"I couldn't find a matching product under "
            f"Rs. {budget:,.0f}. "
            "Would you like to increase your budget?"
        )

    if search_terms:
        requested_product = " ".join(search_terms)

        return (
            f"Sorry, we don't currently have "
            f"{requested_product} in our catalog. "
            "Would you like to explore our available products?"
        )

    return (
        "I can help you find products from our catalog. "
        "Try questions such as:\n"
        "- Suggest some electronics products.\n"
        "- Find headphones under Rs. 3000.\n"
        "- Show me fashion products.\n"
        "- Recommend affordable accessories."
    )
