import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from helpers.colors import paleta_turismo

st.set_page_config(layout="wide")

# Onbtencion de datos cargados
df: DataFrame = st.session_state.data

st.subheader("Llegadas de turistas internacionales al Perú")

# Colores definidos por el equipo
color_principal = paleta_turismo[1]
color_minimo = paleta_turismo[2]
color_maximo = paleta_turismo[0]

# Preparacion de datos
datos = (
    df[
        (df["ANIO"].between(2019, 2025)) &
        (df["ANIO"] != 2020)
    ]
    .groupby("ANIO", as_index=False)["NUMERO_VISITANTES"]
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
    color_discrete_sequence=[color_principal],
    labels={
        "ANIO": "Año",
        "VISITANTES_MILLONES": "Llegadas de turistas (millones)"
    }
)

# Estilo de la línea y sus puntos
fig.update_traces(
    line=dict(width=3),
    marker=dict(size=9)
)

# Identificamos el mínimo y máximo
fila_min = datos.loc[datos["VISITANTES_MILLONES"].idxmin()]
fila_max = datos.loc[datos["VISITANTES_MILLONES"].idxmax()]

# Resaltamos el mínimo
fig.add_trace(
    go.Scatter(
        x=[fila_min["ANIO"]],
        y=[fila_min["VISITANTES_MILLONES"]],
        mode="markers+text",
        text=[f"Mínimo: {fila_min['VISITANTES_MILLONES']:.2f} M"],
        textposition="bottom center",
        textfont=dict(
            color=color_minimo,
            size=14
        ),
        marker=dict(
            size=14,
            color=color_minimo
        ),
        name="Mínimo"
    )
)

# Resaltamos el máximo
fig.add_trace(
    go.Scatter(
        x=[fila_max["ANIO"]],
        y=[fila_max["VISITANTES_MILLONES"]],
        mode="markers+text",
        text=[f"Máximo: {fila_max['VISITANTES_MILLONES']:.2f} M"],
        textposition="top center",
        textfont=dict(
            color=color_maximo,
            size=14
        ),
        marker=dict(
            size=14,
            color=color_maximo
        ),
        name="Máximo"
    )
)

# Estilos del gráfico
fig.update_layout(
    title={
        "text": "Evolución de las llegadas de turistas internacionales al Perú",
        "x": 0.02,
        "xanchor": "left"
    },
    xaxis=dict(
        dtick=1,
        tickformat="d"
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