# Checklist de retomada

Contexto para continuar o case sem reler a conversa. O roteiro completo continua em `planejamento.md`. Este arquivo só diz onde paramos.

Atualizado em 25/09/2026, com o link do painel e as SQL do item 7.

## Decisões já tomadas

- Base: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Licença CC BY-NC-SA 4.0. Amazon Reviews 2023 foi descartado (grande demais, em inglês, sem pedido/frete/UF).
- Fato: `olist_order_items_dataset`. Grão = item de pedido (`order_id` + `order_item_id`). **112.650** registros.
- `olist_orders_dataset` tem 99.441 pedidos e fica abaixo do corte de 100.000. Não pode ser a fato nem a única tabela carregada.
- Arquivo que sobe na Coleta da Dadosfera: `data/trusted/fact_order_items.csv` (112.650). O arquivo em `data/processed/` guarda o buraco de categoria e não sobe. Roteiro: `docs/carga_dadosfera.md`.
- Fora desse join: pagamentos, reviews e `olist_geolocation_dataset` (1.000.163 CEPs). Pagamentos e reviews viram tabelas próprias. Geo, se entrar, vira `dim_geo_br`.
- O script do join roda localmente. Google Colab é só o item 5 (descrições e features de LLM), nos notebooks de `notebooks/`.
- Modelo alvo: Kimball, escrito em `modeling/kimball.md`. Visão comercial em `fact_order_items` (112.650). Visão da jornada em `fact_reviews` (99.224, grão do review, sem multiplicar pela quantidade de itens). `fact_payments` (103.886) apoia a visão comercial e não se soma com `price`.
- CSVs crus e a fato gerada não entram no Git (`.gitignore`). A amostra de features, `data/refined/features_amostra.csv`, entra: são 147 linhas.
- No Metabase a fato carregada na coleção é o cartão `{{#2837-fact-order-items}}`, no **Sample Database**. A consulta tem de estar nesse banco. No Snowflake o cartão não existe.

## Feito

