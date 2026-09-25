-- Barra extra. Dez categorias com mais itens vendidos.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
SELECT
  "product_category_name",
  COUNT(*) AS itens
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
ORDER BY itens DESC
LIMIT 10
