import streamlit as st

from utils.data_loader import get_retail_data
from utils.ui import apply_global_styles, top_navigation


st.set_page_config(
    page_title="Inicio | Analitica Retail",
    page_icon="📊",
    layout="wide",
)
apply_global_styles()

st.sidebar.title("Carga de datos")
df = get_retail_data(required=False)
top_navigation("Inicio")

st.title("Analitica Retail e Inteligencia de Clientes")
st.caption("Aplicacion web para explorar ventas, clientes, productos y recomendaciones comerciales.")

st.markdown(
    """
    Esta plataforma permite analizar el archivo de **Ventas Online** desde una perspectiva de
    inteligencia comercial. El flujo incluye limpieza automatica de datos, KPIs ejecutivos,
    analisis de ventas, segmentacion RFM, revision de productos y recomendaciones por reglas
    de asociacion.
    """
)

if df is None:
    st.info("Aun no hay un archivo cargado. Puedes cargarlo aqui o desde la barra lateral.")
    home_file = st.file_uploader(
        "Cargar archivo CSV o Excel",
        type=["csv", "xlsx", "xls"],
        key="home_dataset_uploader",
    )
    if home_file is not None:
        st.session_state.retail_file_name = home_file.name
        st.session_state.retail_file_bytes = home_file.getvalue()
        st.rerun()
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros limpios", f"{len(df):,}")
    col2.metric("Clientes", f"{df['Customer ID'].nunique():,}")
    col3.metric("Paises", f"{df['Country'].nunique():,}")

    st.success("Archivo cargado correctamente. Selecciona una pestana superior para continuar.")
