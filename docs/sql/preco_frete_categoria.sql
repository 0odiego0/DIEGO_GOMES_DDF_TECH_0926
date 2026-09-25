-- Dispersão. Preço médio contra frete médio, um ponto por categoria.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
-- Eixo X: preco_medio. Eixo Y: frete_medio.
SELECT
  "product_category_name",
  AVG("price") AS preco_medio,
  AVG("freight_value") AS frete_medio
FROM {{#2837-fact-order-items}}
GROUP BY "product_category_name"
