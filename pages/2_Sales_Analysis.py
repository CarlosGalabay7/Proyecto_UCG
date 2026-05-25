import streamlit as st

from utils.charts import (
    monthly_sales_trend,
    revenue_distribution,
    sales_over_time,
    top_countries_by_revenue,
    top_products_by_quantity,
)
from utils.data_loader import get_retail_data
from utils.ui import apply_global_styles, chart_box, limited_dataframe, top_navigation


st.set_page_config(page_title="Ventas | Analitica Retail", page_icon="📈", layout="wide")
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data()
top_navigation("Ventas")

st.title("Analisis de ventas")
st.caption("Evolucion de ingresos, productos, paises y patrones de facturacion.")

country_options = sorted(df["Country"].dropna().unique())
selected_countries = st.multiselect(
    "Filtrar por pais",
    options=country_options,
    default=country_options[: min(5, len(country_options))],
)

filtered_df = df[df["Country"].isin(selected_countries)] if selected_countries else df
top_n = st.slider("Cantidad de elementos en rankings", min_value=5, max_value=30, value=15)

tab_graficos, tab_datos = st.tabs(["Visualizaciones", "Muestra de datos"])

with tab_graficos:
    with chart_box():
        st.plotly_chart(sales_over_time(filtered_df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with chart_box():
            st.plotly_chart(monthly_sales_trend(filtered_df), use_container_width=True)
    with col2:
        with chart_box():
            st.plotly_chart(revenue_distribution(filtered_df), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        with chart_box():
            st.plotly_chart(top_products_by_quantity(filtered_df, top_n=top_n), use_container_width=True)
    with col4:
        with chart_box():
            st.plotly_chart(top_countries_by_revenue(filtered_df, top_n=top_n), use_container_width=True)

with tab_datos:
    muestra_ventas = filtered_df.rename(
        columns={
            "Invoice": "Factura",
            "StockCode": "Codigo de producto",
            "Description": "Producto",
            "Quantity": "Cantidad",
            "InvoiceDate": "Fecha de factura",
            "Price": "Precio",
            "Customer ID": "Cliente",
            "Country": "Pais",
            "Revenue": "Ingresos",
            "InvoiceMonth": "Mes de factura",
        }
    )
    limited_dataframe(muestra_ventas, "Filas de ventas a mostrar", default_rows=25, max_rows=200)
