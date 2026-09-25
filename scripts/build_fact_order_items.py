"""Monta a fato enriquecida no grão de item de pedido.

Junta apenas tabelas em que a chave é única, para a contagem continuar
igual à de olist_order_items_dataset (112.650). Pagamentos, reviews e
geolocalização ficam de fora: multiplicariam linhas ou inchariam o arquivo.

Uso, na raiz do repositório:

    python scripts/build_fact_order_items.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "fact_order_items.csv"

EXPECTED_ROWS = 112_650


def load_rows(filename):
    path = RAW / filename
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def index_by(rows, key, label):
    lookup = {}
    for row in rows:
        value = row[key]
        if value in lookup:
            raise SystemExit(f"Chave duplicada em {label}.{key}: {value}")
        lookup[value] = row
    return lookup


def main():
    items = load_rows("olist_order_items_dataset.csv")
    orders = index_by(load_rows("olist_orders_dataset.csv"), "order_id", "orders")
    customers = index_by(
        load_rows("olist_customers_dataset.csv"), "customer_id", "customers"
    )
    products = index_by(
        load_rows("olist_products_dataset.csv"), "product_id", "products"
    )
    sellers = index_by(load_rows("olist_sellers_dataset.csv"), "seller_id", "sellers")
    categories = index_by(
        load_rows("product_category_name_translation.csv"),
        "product_category_name",
        "categories",
    )

    fieldnames = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "product_category_name",
        "product_category_name_english",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]

    missing = {
        "order": 0,
        "customer": 0,
        "product": 0,
        "seller": 0,
        "category_blank": 0,
        "category_untranslated": 0,
    }
    untranslated = set()
    seen = set()
    enriched = []

    for item in items:
        grain = (item["order_id"], item["order_item_id"])
        if grain in seen:
            raise SystemExit(f"Grão duplicado na fato: {grain}")
        seen.add(grain)

        order = orders.get(item["order_id"])
        if order is None:
            missing["order"] += 1
            order = {}
        customer = customers.get(order.get("customer_id", ""))
        if customer is None:
            missing["customer"] += 1
            customer = {}
        product = products.get(item["product_id"])
        if product is None:
            missing["product"] += 1
            product = {}
        seller = sellers.get(item["seller_id"])
        if seller is None:
            missing["seller"] += 1
            seller = {}
        category_name = product.get("product_category_name", "")
        category = categories.get(category_name) if category_name else None
        if not category_name:
            missing["category_blank"] += 1
            category = {}
        elif category is None:
            missing["category_untranslated"] += 1
            untranslated.add(category_name)
            category = {}

        enriched.append(
            {
                "order_id": item["order_id"],
                "order_item_id": item["order_item_id"],
                "product_id": item["product_id"],
                "seller_id": item["seller_id"],
                "shipping_limit_date": item["shipping_limit_date"],
                "price": item["price"],
                "freight_value": item["freight_value"],
                "customer_id": order.get("customer_id", ""),
                "customer_unique_id": customer.get("customer_unique_id", ""),
                "customer_zip_code_prefix": customer.get("customer_zip_code_prefix", ""),
                "customer_city": customer.get("customer_city", ""),
                "customer_state": customer.get("customer_state", ""),
                "order_status": order.get("order_status", ""),
                "order_purchase_timestamp": order.get("order_purchase_timestamp", ""),
                "order_approved_at": order.get("order_approved_at", ""),
                "order_delivered_carrier_date": order.get(
                    "order_delivered_carrier_date", ""
                ),
                "order_delivered_customer_date": order.get(
                    "order_delivered_customer_date", ""
                ),
                "order_estimated_delivery_date": order.get(
                    "order_estimated_delivery_date", ""
                ),
                "product_category_name": category_name,
                "product_category_name_english": category.get(
                    "product_category_name_english", ""
                ),
                "product_name_lenght": product.get("product_name_lenght", ""),
                "product_description_lenght": product.get(
                    "product_description_lenght", ""
                ),
                "product_photos_qty": product.get("product_photos_qty", ""),
                "product_weight_g": product.get("product_weight_g", ""),
                "product_length_cm": product.get("product_length_cm", ""),
                "product_height_cm": product.get("product_height_cm", ""),
                "product_width_cm": product.get("product_width_cm", ""),
                "seller_zip_code_prefix": seller.get("seller_zip_code_prefix", ""),
                "seller_city": seller.get("seller_city", ""),
                "seller_state": seller.get("seller_state", ""),
            }
        )

    if len(enriched) != len(items):
        raise SystemExit(
            f"O join mudou o número de linhas: {len(items)} -> {len(enriched)}"
        )
    if len(enriched) != EXPECTED_ROWS:
        raise SystemExit(
            f"Contagem inesperada: {len(enriched)} (esperado {EXPECTED_ROWS})"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)

    print(f"linhas={len(enriched)}")
    print(f"arquivo={OUT}")
    for label, count in missing.items():
        print(f"sem_{label}={count}")
    if untranslated:
        print("categorias_sem_traducao=" + ",".join(sorted(untranslated)))


if __name__ == "__main__":
    main()
