import plotly.express as px
import streamlit as st

from utils.charts import rfm_cluster_scatter, style_figure
from utils.data_loader import get_retail_data
from utils.segmentation import build_rfm_table, segment_customers
from utils.ui import apply_global_styles, chart_box, limited_dataframe, top_navigation


st.set_page_config(page_title="Clientes | Analitica Retail", page_icon="👥", layout="wide")
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data()
top_navigation("Clientes")

st.title("Segmentacion de clientes")
st.caption("Analisis RFM con clustering KMeans para inteligencia de clientes.")

rfm = build_rfm_table(df)
n_clusters = st.slider("Numero de segmentos", min_value=2, max_value=6, value=4)
segmented = segment_customers(rfm, n_clusters=n_clusters)

segment_summary = (
    segmented.groupby("Segment", as_index=False)
    .agg(
        Clientes=("Customer ID", "count"),
        Recencia_promedio=("Recency", "mean"),
        Frecuencia_promedio=("Frequency", "mean"),
        Valor_monetario_total=("Monetary", "sum"),
    )
    .rename(
        columns={
            "Segment": "Segmento",
            "Recencia_promedio": "Recencia promedio",
            "Frecuencia_promedio": "Frecuencia promedio",
            "Valor_monetario_total": "Valor monetario total",
        }
    )
    .sort_values("Valor monetario total", ascending=False)
)

tab_graficos, tab_datos = st.tabs(["Visualizaciones", "Datos RFM"])

with tab_graficos:
    col1, col2 = st.columns([2, 1])
    with col1:
        with chart_box():
            st.plotly_chart(rfm_cluster_scatter(segmented), use_container_width=True)
    with col2:
        with chart_box():
            fig = px.pie(segment_summary, names="Segmento", values="Clientes", hole=0.45)
            fig.update_layout(title="Distribucion de clientes")
            st.plotly_chart(style_figure(fig), use_container_width=True)

    st.subheader("Resumen por segmento")
    st.dataframe(
        segment_summary.style.format(
            {
                "Recencia promedio": "{:.1f}",
                "Frecuencia promedio": "{:.1f}",
                "Valor monetario total": "${:,.2f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

with tab_datos:
    clientes_segmentados = segmented.rename(
        columns={
            "Customer ID": "Cliente",
            "Recency": "Recencia",
            "Frequency": "Frecuencia",
            "Monetary": "Valor monetario",
            "Cluster": "Cluster",
            "Segment": "Segmento",
        }
    ).sort_values("Valor monetario", ascending=False)
    limited_dataframe(
        clientes_segmentados,
        "Filas de clientes a mostrar",
        default_rows=25,
        max_rows=200,
        formats={"Valor monetario": "${:,.2f}"},
    )
