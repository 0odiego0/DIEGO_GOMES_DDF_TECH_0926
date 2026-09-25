-- Linha. Série temporal da receita pelo mês da compra.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
SELECT
  FORMATDATETIME("order_purchase_timestamp", 'yyyy-MM') AS mes,
  SUM("price") AS receita
FROM {{#2837-fact-order-items}}
GROUP BY FORMATDATETIME("order_purchase_timestamp", 'yyyy-MM')
ORDER BY mes
