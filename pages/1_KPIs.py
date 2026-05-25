import streamlit as st

from utils.data_loader import get_retail_data
from utils.metrics import calculate_kpis
from utils.ui import apply_global_styles, limited_dataframe, top_navigation


st.set_page_config(page_title="KPIs | Analitica Retail", page_icon="📊", layout="wide")
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data()
top_navigation("KPIs")

st.title("KPIs generales")
st.caption("Resumen ejecutivo del desempeño comercial del retail.")

kpis = calculate_kpis(df)

tab_resumen, tab_muestra = st.tabs(["Resumen", "Muestra de datos"])

with tab_resumen:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 Ventas totales", f"${kpis['total_sales']:,.2f}")
    col2.metric("🧾 Ordenes", f"{kpis['total_orders']:,}")
    col3.metric("👥 Clientes", f"{kpis['total_customers']:,}")
    col4.metric("🎟️ Ticket promedio", f"${kpis['avg_ticket']:,.2f}")
    col5.metric("📦 Productos vendidos", f"{kpis['total_products_sold']:,}")

    st.divider()

    st.subheader("Cobertura del archivo")
    coverage_col1, coverage_col2, coverage_col3, coverage_col4 = st.columns(4)
    coverage_col1.metric("📅 Fecha inicial", df["InvoiceDate"].min().strftime("%Y-%m-%d"))
    coverage_col2.metric("📅 Fecha final", df["InvoiceDate"].max().strftime("%Y-%m-%d"))
    coverage_col3.metric("🌎 Paises", f"{df['Country'].nunique():,}")
    coverage_col4.metric("🏷️ Productos unicos", f"{df['StockCode'].nunique():,}")

with tab_muestra:
    preview = df.rename(
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
    limited_dataframe(preview, "Filas a mostrar en la muestra", default_rows=25, max_rows=100)
