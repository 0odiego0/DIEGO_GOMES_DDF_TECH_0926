# Dados

Os CSVs crus do Olist ficam em `data/raw/` e **não entram no Git** (ver `.gitignore`). Esta pasta explica de onde vêm, quantas linhas têm e o que sobe para a Dadosfera.

## Fonte e licença

- **Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Quem publicou:** Olist, no Kaggle (`olistbr/brazilian-ecommerce`)
- **O que é:** pedidos reais de 2016 a 2018 em marketplaces brasileiros, com item, pagamento, review, produto, vendedor e CEP
- **Licença:** [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
  - citar a Olist e o link do Kaggle
  - uso não comercial
  - obras derivadas na mesma licença

## Como reproduzir

1. Conta no Kaggle.
2. Baixar o zip em [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
3. Extrair os nove CSVs para `data/raw/`.

Pelo Kaggle CLI, na raiz do repositório:

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

## Contagem (prova de volume)

Conferida com o módulo `csv` do Python sobre os arquivos em `data/raw/`. A linha de cabeçalho não entra na conta. Reviews têm quebra de linha dentro do comentário; a contagem abaixo é de registros, não de linhas físicas do arquivo.

| Arquivo | Registros | Papel |
| --- | ---: | --- |
| `olist_order_items_dataset.csv` | **112.650** | **Fato.** Passa de 100.000. |
| `olist_order_payments_dataset.csv` | 103.886 | Pagamentos. Passa de 100.000. Não é a fato. |
| `olist_geolocation_dataset.csv` | 1.000.163 | CEP → lat/long. Não entra na carga principal. |
| `olist_orders_dataset.csv` | 99.441 | Pedido. Abaixo do corte. |
| `olist_customers_dataset.csv` | 99.441 | Cliente. Abaixo do corte. |
| `olist_order_reviews_dataset.csv` | 99.224 | Texto de review. Abaixo do corte. |
| `olist_products_dataset.csv` | 32.951 | Produto. |
| `olist_sellers_dataset.csv` | 3.095 | Vendedor. |
| `product_category_name_translation.csv` | 71 | Categoria em inglês. |

O grão da fato é um item de pedido. A chave é `order_id` + `order_item_id`. Colunas: `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value`.

## Fato enriquecida

Arquivo da Coleta: `data/processed/fact_order_items.csv`.

Ele não entra no Git. Para gerar de novo, na raiz do repositório, com os CSVs já em `data/raw/`:

```bash
python scripts/build_fact_order_items.py
```

O script faz left join só com tabelas de chave única, para o grão não mudar:

- `olist_orders_dataset` por `order_id`
- `olist_customers_dataset` por `customer_id`
- `olist_products_dataset` por `product_id`
- `product_category_name_translation` por `product_category_name`
- `olist_sellers_dataset` por `seller_id`

Fora do join: pagamentos, reviews e `olist_geolocation_dataset`.

Esse script roda na máquina local. O Google Colab fica para o item 5 (descrições e features de LLM), nos notebooks de `notebooks/`.

### Contagem depois do join

Rodado em 22/09/2026 sobre os CSVs locais:

| Verificação | Resultado |
| --- | --- |
| Linhas | **112.650** (igual à fato crua) |
| Item sem pedido, cliente, produto ou vendedor | 0 |
| Item sem categoria no cadastro | 1.603 |
| Item com categoria sem tradução | 24 (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) |

As 1.603 categorias vazias e as duas categorias fora da tabela de tradução são buraco do dado original. O join não as criou e não as descartou. A correção fica em `data/trusted/fact_order_items.csv` e não altera este arquivo.

## Zona trusted

```bash
python scripts/build_trusted_fact.py
```

O script lê a fato da Coleta e grava `data/trusted/fact_order_items.csv`, ainda com 112.650 linhas:

- categoria vazia vira `sem_categoria` / `uncategorized` (1.603 itens)
- `pc_gamer` ganha `gaming_pc` (9 itens)
- `portateis_cozinha_e_preparadores_de_alimentos` ganha `portable_kitchen_and_food_preparers` (15 itens)

| Zona | Arquivo | Papel |
| --- | --- | --- |
| `raw` | `data/raw/*.csv` | CSVs do Kaggle, sem regra de negócio |
| `trusted` | `data/trusted/fact_order_items.csv` | Mesmo grão, com categoria vazia e tradução corrigidas |
| `refined` | modelo em `modeling/kimball.md` | Fatos e dimensões. Ainda no papel |

## O que sobe para a Dadosfera

O arquivo da carga é `data/trusted/fact_order_items.csv` (112.650 linhas de dados). O passo a passo está em `docs/carga_dadosfera.md`.

`data/processed/fact_order_items.csv` não sobe: ele guarda as 1.603 categorias vazias para o relatório de qualidade mostrar o buraco antes da correção.

`olist_geolocation_dataset` não entra nessa carga: são 1.000.163 CEPs e cerca de 60 MB. Geolocalização, se for usada, vira dimensão à parte (`dim_geo_br`).

Pagamentos e reviews continuam como tabelas de apoio. A segunda fato do modelo (`fact_reviews`) nasce de `olist_order_reviews_dataset` e não precisa, sozinha, passar de 100.000.

Colunas e chaves: `docs/dicionario_de_dados.md`. Checagens e o que falhou: `quality/relatorio.md`.
