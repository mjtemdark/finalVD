import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pandas import DataFrame

from helpers.colors import paleta_turismo

st.set_page_config(layout="wide")

COL_DEPTO, COL_ANIO, COL_VISITANTES = "DEPARTAMENTO_OCM", "ANIO", "NUMERO_VISITANTES"
COLORES = {
    "Top 1": paleta_turismo[2],
    "Top 2": paleta_turismo[1],
    "Top 3": paleta_turismo[3],
    "Otros": paleta_turismo[0],
}
NO_ESPECIFICADO = {"", "-", "--", "NA", "N/A", "NAN", "NULL", "NONE", "SIN ESPECIFICAR"}
 
df: DataFrame | None = st.session_state.get("data")
 
st.subheader("Departamentos más visitados")
st.write("Ranking de departamentos según el número total de visitantes.")
 
if df is None or df.empty:
    st.warning("No hay datos disponibles para mostrar.")
    st.stop()
faltantes = [c for c in (COL_DEPTO, COL_VISITANTES) if c not in df.columns]
if faltantes:
    st.error(f"El dataset no contiene la(s) columna(s): {', '.join(faltantes)}.")
    st.stop()
 
st.sidebar.header("Filtros")
datos = df
if COL_ANIO in df.columns:
    anios = st.sidebar.multiselect(
        "Años", sorted(df[COL_ANIO].dropna().unique().tolist()), placeholder="Todos los años"
    )
    if anios:
        datos = df[df[COL_ANIO].isin(anios)]
 
incluir_sin_depto = st.sidebar.checkbox(
    "Incluir departamento sin especificar ('-')", value=False
)
 
datos = pd.DataFrame(
    {
        "Departamento": datos[COL_DEPTO].astype("string").str.strip(),
        "Visitantes": pd.to_numeric(datos[COL_VISITANTES], errors="coerce").fillna(0),
    }
).dropna(subset=["Departamento"])
 
if not incluir_sin_depto:
    datos = datos[~datos["Departamento"].str.upper().isin(NO_ESPECIFICADO)]
 
conteos = (
    datos.groupby("Departamento", as_index=False)["Visitantes"]
    .sum()
    .sort_values(["Visitantes", "Departamento"], ascending=[False, True], ignore_index=True)
)
if conteos.empty:
    st.warning("No hay registros con un departamento válido para este filtro.")
    st.stop()
 
total = conteos["Visitantes"].sum()
conteos["Participación"] = conteos["Visitantes"] / total if total else 0
conteos["Posición"] = conteos["Visitantes"].rank(method="min", ascending=False).astype(int)
conteos["Nivel"] = conteos["Posición"].map(lambda p: f"Top {p}" if p <= 3 else "Otros")
conteos["Etiqueta"] = conteos["Posición"].astype(str) + ". " + conteos["Departamento"]
 
cantidad = (
    st.sidebar.slider("Departamentos a mostrar", 1, len(conteos), min(10, len(conteos)))
    if len(conteos) > 1
    else 1
)
grafico = conteos.head(cantidad)
 
lider = conteos.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de visitantes", f"{total:,.0f}")
c2.metric("Departamentos", f"{len(conteos):,}")
c3.metric("Departamento líder", lider["Departamento"], f"{lider['Participación']:.1%} del total", delta_color="off")
c4.metric("Concentración Top 3", f"{conteos.head(3)['Participación'].sum():.1%}")
st.caption("Se suma la columna NUMERO_VISITANTES por departamento.")

fig = go.Figure()
for nivel, color in COLORES.items():
    sub = grafico[grafico["Nivel"] == nivel]
    if sub.empty:
        continue
    fig.add_bar(
        x=sub["Visitantes"],
        y=sub["Etiqueta"],
        name=nivel,
        orientation="h",
        marker_color=color,
        text=[f"{v:,.0f}  ·  {p:.1%}" for v, p in zip(sub["Visitantes"], sub["Participación"])],
        textposition="outside",
        cliponaxis=False,
        customdata=sub[["Departamento", "Posición", "Participación"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>Posición: #%{customdata[1]}<br>"
            "Visitantes: %{x:,.0f}<br>Participación: %{customdata[2]:.1%}<extra></extra>"
        ),
    )
 
fig.add_vline(
    x=grafico["Visitantes"].mean(),
    line=dict(color="rgba(255,255,255,0.45)", width=1, dash="dot"),
    annotation_text="Promedio",
    annotation_position="top",
    annotation_font=dict(size=11, color="rgba(255,255,255,0.6)"),
)
fig.update_layout(
    template="plotly_dark",
    height=max(420, len(grafico) * 44 + 120),
    margin=dict(l=10, r=150, t=50, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", size=13),
    bargap=0.28,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
)
fig.update_xaxes(
    title="Número de visitantes", tickformat="~s", gridcolor="rgba(255,255,255,0.08)", zeroline=False
)
fig.update_yaxes(
    title="",
    categoryorder="array",
    categoryarray=grafico["Etiqueta"].tolist(),
    autorange="reversed",
    showgrid=False,
    ticksuffix="  ",
)
 
st.plotly_chart(fig, width="stretch", config={"displaylogo": False})