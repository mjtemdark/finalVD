import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pandas import DataFrame

from helpers.colors import escala_mapa
from helpers.paises_iso import agregar_iso3

st.set_page_config(layout="wide")
df: DataFrame = st.session_state.data
df = agregar_iso3(df, "PAIS")

st.subheader("Evolución de la cantidad de turistas llegando al Perú desde 2019 hasta 2026")

## CONTROLES DE APARIENCIA
st.sidebar.header("Apariencia")
escala_log = st.sidebar.checkbox("Escala logarítmica", value=False)

proyecciones = {
    "Natural": "natural earth",
    "Equirectangular": "equirectangular",
    "Ortográfica": "orthographic"
}

proyeccion = st.sidebar.selectbox(
    "Proyección",
    options=proyecciones.keys()
)

proyeccion = proyecciones[proyeccion]

alto = st.sidebar.slider("Alto del mapa (px)", 500, 1000, 820, step=20)

## DATOS (por año, país)
datos = (
    df.dropna(subset=["ISO3"])
    .groupby(["ANIO", "ISO3", "PAIS"], as_index=False)["NUMERO_VISITANTES"].sum()
    .sort_values("ANIO")
)
datos = datos[datos["NUMERO_VISITANTES"] > 0]

if datos.empty:
    st.warning("No hay datos para mostrar.")
    st.stop()

# AJUSTAR ESCALA
datos["valor"] = np.log10(datos["NUMERO_VISITANTES"]) if escala_log else datos["NUMERO_VISITANTES"]

# ------------------------------------------------------------------
# ESTADÍSTICAS POR AÑO (se muestran dentro del gráfico)
# ------------------------------------------------------------------
stats = {}
for a, g in datos.groupby("ANIO"):
    top = g.loc[g["NUMERO_VISITANTES"].idxmax()]
    stats[str(a)] = (
        g["NUMERO_VISITANTES"].sum(),
        g["ISO3"].nunique(),
        top["PAIS"],
        top["NUMERO_VISITANTES"],
    )


def texto_stats(a):
    total, n, pais, v = stats[str(a)]
    return (
        f"<b>Total:</b> {total:,.0f}   |   "
        f"<b>Países de origen:</b> {n}   |   "
        f"<b>Principal país:</b> {pais} ({v:,.0f})"
    )


def anotacion(txt):
    return dict(
        text=txt, x=0.5, y=1.0, xref="paper", yref="paper",
        xanchor="center", yanchor="bottom", showarrow=False,
        font=dict(size=24),
    )


# ------------------------------------------------------------------
# MAPA ANIMADO
# ------------------------------------------------------------------

fig = px.choropleth(
    datos,
    locations="ISO3",
    locationmode="ISO-3",
    color="valor",
    animation_frame="ANIO",
    labels={"ANIO": "Año", "NUMERO_VISITANTES": "Numero de visitantes"},
    range_color=(datos["valor"].min(), datos["valor"].max()),  # misma escala en todos los años
    hover_name="PAIS",
    hover_data={"ISO3": False, "valor": False, "NUMERO_VISITANTES": ":,.0f"},
    color_continuous_scale=escala_mapa,
    projection=proyeccion,
)

# Velocidad de la animación (ms por año)
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800

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
    projection_rotation=dict(lon=0, lat=0, roll=0),
    showframe=False,
    showcoastlines=True,
    coastlinecolor="#000",
    coastlinewidth=0.5,
    showland=True,
    bgcolor="#0D1321",
    landcolor="#eceff3",
    showocean=True,
    oceancolor="#dcebf7",
    showcountries=True,
    countrycolor="#fff",
    showlakes=False,
)
fig.update_traces(marker_line_color="#000", marker_line_width=0.4)
fig.update_layout(
    height=alto,
    margin=dict(l=0, r=0, t=50, b=0),  # espacio arriba para las estadísticas
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", size=13),
)

# ESTADÍSTICAS DENTRO DEL GRÁFICO: estado inicial y un texto por cada año
fig.update_layout(annotations=[anotacion(texto_stats(datos["ANIO"].min()))])
for fr in fig.frames:
    fr.layout = go.Layout(annotations=[anotacion(texto_stats(fr.name))])

st.plotly_chart(fig, width="stretch")

st.subheader("Resumen")
st.write("""El gráfico animado nos muestra la evolución de la llegada de turistas pre y post pandemia
podemos visualizar que la mayoria de turistas provienen de Chile y EE.UU, se puede observar el cambio
en los años de pandemia donde no hubo afluencia.
 """)