# Qualidade

Checagens da fato enriquecida e dos reviews, em Python, sem biblioteca extra.

```bash
python quality/run_checks.py
```

O relatório sai em `quality/relatorio.md`. No arquivo da Coleta, duas checagens devem falhar: categoria vazia (1.603 itens) e categoria sem tradução (24 itens). Na zona `trusted`, essas correções passam e a contagem continua 112.650. Se uma checagem que deveria passar falhar, o script termina com código 1.

O relatório pedido pelo item 4 do case está em `quality/relatorio_gx.md`. Ele usa Great Expectations 1.9, no Python 3.12 (o 3.14 da máquina não tem essa biblioteca):

```bash
py -3.12 quality/run_great_expectations.py
```

Duas expectations falham de propósito: 1.603 categorias nulas e 24 categorias fora da tradução. As outras passam.
