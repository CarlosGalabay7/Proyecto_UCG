import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import style_figure
from utils.data_loader import get_retail_data
from utils.ui import apply_global_styles, chart_box, limited_dataframe, top_navigation


st.set_page_config(page_title="Productos | Analitica Retail", page_icon="🛒", layout="wide")
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data()
top_navigation("Productos")

st.title("Analisis de productos")
st.caption("Productos lideres por volumen, ingresos y frecuencia de compra.")

resumen_productos = (
    df.groupby(["StockCode", "Description"], as_index=False)
    .agg(
        Cantidad=("Quantity", "sum"),
        Ingresos=("Revenue", "sum"),
        Ordenes=("Invoice", "nunique"),
        Clientes=("Customer ID", "nunique"),
    )
    .rename(columns={"StockCode": "Codigo de producto", "Description": "Producto"})
    .sort_values("Ingresos", ascending=False)
)

top_n = st.slider("Cantidad de productos a mostrar", min_value=5, max_value=30, value=15)
tab_graficos, tab_datos = st.tabs(["Visualizaciones", "Tabla de productos"])

with tab_graficos:
    col1, col2 = st.columns(2)
    with col1:
        with chart_box():
            top_quantity = resumen_productos.sort_values("Cantidad", ascending=False).head(top_n)
            fig = px.bar(top_quantity, x="Cantidad", y="Producto", orientation="h", title="Mas vendidos")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(style_figure(fig), use_container_width=True)

    with col2:
        with chart_box():
            top_revenue = resumen_productos.sort_values("Ingresos", ascending=False).head(top_n)
            fig = px.bar(top_revenue, x="Ingresos", y="Producto", orientation="h", title="Mayores ingresos")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(style_figure(fig), use_container_width=True)

    with chart_box():
        frequent_products = resumen_productos.sort_values("Ordenes", ascending=False).head(top_n)
        fig = px.bar(
            frequent_products,
            x="Ordenes",
            y="Producto",
            orientation="h",
            title="Productos comprados con mayor frecuencia",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_figure(fig), use_container_width=True)

    st.subheader("Insights comerciales")
    best_product = resumen_productos.iloc[0]
    most_sold = resumen_productos.sort_values("Cantidad", ascending=False).iloc[0]
    most_frequent = resumen_productos.sort_values("Ordenes", ascending=False).iloc[0]

    insights = pd.DataFrame(
        [
            {"Insight": "Producto con mayor ingreso", "Producto": best_product["Producto"], "Valor": f"${best_product['Ingresos']:,.2f}"},
            {"Insight": "Producto con mayor volumen", "Producto": most_sold["Producto"], "Valor": f"{most_sold['Cantidad']:,.0f} unidades"},
            {"Insight": "Producto mas frecuente", "Producto": most_frequent["Producto"], "Valor": f"{most_frequent['Ordenes']:,.0f} ordenes"},
        ]
    )
    st.dataframe(insights, hide_index=True, use_container_width=True)

with tab_datos:
    limited_dataframe(
        resumen_productos,
        "Filas de productos a mostrar",
        default_rows=25,
        max_rows=200,
        formats={
            "Cantidad": "{:,.0f}",
            "Ingresos": "${:,.2f}",
            "Ordenes": "{:,.0f}",
            "Clientes": "{:,.0f}",
        },
    )
