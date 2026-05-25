import streamlit as st

from utils.data_loader import get_retail_data
from utils.market_basket import generate_association_rules
from utils.ui import apply_global_styles, limited_dataframe, top_navigation


st.set_page_config(page_title="Recomendaciones | Analitica Retail", page_icon="💡", layout="wide")
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data()
top_navigation("Recomendaciones")

st.title("Recomendaciones comerciales")
st.caption("Analisis de canasta de mercado con Apriori y reglas de asociacion.")

col1, col2 = st.columns(2)
with col1:
    min_support = st.slider("Soporte minimo", 0.005, 0.10, 0.02, 0.005)
with col2:
    min_confidence = st.slider("Confianza minima", 0.10, 0.90, 0.30, 0.05)

# Los parametros controlan cuan frecuentes y confiables deben ser las reglas sugeridas.
with st.spinner("Calculando reglas de asociacion..."):
    rules = generate_association_rules(
        df,
        min_support=min_support,
        min_confidence=min_confidence,
    )

if rules.empty:
    st.warning("No se encontraron reglas con los parametros actuales. Reduce soporte o confianza.")
    st.stop()

reglas_asociacion = rules.rename(
    columns={
        "antecedents": "Productos base",
        "consequents": "Productos recomendados",
        "support": "Soporte",
        "confidence": "Confianza",
        "lift": "Elevacion",
    }
)

tab_oportunidades, tab_reglas = st.tabs(["Oportunidades", "Reglas de asociacion"])

with tab_oportunidades:
    st.subheader("Mejores oportunidades")
    top_rules = reglas_asociacion.head(10)

    # Presenta las mejores reglas como acciones de venta cruzada faciles de interpretar.
    for _, row in top_rules.iterrows():
        st.markdown(
            f"- Si el cliente compra **{row['Productos base']}**, recomendar **{row['Productos recomendados']}** "
            f"(confianza: {row['Confianza']:.2f}, elevacion: {row['Elevacion']:.2f})."
        )

with tab_reglas:
    limited_dataframe(
        reglas_asociacion,
        "Filas de reglas a mostrar",
        default_rows=25,
        max_rows=100,
        formats={"Soporte": "{:.3f}", "Confianza": "{:.3f}", "Elevacion": "{:.3f}"},
    )
