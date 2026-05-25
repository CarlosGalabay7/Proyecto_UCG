from __future__ import annotations

import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    """Calculate the main dashboard KPIs."""
    # Resume el dataset limpio en indicadores ejecutivos reutilizables en la pagina de KPIs.
    total_sales = float(df["Revenue"].sum())
    total_orders = int(df["Invoice"].nunique())
    total_customers = int(df["Customer ID"].nunique())
    total_products_sold = int(df["Quantity"].sum())
    avg_ticket = total_sales / total_orders if total_orders else 0

    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "avg_ticket": avg_ticket,
        "total_products_sold": total_products_sold,
    }
