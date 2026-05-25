from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def build_rfm_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build customer-level Recency, Frequency and Monetary metrics."""
    # Usa el dia posterior a la ultima compra como referencia para medir recencia.
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby("Customer ID")
        .agg(
            Recency=("InvoiceDate", lambda dates: (reference_date - dates.max()).days),
            Frequency=("Invoice", "nunique"),
            Monetary=("Revenue", "sum"),
        )
        .reset_index()
    )
    return rfm


def segment_customers(rfm: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """Cluster customers with KMeans and assign business-friendly labels."""
    segmented = rfm.copy()

    # Evita pedir mas clusters que clientes disponibles.
    cluster_count = min(n_clusters, len(segmented))

    if cluster_count < 2:
        segmented["Cluster"] = 0
        segmented["Segment"] = "Sin segmento"
        return segmented

    features = segmented[["Recency", "Frequency", "Monetary"]]

    # Escala RFM para que KMeans no quede dominado por la variable monetaria.
    scaled_features = StandardScaler().fit_transform(features)

    model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    segmented["Cluster"] = model.fit_predict(scaled_features)

    profile = (
        segmented.groupby("Cluster")
        .agg(Recency=("Recency", "mean"), Frequency=("Frequency", "mean"), Monetary=("Monetary", "mean"))
        .reset_index()
    )
    profile["Score"] = (
        profile["Frequency"].rank(ascending=True)
        + profile["Monetary"].rank(ascending=True)
        + profile["Recency"].rank(ascending=False)
    )

    # Ordena clusters por valor comercial: mas frecuencia/monetario y menor recencia es mejor.
    ordered_clusters = profile.sort_values("Score", ascending=False)["Cluster"].tolist()
    label_pool = ["Premium", "Leales", "En riesgo", "Inactivos"]
    cluster_labels = {
        cluster: label_pool[index] if index < len(label_pool) else f"Segmento {index + 1}"
        for index, cluster in enumerate(ordered_clusters)
    }
    segmented["Segment"] = segmented["Cluster"].map(cluster_labels)
    return segmented
