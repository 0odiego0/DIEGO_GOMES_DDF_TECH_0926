# Case técnico Dadosfera

Prova de conceito para um marketplace brasileiro: da base de pedidos até uma fato pronta para análise, com o corte de 100.000 registros já atendido. O roteiro completo está em `planejamento.md`. O ponto em que o trabalho local para e a plataforma começa está em `docs/carga_dadosfera.md`.

## Narrativa

O cliente quer decidir categoria, prazo e experiência de compra sem esperar uma stack fragmentada. A base é o [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0). A fato é o item de pedido, não o pedido: `olist_orders` tem 99.441 linhas e fica abaixo do corte.

## O que sobe na Dadosfera

Arquivo: `data/trusted/fact_order_items.csv`

- 112.650 linhas de dados, mais o cabeçalho
- Grão: `order_id` + `order_item_id`
- Categoria vazia já corrigida para `sem_categoria` (1.603 itens)
- Duas categorias sem tradução oficial já com inglês: `gaming_pc` (9) e `portable_kitchen_and_food_preparers` (15)

Não enviar como dataset principal `olist_orders_dataset` nem `olist_geolocation_dataset`.

## Como reproduzir os arquivos

Com os nove CSVs do Olist em `data/raw/`:

```bash
python scripts/build_fact_order_items.py
python scripts/build_trusted_fact.py
python quality/run_checks.py
```

Os CSVs gerados não entram no Git. Fonte, licença e contagens: `data/README.md`.

Repositório: https://github.com/0odiego0/DIEGO_GOMES_DDF_TECH_0926

## Links na Dadosfera

- Coleta: https://app.dadosfera.ai/pt-BR/collect/import-files/042644c1-7b87-4cca-9ce1-db15150e2ace
- Catálogo: https://app.dadosfera.ai/pt-BR/catalog/data-assets/5e679bfc-bf7e-425a-856c-effa23489398
- Painel Metabase (`Diego Gomes - 09_2026`): https://metabase-treinamentos.dadosfera.ai/dashboard/304-diego-gomes-09-2026
- Pipeline: não criado. A observação está em `docs/item_8_pipeline.md`.
- Data App: https://diegogomesddftech0926-2oytppb9rtbdi2ame7hjfw.streamlit.app/
- Vídeo unlisted: a preencher

As consultas do painel, os tipos de gráfico e os prints estão em `docs/sql/consultas.md`.

## Mapa do repositório

| Caminho | Papel |
| --- | --- |
| `planejamento.md` | Roteiro do case |
| `checklist.md` | Onde paramos |
| `modeling/kimball.md` | Estrela, duas visões |
| `docs/dicionario_de_dados.md` | Colunas, chaves e qualidade |
| `docs/carga_dadosfera.md` | O que fazer no módulo de Coleta |
| `quality/relatorio_gx.md` | Relatório do item 4 (Great Expectations) |
| `docs/sql/consultas.md` | SQL, tipos de gráfico e prints do item 7 |
| `docs/item_8_pipeline.md` | Por que o pipeline do item 8 não foi criado |
| `notebooks/features_llm.ipynb` | Notebook do item 5, cópia do Colab |
| `app/streamlit_app.py` | Data App do item 9 |
