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
st.subheader("Turismo Receptivo en el Perú")
st.text("Dataset publicado por el Ministerio de Comercio Exterior y Turismo (MINCETUR)")

st.text("Fuente: Plataforma de Datos Abiertos")
st.link_button(
    "Ver",
    "https://www.datosabiertos.gob.pe/dataset/turismo-receptivo-en-el-per%C3%BA-ministerio-de-comercio-exterior-y-turismo-mincetur",
    icon=":material/open_in_new:",
)
st.subheader("Diccionario de Datos")

COLUMNAS = [
    "Atributo",
    "Descripción",
    "Tipo de dato",
    "Tamaño",
    "Recurso relacionado",
    "Información adicional",
]

FILAS = [
    ("FECHA_CORTE", "Fecha de corte de información.", "Numérico", 8, "", ""),
    ("ANIO", "Código que identifica al año de referencia.", "Numérico", 4, "", ""),
    ("ID_MES", "Código que identifica el mes de referencia.", "Numérico", 2, "",
     "ID del mes, donde: 1: enero …. 12: diciembre."),
    ("MES", "Nombre del mes.", "Texto", 10, "", ""),
    ("ID_PAIS", "Código del país de residencia del visitante internacional.", "Numérico", 3, "", ""),
    ("PAIS", "Nombre del país de residencia del visitante internacional.", "Texto", 25, "", ""),
    ("ID_CONTINENTE", "Código que identifica el continente de residencia.", "Numérico", 2, "", ""),
    ("CONTINENTE", "Nombre del continente de residencia.", "Texto", 17, "", ""),
    ("ID_OCM", "Código que identifica a la Oficina de Control Migratorio (OCM).", "Numérico", 1, "", ""),
    ("OCM", "Nombre de la Oficina de Control Migratorio (OCM).", "Texto", 37, "", ""),
    ("DEPARTAMENTO_OCM",
     "Nombre del departamento del Perú donde se ubica la Oficina de Control Migratorio (OCM).",
     "Texto", 13, "",
     "La región corresponde a la división territorial de mayor nivel en Perú."),
    ("NUMERO_VISITANTES", "Número de visitantes internacionales registrados.", "Numérico", 5, "", ""),
    ("BLOQUE", "Nombre del bloque de integración.", "Texto", 40, "",
     "Identifica el bloque de integración al que pertenece el país de residencia, "
     "considerando APEC, Comunidad Andina, Alianza del Pacífico y OCEX. Cuando el país "
     "no pertenece a ninguno de los bloques considerados, el campo se mantiene sin valor."),
    ("TIPO_VISITANTE",
     "Tipo de visitante internacional según clasificación estadística (turista o excursionista).",
     "Texto", 14, "", "Categorizado por Turista y Excursionista."),
]


dfdict = pd.DataFrame(FILAS, columns=COLUMNAS)

st.table(dfdict)
st.subheader("Resumen del Dataset")

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