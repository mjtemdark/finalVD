import plotly.express as px
import streamlit as st
from pandas import DataFrame

st.set_page_config(layout="wide")

df: DataFrame = st.session_state.data

st.subheader("Departamentos más visitados")
st.write(
    "Ranking de departamentos según la cantidad de registros del dataset. "
    "Selecciona un año o explora el total de años."
)

if df is None or df.empty:
    st.warning("No hay datos disponibles para mostrar.")
    st.stop()

if "DEPARTAMENTO_OCM" not in df.columns:
    st.error("El dataset no contiene la columna DEPARTAMENTO_OCM.")
    st.stop()

st.sidebar.header("Filtros")
anios = sorted(df["ANIO"].dropna().unique().tolist()) if "ANIO" in df.columns else []
anio_seleccionado = st.sidebar.selectbox(
    "Año",
    options=[None, *anios],
    format_func=lambda anio: "Todos los años" if anio is None else str(anio),
)

datos = df if anio_seleccionado is None or "ANIO" not in df.columns else df[
    df["ANIO"] == anio_seleccionado
]

departamentos = datos["DEPARTAMENTO_OCM"].dropna().astype(str).str.strip()
departamentos = departamentos[departamentos.ne("")]
conteos = (
    departamentos.value_counts()
    .rename_axis("Departamento")
    .reset_index(name="Registros")
    .sort_values(["Registros", "Departamento"], ascending=[False, True])
    .reset_index(drop=True)
)

if conteos.empty:
    st.warning("No hay registros con un departamento válido para este filtro.")
    st.stop()

conteos["Posición"] = range(1, len(conteos) + 1)
if len(conteos) > 1:
    cantidad = st.sidebar.slider(
        "Departamentos a mostrar",
        min_value=1,
        max_value=len(conteos),
        value=min(10, len(conteos)),
    )
else:
    cantidad = 1

grafico = conteos.head(cantidad).copy()
grafico["Nivel"] = grafico["Posición"].map(
    lambda posicion: f"Top {posicion}" if posicion <= 3 else "Otros"
)
grafico["Etiqueta"] = grafico.apply(
    lambda fila: f"{fila['Posición']}. {fila['Departamento']}", axis=1
)

col1, col2 = st.columns(2)
with col1:
    st.metric("Registros contabilizados", f"{len(departamentos):,}")
with col2:
    st.metric("Departamentos", f"{len(conteos):,}")

st.caption(
    "Se cuenta cada fila como un registro; los registros sin departamento se excluyen."
)

fig = px.bar(
    grafico,
    x="Registros",
    y="Etiqueta",
    color="Nivel",
    orientation="h",
    category_orders={"Etiqueta": grafico["Etiqueta"].tolist()[::-1]},
    color_discrete_map={
        "Top 1": "#E9C46A",
        "Top 2": "#A8B3B0",
        "Top 3": "#CD7F32",
        "Otros": "#287271",
    },
    custom_data=["Departamento", "Posición"],
    labels={"Registros": "Cantidad de registros", "Nivel": "Nivel"},
)
fig.update_traces(
    texttemplate="%{x:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Registros: %{x:,.0f}<br>"
        "Posición: #%{customdata[1]}<extra></extra>"
    ),
)
fig.update_layout(
    height=max(450, len(grafico) * 38),
    margin=dict(l=10, r=70, t=20, b=10),
    xaxis_title="Cantidad de registros",
    yaxis_title="",
    legend_title="",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Arial, sans-serif", size=13),
)

st.plotly_chart(fig, width="stretch")
