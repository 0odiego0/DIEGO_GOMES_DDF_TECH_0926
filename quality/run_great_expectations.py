"""Relatório do item 4 com Great Expectations.

Roda sobre data/processed/fact_order_items.csv, onde os buracos de
categoria ainda estão. A zona trusted já corrigiu esses buracos; o
relatório registra a correção no texto, sem esconder a falha.

Uso (Python 3.12, não o 3.14):

    py -3.12 quality/run_great_expectations.py
"""

from pathlib import Path

import great_expectations as gx
import pandas as pd
from great_expectations.expectations import (
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToNotBeNull,
    ExpectCompoundColumnsToBeUnique,
    ExpectTableRowCountToEqual,
)

ROOT = Path(__file__).resolve().parents[1]
FACT = ROOT / "data" / "processed" / "fact_order_items.csv"
REVIEWS = ROOT / "data" / "raw" / "olist_order_reviews_dataset.csv"
CATEGORIES = ROOT / "data" / "raw" / "product_category_name_translation.csv"
REPORT = ROOT / "quality" / "relatorio_gx.md"

ORDER_STATUS = [
    "delivered",
    "shipped",
    "canceled",
    "unavailable",
    "invoiced",
    "processing",
    "created",
    "approved",
]


def validate(name, frame, expectations):
    context = gx.get_context(mode="ephemeral")
    source = context.data_sources.add_pandas(name)
    asset = source.add_dataframe_asset(name)
    batch_definition = asset.add_batch_definition_whole_dataframe("full")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": frame})
    suite = gx.ExpectationSuite(name=name)
    for expectation in expectations:
        suite.add_expectation(expectation)
    return batch.validate(suite)


def rows_from_result(result):
    lines = []
    for item in result["results"]:
        config = item["expectation_config"]
        column = config.get("kwargs", {}).get("column", "")
        label = config["type"]
        if column:
            label = f"{label} ({column})"
        success = "PASS" if item["success"] else "FAIL"
        observed = item.get("result", {}).get("observed_value", "")
        unexpected = item.get("result", {}).get("unexpected_count", "")
        detail = f"observado={observed}" if observed != "" else f"inesperados={unexpected}"
        lines.append(f"| {label} | {success} | {detail} |")
    return lines


def main():
    fact = pd.read_csv(FACT)
    reviews = pd.read_csv(REVIEWS)
    known = set(pd.read_csv(CATEGORIES)["product_category_name"])

    fact_result = validate(
        "fact_order_items",
        fact,
        [
            ExpectTableRowCountToEqual(value=112_650),
            ExpectCompoundColumnsToBeUnique(column_list=["order_id", "order_item_id"]),
            ExpectColumnValuesToNotBeNull(column="order_id"),
            ExpectColumnValuesToNotBeNull(column="product_id"),
            ExpectColumnValuesToNotBeNull(column="customer_id"),
            ExpectColumnValuesToBeBetween(column="price", min_value=0),
            ExpectColumnValuesToBeBetween(column="freight_value", min_value=0),
            ExpectColumnValuesToMatchRegex(
                column="order_purchase_timestamp",
                regex=r"^201[6-8]-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            ),
            ExpectColumnValuesToBeInSet(column="order_status", value_set=ORDER_STATUS),
            ExpectColumnValuesToNotBeNull(column="product_category_name"),
            ExpectColumnValuesToBeInSet(
                column="product_category_name",
                value_set=sorted(known),
            ),
        ],
    )
    review_result = validate(
        "order_reviews",
        reviews,
        [
            ExpectTableRowCountToEqual(value=99_224),
            ExpectColumnValuesToBeBetween(
                column="review_score", min_value=1, max_value=5
            ),
        ],
    )

    failed = [
        item
        for item in fact_result["results"] + review_result["results"]
        if not item["success"]
    ]
    lines = [
        "# Relatório Great Expectations",
        "",
        "Biblioteca: Great Expectations 1.9, suíte em `quality/run_great_expectations.py`.",
        "Arquivo medido: `data/processed/fact_order_items.csv` (antes da correção) e `olist_order_reviews_dataset.csv`.",
        "",
        f"Sucesso geral da fato: **{fact_result['success']}**. Sucesso geral dos reviews: **{review_result['success']}**.",
        "",
        "## Fato (processed)",
        "",
        "| Expectation | Resultado | Detalhe |",
        "| --- | --- | --- |",
        *rows_from_result(fact_result),
        "",
        "## Reviews",
        "",
        "| Expectation | Resultado | Detalhe |",
        "| --- | --- | --- |",
        *rows_from_result(review_result),
        "",
        "## O que está ruim",
        "",
        "- `product_category_name` nulo em 1.603 itens. A categoria não veio no cadastro.",
        "- 24 itens em `pc_gamer` e `portateis_cozinha_e_preparadores_de_alimentos` estão fora da tabela de tradução. O Great Expectations contou só esses 24 na checagem de conjunto; os nulos ficam na checagem de não nulo.",
        "",
        "## O que a zona trusted já corrigiu",
        "",
        "Em `data/trusted/fact_order_items.csv`, sem descartar as 112.650 linhas:",
        "",
        "- categoria vazia virou `sem_categoria` / `uncategorized` (1.603)",
        "- `pc_gamer` ganhou `gaming_pc` (9)",
        "- `portateis_cozinha_e_preparadores_de_alimentos` ganhou `portable_kitchen_and_food_preparers` (15)",
        "",
        f"Expectations que falharam nesta rodada: {len(failed)}. As duas de categoria são o buraco conhecido. As demais precisam passar.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"relatorio={REPORT}")
    print(f"fact_success={fact_result['success']}")
    print(f"review_success={review_result['success']}")
    for item in failed:
        config = item["expectation_config"]
        print(f"FAIL {config['type']} {config.get('kwargs', {}).get('column', '')}")

    unexpected_failures = [
        item
        for item in failed
        if item["expectation_config"]["kwargs"].get("column") != "product_category_name"
    ]
    if unexpected_failures or review_result["success"] is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
