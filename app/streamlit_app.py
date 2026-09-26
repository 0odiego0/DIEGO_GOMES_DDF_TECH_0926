"""Exploração da amostra de features geradas no item 5.

Rode na raiz do repositório:

    pip install -r app/requirements.txt
    streamlit run app/streamlit_app.py
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "refined" / "features_amostra.csv"


def tokens(text):
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in str(text))
    return {word for word in cleaned.split() if len(word) > 2}


def jaccard(left, right):
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


@st.cache_data
def load():
    frame = pd.read_csv(DATA)
    parsed = pd.json_normalize(frame["features_json"].map(json.loads))
    frame["price_tier"] = parsed["features.price_tier"]
    frame["use_case"] = parsed["features.use_case"]
    frame["texto"] = (frame["titulo"].fillna("") + " " + frame["descricao"].fillna("")).map(tokens)
    return frame


def main():
    st.set_page_config(page_title="Features Olist", layout="wide")
    st.title("Amostra de produtos com features de LLM")
    st.caption("147 produtos, dois por categoria. Título e descrição gerados no Colab.")

    frame = load()
    categories = ["Todas"] + sorted(frame["product_category_name"].dropna().unique())
    tiers = ["Todas"] + sorted(frame["price_tier"].dropna().unique())

    left, right = st.columns(2)
    category = left.selectbox("Categoria do catálogo", categories)
    tier = right.selectbox("Faixa de preço", tiers)

    view = frame
    if category != "Todas":
        view = view[view["product_category_name"] == category]
    if tier != "Todas":
        view = view[view["price_tier"] == tier]

    st.metric("Produtos na seleção", len(view))
    st.dataframe(
        view[["titulo", "product_category_name", "price", "price_tier", "use_case"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Produtos parecidos")
    chosen = st.selectbox("Produto de referência", view["titulo"].tolist())
    reference = view.loc[view["titulo"] == chosen].iloc[0]
    scores = frame.copy()
    scores["semelhanca"] = scores["texto"].map(lambda bag: jaccard(reference["texto"], bag))
    scores = scores[scores["product_id"] != reference["product_id"]].sort_values(
        "semelhanca", ascending=False
    )
    st.dataframe(
        scores[["titulo", "product_category_name", "price", "price_tier", "semelhanca"]].head(5),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
