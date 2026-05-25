from __future__ import annotations

import pandas as pd
import streamlit as st


def apply_global_styles() -> None:
    """Apply lightweight CSS for a cleaner dashboard appearance."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 3.25rem;
            padding-bottom: 2rem;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid #e5e7eb;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #111827;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            color: #111827;
            padding: 0.85rem 1rem;
        }

        div[data-testid="stMetricLabel"] p {
            color: #4b5563;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #111827;
        }

        div[data-testid="stMetricDelta"] {
            color: #374151;
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p,
        div[data-testid="stMetric"] div {
            color: inherit;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #d1d5db;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stButton"] > button {
            border-radius: 8px;
            font-weight: 600;
            min-height: 2.55rem;
            width: 100%;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: #2563eb;
            color: #1d4ed8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def top_navigation(current_page: str = "Inicio") -> None:
    """Render a horizontal Spanish navigation bar."""
    st.markdown('<div style="height: 0.35rem;"></div>', unsafe_allow_html=True)

    nav_items = {
        "Inicio": "app.py",
        "KPIs": "pages/1_KPIs.py",
        "Ventas": "pages/2_Sales_Analysis.py",
        "Clientes": "pages/3_Customer_Segmentation.py",
        "Productos": "pages/4_Product_Insights.py",
        "Recomendaciones": "pages/5_Recommendations.py",
    }

    columns = st.columns(len(nav_items), gap="small")
    for column, (label, page_path) in zip(columns, nav_items.items()):
        button_label = f"● {label}" if label == current_page else label
        with column:
            if st.button(button_label, key=f"nav_{label}", use_container_width=True):
                if label != current_page:
                    st.switch_page(page_path)

    st.divider()


def chart_box(title: str | None = None):
    """Create a bordered visual container for charts."""
    container = st.container(border=True)
    if title:
        container.subheader(title)
    return container


def limited_dataframe(
    df: pd.DataFrame,
    label: str,
    default_rows: int = 20,
    max_rows: int = 200,
    hide_index: bool = True,
    formats: dict[str, str] | None = None,
) -> None:
    """Render a dataframe with a row selector to avoid oversized tables."""
    if df.empty:
        st.info("No hay datos para mostrar.")
        return

    if len(df) <= 5:
        display_df = df
    else:
        row_count = st.slider(
            label,
            min_value=5,
            max_value=min(max_rows, len(df)),
            value=min(default_rows, len(df)),
            step=5,
        )
        display_df = df.head(row_count)

    if formats:
        st.dataframe(
            display_df.style.format(formats),
            hide_index=hide_index,
            use_container_width=True,
        )
        return

    st.dataframe(display_df, hide_index=hide_index, use_container_width=True)
