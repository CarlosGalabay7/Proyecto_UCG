from __future__ import annotations

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def build_basket(df: pd.DataFrame, max_invoices: int = 5000) -> pd.DataFrame:
    """Create an invoice-product matrix for market basket analysis."""
    basket_source = df[["Invoice", "Description", "Quantity"]].copy()

    # Limita el volumen para que Apriori siga siendo viable en Streamlit.
    if basket_source["Invoice"].nunique() > max_invoices:
        invoice_sample = basket_source["Invoice"].drop_duplicates().head(max_invoices)
        basket_source = basket_source[basket_source["Invoice"].isin(invoice_sample)]

    # Convierte ventas por factura/producto en matriz booleana: producto comprado o no comprado.
    basket = (
        basket_source.groupby(["Invoice", "Description"])["Quantity"]
        .sum()
        .unstack()
        .fillna(0)
    )
    return basket.gt(0)


def generate_association_rules(
    df: pd.DataFrame,
    min_support: float = 0.02,
    min_confidence: float = 0.3,
) -> pd.DataFrame:
    """Generate Apriori frequent itemsets and association rules."""
    basket = build_basket(df)

    # Primero identifica combinaciones frecuentes y luego deriva reglas de recomendacion.
    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        return pd.DataFrame()

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame()

    # Prioriza reglas con mayor lift y confianza para mostrar oportunidades mas accionables.
    rules = rules.sort_values(["lift", "confidence"], ascending=False).copy()
    rules["antecedents"] = rules["antecedents"].apply(lambda items: ", ".join(sorted(items)))
    rules["consequents"] = rules["consequents"].apply(lambda items: ", ".join(sorted(items)))
    return rules[["antecedents", "consequents", "support", "confidence", "lift"]]
