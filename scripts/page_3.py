import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

st.set_page_config(layout="wide")

# Onbtencion de datos cargados
df: DataFrame = st.session_state.data

st.subheader("Llegadas de turistas internacionales al Perú")

# Preparacion de datos
datos = (
    df.groupby("ANIO", as_index=False)["NUMERO_VISITANTES"]
      .sum()
      .sort_values("ANIO")
)

# Convercion a millones para que el gráfico sea más legible
datos["VISITANTES_MILLONES"] = datos["NUMERO_VISITANTES"] / 1_000_000

# Grafico temporal
fig = px.line(
    datos,
    x="ANIO",
    y="VISITANTES_MILLONES",
    markers=True,
    labels={
        "ANIO": "Año",
        "VISITANTES_MILLONES": "Llegadas de turistas (millones)"
    }
)

# Etiquetas
fig.update_traces(
    text=[f"{x:.2f} M" for x in datos["VISITANTES_MILLONES"]],
    textposition="top center",
    line=dict(width=3),
    marker=dict(size=9)
)

# Resaltamos los puntos mínimos y máximos
fila_min = datos.loc[datos["VISITANTES_MILLONES"].idxmin()]
fila_max = datos.loc[datos["VISITANTES_MILLONES"].idxmax()]

fig.add_trace(
    go.Scatter(
        x=[fila_min["ANIO"]],
        y=[fila_min["VISITANTES_MILLONES"]],
        mode="markers",
        marker=dict(size=14),
        name="Mínimo",
        hovertemplate=(
            f"Año: {int(fila_min['ANIO'])}<br>"
            f"Turistas: {fila_min['VISITANTES_MILLONES']:.2f} M"
            "<extra></extra>"
        )
    )
)

fig.add_trace(
    go.Scatter(
        x=[fila_max["ANIO"]],
        y=[fila_max["VISITANTES_MILLONES"]],
        mode="markers",
        marker=dict(size=14),
        name="Máximo",
        hovertemplate=(
            f"Año: {int(fila_max['ANIO'])}<br>"
            f"Turistas: {fila_max['VISITANTES_MILLONES']:.2f} M"
            "<extra></extra>"
        )
    )
)

# Anotación de la caída en el año 2022
if 2020 in datos["ANIO"].values:
    valor_2020 = datos.loc[
        datos["ANIO"] == 2020,
        "VISITANTES_MILLONES"
    ].iloc[0]

    fig.add_annotation(
        x=2020,
        y=valor_2020,
        text="Fuerte caída en 2020",
        showarrow=True,
        arrowhead=2,
        ax=70,
        ay=-40
    )

# Estilos del gráfico
fig.update_layout(
    title={
        "text": "Evolución de las llegadas de turistas internacionales al Perú",
        "x": 0.02,
        "xanchor": "left"
    },
    xaxis=dict(
        dtick=1
    ),
    yaxis=dict(
        rangemode="tozero"
    ),
    hovermode="x unified",
    height=600,
    margin=dict(l=40, r=40, t=80, b=40),
    legend_title_text=""
)

st.plotly_chart(fig, width="stretch")

st.caption("Fuente: MINCETUR")