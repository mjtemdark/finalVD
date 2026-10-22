import pandas as pd
import streamlit as st

datapath="./data/Llegada_turistas_internacionales.xlsx"

st.header("Turismo internacional en el Perú: una recuperación que todavía no alcanza los niveles prepandemia")
@st.cache_data(show_spinner="Descargando y procesando datos")
def cargar_datos() -> pd.DataFrame:
    return pd.read_excel(
        datapath,
    )


if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

pg = st.navigation([
    st.Page("scripts/dataframe.py", title="Resumen de Datos"),
    st.Page("scripts/page_1.py", title="Gráfico 1 Mapa Coroplético"),
    st.Page("scripts/page_2.py", title="Grafico 2"),
    st.Page("scripts/page_3.py", title="Grafico 3"),
])
pg.run()