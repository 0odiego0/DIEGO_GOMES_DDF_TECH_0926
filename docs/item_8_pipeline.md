# Item 8 — Pipeline

O pipeline do item 8 não foi criado. A fonte deste case é um CSV, carregado em Coletar por Importar arquivos (`fact_order_items`, 112.650 linhas).

Em Coletar → Pipelines, o assistente de nova pipeline só oferece sistemas online: Zendesk, Mixpanel, PostgreSQL, Facebook Ads, StatsBomb, Google Analytics, DocumentDB, MongoDB, MySQL, VTEX, Amazon S3 e equivalentes. Não há opção de CSV nem de arquivo já importado.

Processar → Transformação, que seria o módulo para tratar um arquivo já dentro da plataforma, está bloqueado nesta conta. Sem essa opção, não havia como montar o passo `trusted` → `refined` em cima do CSV.
