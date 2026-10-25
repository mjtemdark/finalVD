import pandas as pd
import streamlit as st

datapath = "./data/Llegada_turistas_internacionales.xlsx"

st.header("Turismo internacional en el Perú: una recuperación que todavía no alcanza los niveles prepandemia")


@st.cache_data(show_spinner="Descargando y procesando datos")
def cargar_datos() -> pd.DataFrame:
    return pd.read_excel(
        datapath,
    )


if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

pg = st.navigation([
    st.Page("scripts/dataframe.py", title="Resumen de Datos", icon=":material/dataset:"),
    st.Page("scripts/page_1.py", title="Mapa Coroplético Visitas por País", icon=":material/public:"),
    st.Page("scripts/page_3.py", title="Evolución anual de visitas", icon=":material/stacked_line_chart:"),
    st.Page("scripts/page_2.py", title="Grafico de Barras Top OCM", icon=":material/leaderboard:"),

])
pg.run()
