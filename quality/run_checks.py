"""Checagens de qualidade da fato enriquecida e dos reviews.

A suíte usa só a biblioteca padrão. Checagens marcadas como espera=fail
documentam buracos já conhecidos do dado original. As demais devem passar.
Se uma checagem que deveria passar falhar, o processo termina com código 1.

Uso, na raiz do repositório:

    python quality/run_checks.py
"""

import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
FACT = ROOT / "data" / "processed" / "fact_order_items.csv"
TRUSTED = ROOT / "data" / "trusted" / "fact_order_items.csv"
REPORT = ROOT / "quality" / "relatorio.md"

EXPECTED_ROWS = 112_650
EXPECTED_REVIEWS = 99_224
EXPECTED_BLANK_CATEGORY = 1_603
EXPECTED_UNTRANSLATED = 24
UNTRANSLATED_NAMES = {
    "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos",
}
ORDER_STATUS = {
    "delivered",
    "shipped",
    "canceled",
    "unavailable",
    "invoiced",
    "processing",
    "created",
    "approved",
}
PURCHASE_MIN = datetime(2016, 1, 1)
PURCHASE_MAX = datetime(2018, 12, 31, 23, 59, 59)


def load(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def blank(value):
    return value is None or str(value).strip() == ""


def parse_number(value):
    if blank(value):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_timestamp(value):
    if blank(value):
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


class Suite:
    def __init__(self):
        self.rows = []

    def add(self, name, ok, detail, expect_fail=False):
        self.rows.append(
            {
                "name": name,
                "ok": ok,
                "detail": detail,
                "expect_fail": expect_fail,
            }
        )

    @property
    def unexpected(self):
        bad = []
        for row in self.rows:
            if row["expect_fail"] and row["ok"]:
                bad.append(row["name"] + " (esperava falha e passou)")
            if not row["expect_fail"] and not row["ok"]:
                bad.append(row["name"])
        return bad


def main():
    fact = load(FACT)
    reviews = load(RAW / "olist_order_reviews_dataset.csv")
    categories = load(RAW / "product_category_name_translation.csv")
    known_categories = {row["product_category_name"] for row in categories}

    suite = Suite()
    suite.add(
        "Volume da fato >= 100.000",
        len(fact) >= 100_000,
        f"{len(fact)} linhas",
    )
    suite.add(
        "Volume da fato = 112.650",
        len(fact) == EXPECTED_ROWS,
        f"{len(fact)} linhas",
    )

    grains = [(row["order_id"], row["order_item_id"]) for row in fact]
    suite.add(
        "Grão order_id + order_item_id único",
        len(grains) == len(set(grains)),
        f"{len(grains) - len(set(grains))} duplicatas",
    )

    for column in ("order_id", "product_id", "seller_id", "customer_id"):
        missing = sum(1 for row in fact if blank(row[column]))
        suite.add(
            f"{column} não nulo",
            missing == 0,
            f"{missing} nulos",
        )

    bad_price = 0
    bad_freight = 0
    for row in fact:
        price = parse_number(row["price"])
        freight = parse_number(row["freight_value"])
        if price is None or price < 0:
            bad_price += 1
        if freight is None or freight < 0:
            bad_freight += 1
    suite.add("price numérico e >= 0", bad_price == 0, f"{bad_price} fora da regra")
    suite.add(
        "freight_value numérico e >= 0",
        bad_freight == 0,
        f"{bad_freight} fora da regra",
    )

    bad_purchase = 0
    outside_window = 0
    for row in fact:
        stamp = parse_timestamp(row["order_purchase_timestamp"])
        if stamp is None:
            bad_purchase += 1
            continue
        if stamp < PURCHASE_MIN or stamp > PURCHASE_MAX:
            outside_window += 1
    suite.add(
        "order_purchase_timestamp parseável",
        bad_purchase == 0,
        f"{bad_purchase} inválidos",
    )
    suite.add(
        "order_purchase_timestamp entre 2016 e 2018",
        outside_window == 0,
        f"{outside_window} fora da janela",
    )

    unknown_status = sorted(
        {row["order_status"] for row in fact if row["order_status"] not in ORDER_STATUS}
    )
    suite.add(
        "order_status em conjunto fechado",
        not unknown_status,
        "ok" if not unknown_status else ", ".join(unknown_status),
    )

    blank_category = sum(1 for row in fact if blank(row["product_category_name"]))
    suite.add(
        "product_category_name não nulo",
        blank_category == 0,
        f"{blank_category} nulos (esperado {EXPECTED_BLANK_CATEGORY})",
        expect_fail=True,
    )
    suite.add(
        "Nulos de categoria permanecem 1.603",
        blank_category == EXPECTED_BLANK_CATEGORY,
        f"{blank_category} nulos",
    )

    untranslated = []
    for row in fact:
        name = row["product_category_name"]
        if blank(name):
            continue
        if name not in known_categories or blank(row["product_category_name_english"]):
            untranslated.append(name)
    untranslated_names = sorted(set(untranslated))
    suite.add(
        "Categoria com tradução em inglês",
        not untranslated,
        f"{len(untranslated)} itens; categorias: {', '.join(untranslated_names) or 'nenhuma'}",
        expect_fail=True,
    )
    suite.add(
        "Categorias sem tradução são só as duas conhecidas",
        set(untranslated_names) == UNTRANSLATED_NAMES
        and len(untranslated) == EXPECTED_UNTRANSLATED,
        f"{len(untranslated)} itens em {untranslated_names}",
    )

    bad_score = 0
    for row in reviews:
        try:
            score = int(row["review_score"])
        except ValueError:
            bad_score += 1
            continue
        if score < 1 or score > 5:
            bad_score += 1
    suite.add(
        "Reviews = 99.224",
        len(reviews) == EXPECTED_REVIEWS,
        f"{len(reviews)} registros",
    )
    suite.add(
        "review_score entre 1 e 5",
        bad_score == 0,
        f"{bad_score} fora da faixa",
    )

    trusted = load(TRUSTED)
    suite.add(
        "Trusted conserva 112.650 linhas",
        len(trusted) == EXPECTED_ROWS,
        f"{len(trusted)} linhas",
    )
    trusted_grains = [(row["order_id"], row["order_item_id"]) for row in trusted]
    suite.add(
        "Trusted conserva o grão único",
        len(trusted_grains) == len(set(trusted_grains)),
        f"{len(trusted_grains) - len(set(trusted_grains))} duplicatas",
    )
    trusted_blank = sum(
        1
        for row in trusted
        if blank(row["product_category_name"]) or blank(row["product_category_name_english"])
    )
    suite.add(
        "Trusted sem categoria vazia nem tradução vazia",
        trusted_blank == 0,
        f"{trusted_blank} vazios",
    )
    sem_categoria = sum(1 for row in trusted if row["product_category_name"] == "sem_categoria")
    suite.add(
        "Trusted marca 1.603 itens como sem_categoria",
        sem_categoria == EXPECTED_BLANK_CATEGORY
        and sum(1 for row in trusted if row["product_category_name_english"] == "uncategorized")
        == EXPECTED_BLANK_CATEGORY,
        f"{sem_categoria} itens",
    )
    gaming = sum(
        1
        for row in trusted
        if row["product_category_name"] == "pc_gamer"
        and row["product_category_name_english"] == "gaming_pc"
    )
    kitchen = sum(
        1
        for row in trusted
        if row["product_category_name"] == "portateis_cozinha_e_preparadores_de_alimentos"
        and row["product_category_name_english"] == "portable_kitchen_and_food_preparers"
    )
    suite.add(
        "Trusted traduz as duas categorias que faltavam",
        gaming == 9 and kitchen == 15,
        f"pc_gamer={gaming}, portateis={kitchen}",
    )

    lines = [
        "# Relatório de qualidade",
        "",
        "Suíte em `quality/run_checks.py`. A primeira parte mede a fato enriquecida antes da correção, `data/processed/fact_order_items.csv`, e os reviews. A segunda mede `data/trusted/fact_order_items.csv`, que é o arquivo que sobe na Coleta da Dadosfera.",
        "",
        "Os **FAIL** marcados como falha conhecida são os buracos do dado original. Eles continuam no arquivo `processed` de propósito. A correção aparece só na zona `trusted`.",
        "",
        "| Checagem | Resultado | Esperado | Detalhe |",
        "| --- | --- | --- | --- |",
    ]
    for row in suite.rows:
        result = "PASS" if row["ok"] else "FAIL"
        expected = "falha conhecida" if row["expect_fail"] else "passar"
        lines.append(
            f"| {row['name']} | {result} | {expected} | {row['detail']} |"
        )

    lines.extend(
        [
            "",
            "## O que está ruim",
            "",
            f"- {blank_category} itens sem `product_category_name`. A categoria não veio no cadastro do produto.",
            f"- {len(untranslated)} itens nas categorias {', '.join(untranslated_names)}, que não existem em `product_category_name_translation`.",
            "- O review é texto do pedido. A nota em si está íntegra (1 a 5). O problema de categoria afeta a visão comercial e as features de LLM, não o score.",
            "",
            "## O que a zona trusted corrigiu",
            "",
            "- 1.603 categorias vazias viraram `sem_categoria` / `uncategorized`. Nenhuma linha foi descartada.",
            "- 9 itens `pc_gamer` receberam `gaming_pc`.",
            "- 15 itens `portateis_cozinha_e_preparadores_de_alimentos` receberam `portable_kitchen_and_food_preparers`.",
            "- Preço, frete, grão e datas já passavam e foram copiados sem mudança.",
            "",
            "O arquivo corrigido, e o que sobe na Dadosfera, é `data/trusted/fact_order_items.csv`, gerado por `scripts/build_trusted_fact.py`. O arquivo em `data/processed/` não foi alterado.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"relatorio={REPORT}")
    for row in suite.rows:
        label = "PASS" if row["ok"] else "FAIL"
        print(f"{label} {row['name']} — {row['detail']}")
    if suite.unexpected:
        print("inesperado:")
        for name in suite.unexpected:
            print(f"- {name}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
