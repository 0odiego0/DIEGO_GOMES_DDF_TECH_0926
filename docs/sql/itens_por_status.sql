-- Tabela. Quantidade de itens por status do pedido.
-- A soma dos status é 112.650.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
SELECT
  "order_status",
  COUNT(*) AS itens
FROM {{#2837-fact-order-items}}
GROUP BY "order_status"
ORDER BY itens DESC
