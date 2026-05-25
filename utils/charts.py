from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"]


def style_figure(fig: go.Figure) -> go.Figure:
    """Apply a consistent dashboard style to Plotly charts."""
    # Centraliza el estilo visual para que todos los graficos mantengan la misma apariencia.
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=35),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#111827"),
        title_font=dict(size=18, color="#111827"),
        legend=dict(font=dict(color="#111827"), title_font=dict(color="#111827")),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#d1d5db", font=dict(color="#111827")),
    )
    fig.update_xaxes(
        color="#111827",
        gridcolor="#e5e7eb",
        linecolor="#d1d5db",
        mirror=True,
        showline=True,
        tickfont=dict(color="#111827"),
        title_font=dict(color="#111827"),
        linewidth=1,
        zerolinecolor="#e5e7eb",
    )
    fig.update_yaxes(
        color="#111827",
        gridcolor="#e5e7eb",
        linecolor="#d1d5db",
        mirror=True,
        showline=True,
        tickfont=dict(color="#111827"),
        title_font=dict(color="#111827"),
        linewidth=1,
        zerolinecolor="#e5e7eb",
    )
    return fig


def sales_over_time(df: pd.DataFrame) -> go.Figure:
    # Agrega ingresos diarios para observar tendencia y estacionalidad de ventas.
    daily_sales = (
        df.groupby(df["InvoiceDate"].dt.date, as_index=False)["Revenue"]
        .sum()
        .rename(columns={"InvoiceDate": "Fecha", "Revenue": "Ingresos"})
    )
    fig = px.line(daily_sales, x="Fecha", y="Ingresos", template=TEMPLATE)
    fig.update_layout(title="Ventas en el tiempo", xaxis_title="Fecha", yaxis_title="Ingresos")
    return style_figure(fig)


def monthly_sales_trend(df: pd.DataFrame) -> go.Figure:
    monthly = df.groupby("InvoiceMonth", as_index=False)["Revenue"].sum()
    monthly = monthly.rename(columns={"InvoiceMonth": "Mes", "Revenue": "Ingresos"})
    fig = px.bar(monthly, x="Mes", y="Ingresos", template=TEMPLATE)
    fig.update_layout(title="Tendencia mensual", xaxis_title="Mes", yaxis_title="Ingresos")
    return style_figure(fig)


def top_products_by_quantity(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    products = (
        df.groupby("Description", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
        .head(top_n)
        .rename(columns={"Description": "Producto", "Quantity": "Unidades"})
    )
    fig = px.bar(
        products,
        x="Unidades",
        y="Producto",
        orientation="h",
        template=TEMPLATE,
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(title="Productos mas vendidos", yaxis={"categoryorder": "total ascending"})
    return style_figure(fig)


def top_countries_by_revenue(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    countries = (
        df.groupby("Country", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(top_n)
        .rename(columns={"Country": "Pais", "Revenue": "Ingresos"})
    )
    fig = px.bar(countries, x="Pais", y="Ingresos", template=TEMPLATE)
    fig.update_layout(title="Paises con mas ventas", xaxis_title="Pais", yaxis_title="Ingresos")
    return style_figure(fig)


def revenue_distribution(df: pd.DataFrame) -> go.Figure:
    # Calcula el valor total por factura para analizar la distribucion del ticket.
    order_revenue = df.groupby("Invoice", as_index=False)["Revenue"].sum()
    order_revenue = order_revenue.rename(columns={"Revenue": "Ingresos"})
    fig = px.histogram(order_revenue, x="Ingresos", nbins=60, template=TEMPLATE)
    fig.update_layout(title="Distribucion de ingresos por orden", yaxis_title="Ordenes")
    return style_figure(fig)


def rfm_cluster_scatter(rfm: pd.DataFrame) -> go.Figure:
    # Cruza frecuencia y valor monetario para visualizar la separacion de segmentos.
    fig = px.scatter(
        rfm,
        x="Frequency",
        y="Monetary",
        color="Segment",
        size="Monetary",
        hover_data=["Customer ID", "Recency"],
        labels={
            "Frequency": "Frecuencia",
            "Monetary": "Valor monetario",
            "Recency": "Recencia",
            "Customer ID": "Cliente",
            "Segment": "Segmento",
        },
        template=TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(title="Clusters de clientes", xaxis_title="Frecuencia", yaxis_title="Valor monetario")
    return style_figure(fig)
