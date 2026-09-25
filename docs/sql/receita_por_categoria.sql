-- Barra. Receita das 14 categorias de maior faturamento.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
SELECT
  "product_category_name",
  SUM("price") AS receita
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
ORDER BY receita DESC
LIMIT 14
