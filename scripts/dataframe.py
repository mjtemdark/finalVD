import math

import pandas as pd
import streamlit as st
from pandas import DataFrame

df: DataFrame = st.session_state.data

st.set_page_config(layout="wide")

def tabla_paginada(
    df: DataFrame,
    key: str,
    page_size: int = 10,
) -> None:
    total_paginas = max(1, math.ceil(len(df) / page_size))

    page = st.pagination(
        num_pages=total_paginas,
        key=f"{key}_pagination",
        max_visible_pages=5,
    )

    inicio = (page - 1) * page_size
    fin = inicio + page_size

    st.dataframe(
        df.iloc[inicio:fin],
        width='stretch',
        hide_index=True,
    )

st.header("Resumen del Dataset")


if df is None or df.empty:
    st.warning("No hay datos disponibles para mostrar.")
    st.stop()

# Indicadores principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Filas", f"{df.shape[0]:,}")

with col2:
    st.metric("Columnas", f"{df.shape[1]:,}")

with col3:
    st.metric("Celdas vacías", f"{df.isna().sum().sum():,}")

with col4:
    duplicados = df.duplicated().sum()
    st.metric("Filas duplicadas", f"{duplicados:,}")

st.divider()

# Previsualización
st.subheader("Previsualización de los datos")
tabla_paginada(df, key="data", page_size=30)

# Información general
st.subheader("Información de las columnas")
resumen = pd.DataFrame({
    "Columna": df.columns,
    "Tipo de dato": df.dtypes.astype(str).values,
    "Valores no nulos": df.notna().sum().values,
    "Valores nulos": df.isna().sum().values,
    "% nulos": (df.isna().mean().values * 100).round(2),
    "Valores únicos": df.nunique().values,
})
tabla_paginada(resumen, key="resumen", page_size=20)

# Estadísticas descriptivas
st.subheader("Estadísticas descriptivas")
estadisticas = (
    df.describe(include="all")
    .T
    .rename_axis("Columna")
    .reset_index()
)
tabla_paginada(estadisticas, key="describe")