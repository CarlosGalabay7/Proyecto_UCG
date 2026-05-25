from __future__ import annotations

import pandas as pd


COLUMN_ALIASES = {
    "InvoiceNo": "Invoice",
    "Invoice": "Invoice",
    "StockCode": "StockCode",
    "Description": "Description",
    "Quantity": "Quantity",
    "InvoiceDate": "InvoiceDate",
    "UnitPrice": "Price",
    "Price": "Price",
    "CustomerID": "Customer ID",
    "Customer ID": "Customer ID",
    "Country": "Country",
}

REQUIRED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


class DatasetFormatError(ValueError):
    """Raised when the uploaded dataset does not match the expected schema."""


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize known Online Retail column variants to one shared schema."""
    normalized = df.copy()
    normalized.columns = [str(column).strip() for column in normalized.columns]
    normalized = normalized.rename(columns=COLUMN_ALIASES)

    missing_columns = set(REQUIRED_COLUMNS).difference(normalized.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise DatasetFormatError(f"Faltan columnas requeridas: {missing}")

    return normalized[REQUIRED_COLUMNS].copy()


def clean_retail_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Online Retail data and create the Revenue field."""
    cleaned = df.copy()

    cleaned["Invoice"] = cleaned["Invoice"].astype(str).str.strip()
    cleaned["StockCode"] = cleaned["StockCode"].astype(str).str.strip()
    cleaned["Description"] = cleaned["Description"].astype(str).str.strip()
    cleaned["Country"] = cleaned["Country"].astype(str).str.strip()
    cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], errors="coerce")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")

    cleaned = cleaned.dropna(subset=["Customer ID", "InvoiceDate", "Quantity", "Price"])
    cleaned = cleaned[~cleaned["Invoice"].str.upper().str.startswith("C")]
    cleaned = cleaned[cleaned["Quantity"] > 0]
    cleaned = cleaned[cleaned["Price"] > 0]
    cleaned = cleaned[cleaned["Description"].ne("")]

    cleaned["Customer ID"] = cleaned["Customer ID"].astype(float).astype(int).astype(str)
    cleaned["Revenue"] = cleaned["Quantity"] * cleaned["Price"]
    cleaned["InvoiceMonth"] = cleaned["InvoiceDate"].dt.to_period("M").astype(str)

    if cleaned.empty:
        raise DatasetFormatError(
            "El archivo no contiene registros validos despues de aplicar la limpieza."
        )

    return cleaned.sort_values("InvoiceDate").reset_index(drop=True)
