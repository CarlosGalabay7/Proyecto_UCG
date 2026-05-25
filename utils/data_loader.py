from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd
import streamlit as st

from utils.preprocessing import DatasetFormatError, clean_retail_data, normalize_columns


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
DEFAULT_DATA_PATH = Path("data") / "online_retail_II.csv"
EXPECTED_COLUMNS_MESSAGE = (
    "El archivo cargado no tiene el formato necesario para generar los dashboards. "
    "Carga un archivo Online Retail II con estas columnas: Invoice o InvoiceNo, "
    "StockCode, Description, Quantity, InvoiceDate, Price o UnitPrice, "
    "Customer ID o CustomerID y Country."
)


@st.cache_data(show_spinner="Cargando dataset...")
def load_uploaded_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    """Load a CSV or Excel file uploaded from Streamlit."""
    extension = Path(file_name).suffix.lower()

    if extension == ".csv":
        return pd.read_csv(BytesIO(file_bytes), encoding_errors="ignore")

    if extension in {".xlsx", ".xls"}:
        return pd.read_excel(BytesIO(file_bytes))

    raise ValueError("Formato no soportado. Carga un archivo CSV, XLSX o XLS.")


@st.cache_data(show_spinner="Cargando archivo local...")
def load_local_data(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the default local dataset when it exists."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo local: {file_path}")

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path, encoding_errors="ignore")

    if file_path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)

    raise ValueError("Formato local no soportado. Usa CSV, XLSX o XLS.")


@st.cache_data(show_spinner="Limpiando dataset...")
def prepare_retail_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and clean the retail dataset."""
    # Mantiene separada la lectura del archivo de la preparacion de datos del negocio.
    normalized = normalize_columns(raw_df)
    return clean_retail_data(normalized)


def get_retail_data(required: bool = True) -> pd.DataFrame | None:
    """Render the sidebar uploader and return a clean retail dataframe."""
    st.sidebar.subheader("Archivo")

    if "retail_file_name" not in st.session_state:
        st.session_state.retail_file_name = None
    if "retail_file_bytes" not in st.session_state:
        st.session_state.retail_file_bytes = None

    # Guarda el archivo en session_state para que las paginas multipagina compartan la misma carga.
    uploaded_file: BinaryIO | None = st.sidebar.file_uploader(
        "Archivo Online Retail II",
        type=["csv", "xlsx", "xls"],
        help="Carga el archivo descargado desde Kaggle o un dataset compatible.",
        key="sidebar_dataset_uploader",
    )

    if uploaded_file is not None:
        st.session_state.retail_file_name = uploaded_file.name
        st.session_state.retail_file_bytes = uploaded_file.getvalue()

    if st.session_state.retail_file_name:
        st.sidebar.success(f"Archivo activo: {st.session_state.retail_file_name}")
        if st.sidebar.button("Quitar archivo cargado"):
            st.session_state.retail_file_name = None
            st.session_state.retail_file_bytes = None
            st.rerun()

    use_local = st.sidebar.checkbox(
        "Usar data/online_retail_II.csv",
        value=False,
        help="Disponible solo si el archivo existe dentro del proyecto.",
    )

    try:
        if st.session_state.retail_file_name and st.session_state.retail_file_bytes:
            file_name = st.session_state.retail_file_name
            file_bytes = st.session_state.retail_file_bytes
            extension = Path(file_name).suffix.lower()

            # Valida la extension antes de intentar leer bytes como CSV o Excel.
            if extension not in SUPPORTED_EXTENSIONS:
                st.sidebar.error("Formato no soportado. Usa CSV, XLSX o XLS.")
                if required:
                    st.stop()
                return None

            raw_df = load_uploaded_data(file_name, file_bytes)
            return prepare_retail_data(raw_df)

        if use_local:
            raw_df = load_local_data()
            return prepare_retail_data(raw_df)

    except DatasetFormatError as exc:
        st.error(EXPECTED_COLUMNS_MESSAGE)
        st.warning(str(exc))
        st.session_state.retail_file_name = None
        st.session_state.retail_file_bytes = None
        if required:
            st.stop()
        return None
    except Exception as exc:
        st.error(f"No se pudo cargar el archivo: {exc}")
        if required:
            st.stop()
        return None

    if required:
        st.info("Carga un archivo CSV o Excel desde la barra lateral para continuar.")
        st.stop()

    return None
