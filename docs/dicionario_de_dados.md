# Dicionário de dados

Zonas usadas neste case:

| Zona | O que é hoje |
| --- | --- |
| `raw` | Os nove CSVs em `data/raw/`, como saíram do Kaggle |
| `trusted` | `data/trusted/fact_order_items.csv`. Mesmas 112.650 linhas, com categoria vazia e as duas traduções corrigidas |
| `refined` | Modelo estrela em `modeling/kimball.md`. Ainda no papel |

O arquivo da Coleta é `data/processed/fact_order_items.csv`. Ele é o join da fato com as dimensões de chave única. Pagamentos, reviews e geolocalização não entram nele. Medidas de qualidade: `quality/relatorio.md`.

Tipos abaixo são o significado da coluna. No CSV tudo chega como texto.

## fact_order_items

Grão: `order_id` + `order_item_id`. 112.650 linhas. Uma linha é uma unidade vendida. Não existe coluna de quantidade no Olist.

| Coluna | Tipo | Chave | Descrição | Qualidade |
| --- | --- | --- | --- | --- |
| `order_id` | texto | PK composta, FK do pedido | Pedido | Não nulo |
| `order_item_id` | inteiro | PK composta | Sequência do item dentro do pedido (1, 2, 3…) | Não nulo. O par com `order_id` é único |
| `product_id` | texto | FK de produto | Produto vendido | Não nulo |
| `seller_id` | texto | FK de vendedor | Vendedor do item | Não nulo |
| `shipping_limit_date` | timestamp | | Limite para o vendedor postar | Preenchido na fonte |
| `price` | decimal | | Preço do item, em reais | Numérico e >= 0 |
| `freight_value` | decimal | | Frete do item, em reais | Numérico e >= 0 |
| `customer_id` | texto | FK | Id do cliente neste pedido. Na Olist muda a cada pedido | Não nulo |
| `customer_unique_id` | texto | FK da dimensão de cliente | Cliente real, estável entre pedidos | Não nulo. É o grão de `dim_customer` |
| `customer_zip_code_prefix` | texto | | Prefixo de CEP do cliente | Texto, para não perder zero à esquerda |
| `customer_city` | texto | parte da FK de geo | Cidade do cliente | Junto com a UF forma `dim_geo` |
| `customer_state` | texto | parte da FK de geo | UF do cliente | Duas letras |
| `order_status` | texto | FK de status | Status do pedido | Conjunto fechado: delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| `order_purchase_timestamp` | timestamp | FK de data | Data da compra. É a data da série temporal | Parseável, entre 2016 e 2018, sem nulo |
| `order_approved_at` | timestamp | | Aprovação do pagamento | Pode ser nulo |
| `order_delivered_carrier_date` | timestamp | | Postagem na transportadora | Nulo quando o pedido não chegou a esse estágio |
| `order_delivered_customer_date` | timestamp | | Entrega ao cliente | Nulo quando o pedido não foi entregue |
| `order_estimated_delivery_date` | timestamp | | Prazo prometido | Usado para medir atraso junto com a entrega real |
| `product_category_name` | texto | FK de categoria | Categoria em português | No arquivo da Coleta, 1.603 nulos. Na trusted, esses itens são `sem_categoria` |
| `product_category_name_english` | texto | | Categoria traduzida | No arquivo da Coleta, 24 itens sem tradução. Na trusted: `gaming_pc` e `portable_kitchen_and_food_preparers` |
| `product_name_lenght` | inteiro | | Tamanho do nome do produto na origem | Grafia da Olist (`lenght`). O nome em si não vem no dataset |
| `product_description_lenght` | inteiro | | Tamanho da descrição na origem | A descrição longa será gerada no item 5 |
| `product_photos_qty` | inteiro | | Quantidade de fotos | Pode ser nulo no cadastro |
| `product_weight_g` | inteiro | | Peso em gramas | Pode ser nulo no cadastro |
| `product_length_cm` | inteiro | | Comprimento em centímetros | Pode ser nulo no cadastro |
| `product_height_cm` | inteiro | | Altura em centímetros | Pode ser nulo no cadastro |
| `product_width_cm` | inteiro | | Largura em centímetros | Pode ser nulo no cadastro |
| `seller_zip_code_prefix` | texto | | Prefixo de CEP do vendedor | Atributo de `dim_seller` |
| `seller_city` | texto | | Cidade do vendedor | Atributo de `dim_seller` |
| `seller_state` | texto | | UF do vendedor | Atributo de `dim_seller` |

Métrica derivada, ainda não materializada: `ticket_item` = `price` + `freight_value`.

## Tabelas que não entram nesta fato

### olist_order_payments_dataset

103.886 linhas. Grão: `order_id` + `payment_sequential`. Vira `fact_payments`. Não juntar na fato de itens: um pedido com dois pagamentos duplicaria `price`.

| Coluna | Tipo | Chave | Descrição |
| --- | --- | --- | --- |
| `order_id` | texto | PK composta, FK | Pedido |
| `payment_sequential` | inteiro | PK composta | Sequência do pagamento no pedido |
| `payment_type` | texto | | credit_card, boleto, voucher, debit_card |
| `payment_installments` | inteiro | | Número de parcelas |
| `payment_value` | decimal | | Valor daquela parcela ou meio. Não somar com `price` |

### olist_order_reviews_dataset

99.224 registros. Grão: `review_id`. Vira `fact_reviews`. O review é do pedido. Juntar no item multiplicaria a nota. O CSV tem mais linhas físicas do que registros porque o comentário contém quebra de linha.

| Coluna | Tipo | Chave | Descrição | Qualidade |
| --- | --- | --- | --- | --- |
| `review_id` | texto | PK | Review | Único |
| `order_id` | texto | FK | Pedido avaliado | Liga à visão comercial sem copiar a nota para cada item |
| `review_score` | inteiro | | Nota de 1 a 5 | Todos os registros estão na faixa |
| `review_comment_title` | texto | | Título, quando o cliente escreveu | Muitos nulos |
| `review_comment_message` | texto | | Comentário | Muitos nulos. Texto da visão de jornada |
| `review_creation_date` | timestamp | FK de data | Abertura do review | Data da visão 2 |
| `review_answer_timestamp` | timestamp | | Resposta | Com a criação, mede o tempo de resposta |

### olist_geolocation_dataset

1.000.163 linhas. Não é dimensão pronta: o mesmo prefixo de CEP se repete. Fica em `raw`. `dim_geo` da prova de conceito usa UF + cidade do cliente, que já estão na fato. Lat/long só entram se `dim_geo_br` for construída à parte.

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `geolocation_zip_code_prefix` | texto | Prefixo de CEP |
| `geolocation_lat` | decimal | Latitude |
| `geolocation_lng` | decimal | Longitude |
| `geolocation_city` | texto | Cidade |
| `geolocation_state` | texto | UF |

## Coleta e trusted

Os 1.603 itens sem categoria e os 24 sem tradução continuam em `data/processed/fact_order_items.csv`, para o relatório mostrar o buraco. A correção está em `data/trusted/fact_order_items.csv`: `sem_categoria` / `uncategorized`, `gaming_pc` e `portable_kitchen_and_food_preparers`. Nenhuma linha foi descartada.
