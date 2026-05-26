from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd
import streamlit as st

from utils.preprocessing import DatasetFormatError, clean_retail_data, normalize_columns


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
DEFAULT_DATA_PATH = Path("data") / "online_retail_II.csv"
FILE_NAME_STATE_KEY = "retail_file_name"
FILE_BYTES_STATE_KEY = "retail_file_bytes"
USE_LOCAL_STATE_KEY = "retail_use_local_file"
USE_LOCAL_WIDGET_KEY = "retail_use_local_file_widget"
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


def sync_local_file_choice() -> None:
    """Persist the local-file checkbox outside the widget state."""
    st.session_state[USE_LOCAL_STATE_KEY] = st.session_state[USE_LOCAL_WIDGET_KEY]


def get_retail_data(required: bool = True) -> pd.DataFrame | None:
    """Render the sidebar uploader and return a clean retail dataframe."""
    st.sidebar.subheader("Archivo")

    if FILE_NAME_STATE_KEY not in st.session_state:
        st.session_state[FILE_NAME_STATE_KEY] = None
    if FILE_BYTES_STATE_KEY not in st.session_state:
        st.session_state[FILE_BYTES_STATE_KEY] = None
    if USE_LOCAL_STATE_KEY not in st.session_state:
        st.session_state[USE_LOCAL_STATE_KEY] = False
    st.session_state[USE_LOCAL_WIDGET_KEY] = st.session_state[USE_LOCAL_STATE_KEY]

    # Guarda el archivo en session_state para que las paginas multipagina compartan la misma carga.
    uploaded_file: BinaryIO | None = st.sidebar.file_uploader(
        "Archivo Online Retail II",
        type=["csv", "xlsx", "xls"],
        help="Carga el archivo descargado desde Kaggle o un dataset compatible.",
        key="sidebar_dataset_uploader",
    )

    if uploaded_file is not None:
        st.session_state[FILE_NAME_STATE_KEY] = uploaded_file.name
        st.session_state[FILE_BYTES_STATE_KEY] = uploaded_file.getvalue()
        st.session_state[USE_LOCAL_STATE_KEY] = False
        st.session_state[USE_LOCAL_WIDGET_KEY] = False

    if st.session_state[FILE_NAME_STATE_KEY]:
        st.sidebar.success(f"Archivo activo: {st.session_state[FILE_NAME_STATE_KEY]}")
        if st.sidebar.button("Quitar archivo cargado"):
            st.session_state[FILE_NAME_STATE_KEY] = None
            st.session_state[FILE_BYTES_STATE_KEY] = None
            st.rerun()

    st.sidebar.checkbox(
        "Usar data/online_retail_II.csv",
        help="Disponible solo si el archivo existe dentro del proyecto.",
        key=USE_LOCAL_WIDGET_KEY,
        on_change=sync_local_file_choice,
    )
    use_local = st.session_state[USE_LOCAL_STATE_KEY]

    try:
        if st.session_state[FILE_NAME_STATE_KEY] and st.session_state[FILE_BYTES_STATE_KEY]:
            file_name = st.session_state[FILE_NAME_STATE_KEY]
            file_bytes = st.session_state[FILE_BYTES_STATE_KEY]
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
        st.session_state[FILE_NAME_STATE_KEY] = None
        st.session_state[FILE_BYTES_STATE_KEY] = None
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
