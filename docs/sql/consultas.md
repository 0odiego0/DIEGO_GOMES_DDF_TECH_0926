# Consultas do item 7

Painel: [Diego Gomes - 09_2026](https://metabase-treinamentos.dadosfera.ai/dashboard/304-diego-gomes-09-2026)

Banco: Sample Database. Tabela: cartão `{{#2837-fact-order-items}}` (Fact Order Items). A queda do último ponto da série é o mês final incompleto da Olist.

| Pergunta | Tipo | Arquivo | Print |
| --- | --- | --- | --- |
| Receita por categoria | Barra | `receita_por_categoria.sql` | `docs/prints/receita_por_categoria.png` |
| Receita por mês | Linha | `receita_por_mes.sql` | `docs/prints/receita_por_mes.png` |
| Itens por status | Tabela | `itens_por_status.sql` | `docs/prints/itens_por_status.png` |
| Ticket médio | Número | `ticket_medio.sql` | `docs/prints/ticket_medio.png` |
| Top 10 categorias em volume | Barra | `top10_categorias_volume.sql` | `docs/prints/top10_categorias_volume.png` |
| Preço e frete por categoria | Dispersão | `preco_frete_categoria.sql` | `docs/prints/Correlação preço e frete.png` |

A soma dos status em `itens_por_status` é 112.650. O ticket médio é R$ 120,65.

## Receita por categoria

```sql
SELECT
  "product_category_name",
  SUM("price") AS receita
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
ORDER BY receita DESC
LIMIT 14
```

## Receita por mês

```sql
SELECT
  FORMATDATETIME("order_purchase_timestamp", 'yyyy-MM') AS mes,
  SUM("price") AS receita
FROM {{#2837-fact-order-items}}
GROUP BY FORMATDATETIME("order_purchase_timestamp", 'yyyy-MM')
ORDER BY mes
```

## Itens por status

```sql
SELECT
  "order_status",
  COUNT(*) AS itens
FROM {{#2837-fact-order-items}}
GROUP BY "order_status"
ORDER BY itens DESC
```

## Ticket médio

```sql
SELECT AVG("price") AS ticket_medio
FROM {{#2837-fact-order-items}}
```

## Top 10 categorias em volume

```sql
SELECT
  "product_category_name",
  COUNT(*) AS itens
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
ORDER BY itens DESC
LIMIT 10
```

## Preço e frete por categoria

Quinto tipo, diferente da segunda barra do top 10. Eixo X: `preco_medio`. Eixo Y: `frete_medio`.

```sql
SELECT
  "product_category_name",
  AVG("price") AS preco_medio,
  AVG("freight_value") AS frete_medio
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
```
