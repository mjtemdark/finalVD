import numpy as np
import plotly.express as px
import streamlit as st
from pandas import DataFrame

st.set_page_config(layout="wide")
from helpers.paises_iso import agregar_iso3


df: DataFrame = st.session_state.data
df=agregar_iso3(df,"PAIS")

st.dataframe(df)

##FILTROS
st.sidebar.header("Filtros")
anios = sorted(int(a) for a in df["ANIO"].dropna().unique())
anio = st.sidebar.select_slider("Año", options=["Todos"] + anios, value="Todos")

##CONTROLES DE APARIENCIA
st.sidebar.header("Apariencia")
escala_log = st.sidebar.checkbox("Escala logarítmica (recomendada)", value=True)
proyeccion = st.sidebar.selectbox("Proyección", ["natural earth", "equirectangular", "orthographic"])
alto = st.sidebar.slider("Alto del mapa (px)", 500, 1000, 720, step=20)

## FILTRO DE AÑO
filtrado = df if anio == "Todos" else df[df["ANIO"] == anio]

datos = (
    filtrado.dropna(subset=["ISO3"])
    .groupby(["ISO3", "PAIS"], as_index=False)["NUMERO_VISITANTES"].sum()
)

datos = datos[datos["NUMERO_VISITANTES"] > 0]

if datos.empty:
    st.warning("No hay datos para el año seleccionado.")
    st.stop()

# AJUSTAR ESCALA
datos["valor"] = np.log10(datos["NUMERO_VISITANTES"]) if escala_log else datos["NUMERO_VISITANTES"]

# ------------------------------------------------------------------
# INDICADORES
# ------------------------------------------------------------------
top = datos.sort_values("NUMERO_VISITANTES", ascending=False).iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Total de visitantes", f"{datos['NUMERO_VISITANTES'].sum():,.0f}")
c2.metric("Países de origen", f"{datos['ISO3'].nunique()}")
c3.metric("País con más visitantes", top["PAIS"], f"{top['NUMERO_VISITANTES']:,.0f}", delta_color="off")

# ------------------------------------------------------------------
# MAPA
# ------------------------------------------------------------------
fig = px.choropleth(
    datos,
    locations="ISO3",
    locationmode="ISO-3",
    color="valor",
    hover_name="PAIS",
    hover_data={"ISO3": False, "valor": False, "NUMERO_VISITANTES": ":,.0f"},
    labels={"NUMERO_VISITANTES": "Visitantes"},
    color_continuous_scale="YlOrRd",
    projection=proyeccion,
)

# BARRA DE COLOR CON VALORES REALES
colorbar = dict(title="Visitantes", len=0.7, thickness=16, outlinewidth=0)
if escala_log:
    lo, hi = int(np.floor(datos["valor"].min())), int(np.ceil(datos["valor"].max()))
    tickvals = list(range(lo, hi + 1))
    colorbar["tickvals"] = tickvals
    colorbar["ticktext"] = [f"{10 ** t:,.0f}" for t in tickvals]
fig.update_coloraxes(colorbar=colorbar)

# ESTILO DEL MAPA
fig.update_geos(
    showframe=False,
    showcoastlines=True,
    coastlinecolor="#9aa5b1",
    coastlinewidth=0.5,
    showland=True,
    landcolor="#eceff3",
    showocean=True,
    oceancolor="#dcebf7",
    showcountries=True,
    countrycolor="#ffffff",
    showlakes=False,
)
fig.update_traces(marker_line_color="#ffffff", marker_line_width=0.4)
fig.update_layout(
    height=alto,
    margin=dict(l=0, r=0, t=10, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", size=13),
)

st.plotly_chart(fig, width='stretch')