- [x] `planejamento.md` com Kanban, riscos, custos e caminho crítico (ainda não versionado no Git).
- [x] Olist baixado em `data/raw/` (nove CSVs).
- [x] Fonte, licença, contagens e como reproduzir em `data/README.md`.
- [x] `.gitignore` para `data/raw/*.csv` e `data/processed/*.csv`.
- [x] Fato enriquecida gerada: 112.650 linhas. Nenhum item ficou sem pedido, cliente, produto ou vendedor.
- [x] Buracos do dado original registrados: 1.603 itens sem categoria; 24 itens sem tradução (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`).
- [x] Item 6 no papel: `modeling/kimball.md` (justificativa, grãos, duas visões, diagrama das camadas). Falta materializar na Dadosfera.
- [x] Dicionário em `docs/dicionario_de_dados.md`.
- [x] Suíte de qualidade em `quality/run_checks.py`. No arquivo em `data/processed/` o relatório ainda mostra as duas falhas conhecidas. Em `data/trusted/fact_order_items.csv` a categoria vazia virou `sem_categoria` (1.603), `pc_gamer` virou `gaming_pc` (9) e a categoria de portáteis de cozinha virou `portable_kitchen_and_food_preparers` (15). A contagem segue 112.650.
- [x] `README.md`, roteiro de carga em `docs/carga_dadosfera.md` e pasta `docs/prints/` para o print das 112.650 linhas.
- [x] Acesso à Dadosfera com o usuário `diego.dgadm`.
- [x] Item 2, carga: `data/trusted/fact_order_items.csv` importado em 24/09/2026, status Sucesso, nome `fact_order_items`. Link no README: https://app.dadosfera.ai/pt-BR/collect/import-files/042644c1-7b87-4cca-9ce1-db15150e2ace
- [x] Item 3, catálogo: `fact_order_items` aparece como Table, dono `diego.dgadm`, descrição com zona `trusted`. Link: https://app.dadosfera.ai/pt-BR/catalog/data-assets/5e679bfc-bf7e-425a-856c-effa23489398
- [x] Item 4: relatório Great Expectations em `quality/relatorio_gx.md`. Duas falhas conhecidas (1.603 nulos e 24 fora da tradução). O resto passa. Rodar com `py -3.12`. Print em `docs/prints/relatorio_great_expectations.png`.
- [x] Item 5, local: amostra de 147 produtos em `data/refined/features_amostra.csv`. Faixas conferidas (médio 79, baixo 46, alto 22). Prints em `docs/prints/features_llm_amostra.png` e `docs/prints/output_llm1.png`.
- [x] Coleção do Metabase: `Diego Gomes - 09_2026`. Painel: https://metabase-treinamentos.dadosfera.ai/dashboard/304-diego-gomes-09-2026
- [x] SQL do item 7 em `docs/sql/` e no markdown `docs/sql/consultas.md`. Link do painel no README.

## Próximo passo

Seguir para o vídeo unlisted, o app Streamlit e o bônus DALL-E. O repositório público está em https://github.com/0odiego0/DIEGO_GOMES_DDF_TECH_0926.

## Ainda por fazer

### Antes de implementar na plataforma

- [x] Repositório público: https://github.com/0odiego0/DIEGO_GOMES_DDF_TECH_0926
- [x] `README.md` da raiz.
- [x] Item 6 no papel: `modeling/kimball.md` e o diagrama `raw` → `trusted` → `refined`.
- [x] Amostra de descrições e features gerada no Colab (147 produtos, dois por categoria). CSV em `data/refined/features_amostra.csv`.
- [x] Notebook do Colab em `notebooks/features_llm.ipynb`.
- [ ] (Opcional) Sintético e/ou `dim_geo_br`. O corte de 100 mil já está garantido sem isso.

### Bloqueado por acesso ou chave

- [x] Acesso à Dadosfera (usuário `diego.dgadm`).
- [x] Chave de API de LLM usada no Colab (segredo `open_ai`). O bônus DALL-E ainda não foi feito.
- [x] Conta Google (Colab) usada no item 5. Streamlit Community Cloud ainda não.
- [ ] Conta YouTube para o vídeo unlisted.

### Itens do case (nível Excelente)

- [x] Item 2. Carga de `fact_order_items` feita em 24/09/2026. Link no README. Print: `docs/prints/dados_importados.png`.
- [x] Item 3. Dicionário local e ativo catalogado na Dadosfera. Print: `docs/prints/dados_catalogados.png`.
- [x] Item 4. Relatório Great Expectations em `quality/relatorio_gx.md`. Print: `docs/prints/relatorio_great_expectations.png`.
- [x] Item 5, geração. Amostra em `data/refined/features_amostra.csv` e notebook em `notebooks/features_llm.ipynb`. Falta anotar o link da carga dessa amostra no README, se a ficha do catálogo já existir.
- [x] Item 6 no papel. Falta materializar as duas visões na plataforma, se o avaliador cobrar além do `modeling/kimball.md`.
- [ ] Item 7. Link no README, SQL em `docs/sql/consultas.md` e print da dispersão em `docs/prints/Correlação preço e frete.png`. Confirmar se esse card está no painel junto com barra, linha, tabela e número.
- [ ] Item 8. Pipeline catalogado (`trusted` → `refined`).
- [ ] Item 9. Streamlit de similaridade/EDA, com README de publicação.
- [ ] Bônus. Gerador de pitch + imagem (DALL-E), prompts em `app/prompts.md`.
- [ ] Item 10. Vídeo unlisted no YouTube, link testado em janela anônima.

Núcleo primeiro. Spark, API de catálogo, Power BI, Common Data Model e microtransformação SQL só entram com o nível Excelente já de pé.

## Como retomar o join

Na raiz do repositório, com os CSVs em `data/raw/`:

```bash
python scripts/build_fact_order_items.py
```

A saída esperada é `linhas=112650`.
