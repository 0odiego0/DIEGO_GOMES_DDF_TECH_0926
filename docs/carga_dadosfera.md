# Carga na Dadosfera

Tudo o que dá para fazer fora da plataforma já está feito. Este arquivo é o roteiro do item 2, dentro do módulo de Coleta.

## Antes de abrir a plataforma

1. Confirmar o acesso com o e-mail da vaga. A mensagem vem de `suporte@dadosfera.ai`.
2. Ter em disco o arquivo `data/trusted/fact_order_items.csv`. Se a pasta `data/trusted/` estiver vazia, na raiz do projeto:

```bash
python scripts/build_fact_order_items.py
python scripts/build_trusted_fact.py
```

A segunda saída tem de ser `linhas=112650`.

## O que enviar

| | |
| --- | --- |
| Arquivo | `data/trusted/fact_order_items.csv` |
| Linhas de dados | 112.650 (o cabeçalho não conta) |
| Nome sugerido do ativo | `fact_order_items` |
| Descrição sugerida | Fato de item de pedido do marketplace Olist, 2016–2018. Grão `order_id` + `order_item_id`. Zona trusted: categoria vazia virou `sem_categoria`. |
| Tags sugeridas | `ecommerce`, `olist`, `fato`, `trusted`, `09_2026` |

O arquivo traz preço, frete, status, datas, cidade e UF do cliente, categoria, atributos físicos do produto e cidade e UF do vendedor.

## O que não enviar como dataset principal

- `olist_orders_dataset.csv`: 99.441 pedidos, abaixo do corte.
- `olist_geolocation_dataset.csv`: 1.000.163 CEPs, cerca de 60 MB, não é a fato.
- `data/processed/fact_order_items.csv`: é o mesmo grão, mas ainda com 1.603 categorias vazias. Serve de evidência local em `quality/relatorio.md`, não de carga.

Pagamentos (103.886) e reviews (99.224) ficam para uma carga seguinte, como tabelas de apoio. Não bloqueiam o item 2.

## Depois que a carga terminar

1. Na tela do dataset, conferir se a contagem de registros é 112.650.
2. Salvar o print dessa tela em `docs/prints/`. O número de linhas precisa aparecer.
3. Copiar o link do ativo para a seção "Links na Dadosfera" do `README.md`.
4. Guardar o identificador da tabela. O item 7 usa esse id para achar o dataset no módulo de visualização.

O catálogo (item 3) usa o texto de `docs/dicionario_de_dados.md`. A coleção do Metabase, quando chegar o item 7, segue o padrão `Nome Sobrenome - 09_2026`.
