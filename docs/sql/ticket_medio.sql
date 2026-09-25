-- Número. Ticket médio do item, em reais. Resultado: 120,65.
-- Banco: Sample Database. Cartão: Fact Order Items #2837.
SELECT AVG("price") AS ticket_medio
FROM {{#2837-fact-order-items}}
