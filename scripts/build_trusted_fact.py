"""Gera a fato da zona trusted a partir do arquivo da Coleta.

Não altera data/processed/fact_order_items.csv. A suíte de qualidade
continua medindo esse arquivo para os buracos originais seguirem visíveis.

Regras:
- categoria vazia vira sem_categoria / uncategorized
- pc_gamer ganha gaming_pc
- portateis_cozinha_e_preparadores_de_alimentos ganha
  portable_kitchen_and_food_preparers

Uso, na raiz do repositório:

    python scripts/build_trusted_fact.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "fact_order_items.csv"
OUT = ROOT / "data" / "trusted" / "fact_order_items.csv"

EXPECTED_ROWS = 112_650
EXPECTED_BLANK = 1_603
ENGLISH_BY_CATEGORY = {
    "pc_gamer": "gaming_pc",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_and_food_preparers",
}


def blank(value):
    return value is None or str(value).strip() == ""


def main():
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)

    filled_blank = 0
    translated = {name: 0 for name in ENGLISH_BY_CATEGORY}

    for row in rows:
        category = row["product_category_name"]
        if blank(category):
            row["product_category_name"] = "sem_categoria"
            row["product_category_name_english"] = "uncategorized"
            filled_blank += 1
            continue
        english = ENGLISH_BY_CATEGORY.get(category)
        if english is not None:
            row["product_category_name_english"] = english
            translated[category] += 1

    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"Contagem mudou: {len(rows)}")
    if filled_blank != EXPECTED_BLANK:
        raise SystemExit(f"Categorias vazias: {filled_blank} (esperado {EXPECTED_BLANK})")
    if any(blank(row["product_category_name"]) or blank(row["product_category_name_english"]) for row in rows):
        raise SystemExit("Ainda há categoria ou tradução vazia.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"linhas={len(rows)}")
    print(f"arquivo={OUT}")
    print(f"sem_categoria={filled_blank}")
    for name, count in translated.items():
        print(f"{name}={count}")


if __name__ == "__main__":
    main()
