# Relatório Great Expectations

Biblioteca: Great Expectations 1.9, suíte em `quality/run_great_expectations.py`.
Arquivo medido: `data/processed/fact_order_items.csv` (antes da correção) e `olist_order_reviews_dataset.csv`.

Sucesso geral da fato: **False**. Sucesso geral dos reviews: **True**.

## Fato (processed)

| Expectation | Resultado | Detalhe |
| --- | --- | --- |
| expect_table_row_count_to_equal | PASS | observado=112650 |
| expect_compound_columns_to_be_unique | PASS | inesperados=0 |
| expect_column_values_to_not_be_null (order_id) | PASS | inesperados=0 |
| expect_column_values_to_not_be_null (product_id) | PASS | inesperados=0 |
| expect_column_values_to_not_be_null (customer_id) | PASS | inesperados=0 |
| expect_column_values_to_be_between (price) | PASS | inesperados=0 |
| expect_column_values_to_be_between (freight_value) | PASS | inesperados=0 |
| expect_column_values_to_match_regex (order_purchase_timestamp) | PASS | inesperados=0 |
| expect_column_values_to_be_in_set (order_status) | PASS | inesperados=0 |
| expect_column_values_to_not_be_null (product_category_name) | FAIL | inesperados=1603 |
| expect_column_values_to_be_in_set (product_category_name) | FAIL | inesperados=24 |

## Reviews

| Expectation | Resultado | Detalhe |
| --- | --- | --- |
| expect_table_row_count_to_equal | PASS | observado=99224 |
| expect_column_values_to_be_between (review_score) | PASS | inesperados=0 |

## O que está ruim

- `product_category_name` nulo em 1.603 itens. A categoria não veio no cadastro.
- 24 itens em `pc_gamer` e `portateis_cozinha_e_preparadores_de_alimentos` estão fora da tabela de tradução. O Great Expectations contou só esses 24 na checagem de conjunto; os nulos ficam na checagem de não nulo.

## O que a zona trusted já corrigiu

Em `data/trusted/fact_order_items.csv`, sem descartar as 112.650 linhas:

- categoria vazia virou `sem_categoria` / `uncategorized` (1.603)
- `pc_gamer` ganhou `gaming_pc` (9)
- `portateis_cozinha_e_preparadores_de_alimentos` ganhou `portable_kitchen_and_food_preparers` (15)

Expectations que falharam nesta rodada: 2. As duas de categoria são o buraco conhecido. As demais precisam passar.
