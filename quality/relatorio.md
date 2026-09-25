# Relatório de qualidade

Suíte em `quality/run_checks.py`. A primeira parte mede a fato enriquecida antes da correção, `data/processed/fact_order_items.csv`, e os reviews. A segunda mede `data/trusted/fact_order_items.csv`, que é o arquivo que sobe na Coleta da Dadosfera.

Os **FAIL** marcados como falha conhecida são os buracos do dado original. Eles continuam no arquivo `processed` de propósito. A correção aparece só na zona `trusted`.

| Checagem | Resultado | Esperado | Detalhe |
| --- | --- | --- | --- |
| Volume da fato >= 100.000 | PASS | passar | 112650 linhas |
| Volume da fato = 112.650 | PASS | passar | 112650 linhas |
| Grão order_id + order_item_id único | PASS | passar | 0 duplicatas |
| order_id não nulo | PASS | passar | 0 nulos |
| product_id não nulo | PASS | passar | 0 nulos |
| seller_id não nulo | PASS | passar | 0 nulos |
| customer_id não nulo | PASS | passar | 0 nulos |
| price numérico e >= 0 | PASS | passar | 0 fora da regra |
| freight_value numérico e >= 0 | PASS | passar | 0 fora da regra |
| order_purchase_timestamp parseável | PASS | passar | 0 inválidos |
| order_purchase_timestamp entre 2016 e 2018 | PASS | passar | 0 fora da janela |
| order_status em conjunto fechado | PASS | passar | ok |
| product_category_name não nulo | FAIL | falha conhecida | 1603 nulos (esperado 1603) |
| Nulos de categoria permanecem 1.603 | PASS | passar | 1603 nulos |
| Categoria com tradução em inglês | FAIL | falha conhecida | 24 itens; categorias: pc_gamer, portateis_cozinha_e_preparadores_de_alimentos |
| Categorias sem tradução são só as duas conhecidas | PASS | passar | 24 itens em ['pc_gamer', 'portateis_cozinha_e_preparadores_de_alimentos'] |
| Reviews = 99.224 | PASS | passar | 99224 registros |
| review_score entre 1 e 5 | PASS | passar | 0 fora da faixa |
| Trusted conserva 112.650 linhas | PASS | passar | 112650 linhas |
| Trusted conserva o grão único | PASS | passar | 0 duplicatas |
| Trusted sem categoria vazia nem tradução vazia | PASS | passar | 0 vazios |
| Trusted marca 1.603 itens como sem_categoria | PASS | passar | 1603 itens |
| Trusted traduz as duas categorias que faltavam | PASS | passar | pc_gamer=9, portateis=15 |

## O que está ruim

- 1603 itens sem `product_category_name`. A categoria não veio no cadastro do produto.
- 24 itens nas categorias pc_gamer, portateis_cozinha_e_preparadores_de_alimentos, que não existem em `product_category_name_translation`.
- O review é texto do pedido. A nota em si está íntegra (1 a 5). O problema de categoria afeta a visão comercial e as features de LLM, não o score.

## O que a zona trusted corrigiu

- 1.603 categorias vazias viraram `sem_categoria` / `uncategorized`. Nenhuma linha foi descartada.
- 9 itens `pc_gamer` receberam `gaming_pc`.
- 15 itens `portateis_cozinha_e_preparadores_de_alimentos` receberam `portable_kitchen_and_food_preparers`.
- Preço, frete, grão e datas já passavam e foram copiados sem mudança.

O arquivo corrigido, e o que sobe na Dadosfera, é `data/trusted/fact_order_items.csv`, gerado por `scripts/build_trusted_fact.py`. O arquivo em `data/processed/` não foi alterado.
