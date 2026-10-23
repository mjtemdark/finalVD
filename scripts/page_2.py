import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pandas import DataFrame, Series

st.set_page_config(layout="wide")

COL_DEPTO = "DEPARTAMENTO_OCM"
COL_ANIO = "ANIO"

COLORES = {
    "Top 1": "#E9C46A",
    "Top 2": "#A8B3B0",
    "Top 3": "#CD7F32",
    "Otros": "#287271",
}
NO_ESPECIFICADO = {"", "-", "--", "NA", "N/A", "NAN", "NULL", "NONE", "SIN ESPECIFICAR"}

@st.cache_data(show_spinner=False)
def preparar(df: DataFrame, ocultar_no_especificados: bool) -> DataFrame:
    """Devuelve solo las columnas necesarias, con el departamento limpio."""
    columnas = [COL_DEPTO] + ([COL_ANIO] if COL_ANIO in df.columns else [])
    datos = df[columnas].copy()
    datos[COL_DEPTO] = datos[COL_DEPTO].astype("string").str.strip()
    datos = datos[datos[COL_DEPTO].notna()]
    if ocultar_no_especificados:
        datos = datos[~datos[COL_DEPTO].str.upper().isin(NO_ESPECIFICADO)]
    return datos


def contar(departamentos: Series) -> DataFrame:
    conteos = (
        departamentos.value_counts()
        .rename_axis("Departamento")
        .reset_index(name="Registros")
        .sort_values(["Registros", "Departamento"], ascending=[False, True], ignore_index=True)
    )
    conteos["Participación"] = conteos["Registros"] / conteos["Registros"].sum()
    # method="min": los empates comparten posición
    conteos["Posición"] = conteos["Registros"].rank(method="min", ascending=False).astype(int)
    conteos["Nivel"] = conteos["Posición"].map(lambda p: f"Top {p}" if p <= 3 else "Otros")
    conteos["Etiqueta"] = conteos["Posición"].astype(str) + ". " + conteos["Departamento"]
    return conteos


def grafico_ranking(grafico: DataFrame, metrica: str) -> go.Figure:
    es_porcentaje = metrica == "Participación"
    fig = go.Figure()

    for nivel, color in COLORES.items():
        sub = grafico[grafico["Nivel"] == nivel]
        if sub.empty:
            continue
        fig.add_bar(
            x=sub[metrica],
            y=sub["Etiqueta"],
            name=nivel,
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=[
                f"{r:,.0f}  ·  {p:.1%}" for r, p in zip(sub["Registros"], sub["Participación"])
            ],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=12),
            customdata=sub[["Departamento", "Posición", "Registros", "Participación"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Posición: #%{customdata[1]}<br>"
                "Registros: %{customdata[2]:,.0f}<br>"
                "Participación: %{customdata[3]:.1%}"
                "<extra></extra>"
            ),
            selected=dict(marker=dict(opacity=1)),
            unselected=dict(marker=dict(opacity=0.35)),
        )

    promedio = grafico[metrica].mean()
    fig.add_vline(
        x=promedio,
        line=dict(color="rgba(255,255,255,0.45)", width=1, dash="dot"),
        annotation_text="Promedio",
        annotation_position="top",
        annotation_font=dict(size=11, color="rgba(255,255,255,0.6)"),
    )

    fig.update_layout(
        template="plotly_dark",
        height=max(420, len(grafico) * 44 + 120),
        margin=dict(l=10, r=110, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", size=13),
        bargap=0.28,
        hoverlabel=dict(font_size=13),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""
        ),
        clickmode="event+select",
    )
    fig.update_xaxes(
        title="Participación del total" if es_porcentaje else "Cantidad de registros",
        tickformat=".0%" if es_porcentaje else "~s",
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False,
        showline=False,
    )
    fig.update_yaxes(
        title="",
        categoryorder="array",
        categoryarray=grafico["Etiqueta"].tolist(),
        autorange="reversed",  # el #1 queda arriba
        showgrid=False,
        ticksuffix="  ",
    )
    return fig


def grafico_evolucion(datos: DataFrame, departamentos: list[str]) -> go.Figure:
    evolucion = (
        datos[datos[COL_DEPTO].isin(departamentos)]
        .groupby([COL_ANIO, COL_DEPTO])
        .size()
        .reset_index(name="Registros")
        .rename(columns={COL_DEPTO: "Departamento", COL_ANIO: "Año"})
        .sort_values("Año")
    )
    fig = px.line(
        evolucion,
        x="Año",
        y="Registros",
        color="Departamento",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{fullData.name}</b><br>Año %{x}<br>Registros: %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", size=13),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    )
    fig.update_xaxes(type="category", showgrid=False, title="")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", tickformat="~s", title="Registros")
    return fig


def grafico_treemap(conteos: DataFrame) -> go.Figure:
    fig = px.treemap(
        conteos,
        path=["Departamento"],
        values="Registros",
        color="Registros",
        color_continuous_scale=["#1b3b3a", "#287271", "#E9C46A"],
        template="plotly_dark",
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percentRoot:.1%}",
        hovertemplate="<b>%{label}</b><br>Registros: %{value:,.0f}<br>%{percentRoot:.1%} del total<extra></extra>",
    )
    fig.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        font=dict(family="Inter, Arial, sans-serif", size=14),
    )
    return fig

df: DataFrame | None = st.session_state.get("data")

st.subheader("Departamentos más visitados")
st.write(
    "Ranking de departamentos según la cantidad de registros del dataset. "
    "Filtra por año, cambia la métrica o haz clic en una barra para ver su evolución."
)

if df is None or df.empty:
    st.warning("No hay datos disponibles para mostrar.")
    st.stop()

if COL_DEPTO not in df.columns:
    st.error(f"El dataset no contiene la columna {COL_DEPTO}.")
    st.stop()

st.sidebar.header("Filtros")

ocultar = st.sidebar.checkbox(
    "Ocultar departamentos sin especificar ('-')",
    value=True,
    help="Excluye valores vacíos, '-', 'N/A', etc.",
)
datos_base = preparar(df, ocultar)

tiene_anio = COL_ANIO in datos_base.columns
if tiene_anio:
    anios = sorted(datos_base[COL_ANIO].dropna().unique().tolist())
    anios_sel = st.sidebar.multiselect(
        "Años",
        options=anios,
        default=[],
        placeholder="Todos los años",
    )
    datos = datos_base[datos_base[COL_ANIO].isin(anios_sel)] if anios_sel else datos_base
else:
    datos = datos_base

busqueda = st.sidebar.text_input("Buscar departamento", placeholder="Ej. Cusco")
if busqueda:
    datos = datos[datos[COL_DEPTO].str.contains(busqueda.strip(), case=False, na=False)]

conteos = contar(datos[COL_DEPTO])

if conteos.empty:
    st.warning("No hay registros con un departamento válido para este filtro.")
    st.stop()

if len(conteos) > 1:
    cantidad = st.sidebar.slider(
        "Departamentos a mostrar",
        min_value=1,
        max_value=len(conteos),
        value=min(10, len(conteos)),
    )
else:
    cantidad = 1

metrica = st.sidebar.radio(
    "Métrica",
    options=["Registros", "Participación"],
    format_func=lambda m: "Cantidad de registros" if m == "Registros" else "% del total",
    horizontal=True,
)

lider = conteos.iloc[0]
top3 = conteos.head(3)["Participación"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Registros contabilizados", f"{conteos['Registros'].sum():,}")
k2.metric("Departamentos", f"{len(conteos):,}")
k3.metric("Departamento líder", lider["Departamento"], f"{lider['Participación']:.1%} del total", delta_color="off")
k4.metric("Concentración Top 3", f"{top3:.1%}")

st.caption("Se cuenta cada fila como un registro; los registros sin departamento se excluyen.")

tab_rank, tab_evol, tab_part, tab_datos = st.tabs(
    ["🏆 Ranking", "📈 Evolución", "🧩 Participación", "📋 Datos"]
)

grafico = conteos.head(cantidad)
seleccionados: list[str] = []

with tab_rank:
    evento = st.plotly_chart(
        grafico_ranking(grafico, metrica),
        width="stretch",
        key="ranking",
        on_select="rerun",
        selection_mode="points",
        config={
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
        },
    )
    puntos = evento.selection.points if evento and evento.selection else []
    seleccionados = list(dict.fromkeys(p["customdata"][0] for p in puntos))

    if seleccionados:
        st.info(
            "Seleccionado: **" + ", ".join(seleccionados) + "** — mira la pestaña "
            "**Evolución** para ver su comportamiento por año."
        )
    else:
        st.caption("💡 Haz clic en una o varias barras (Shift + clic) para analizarlas en detalle.")

with tab_evol:
    if not tiene_anio:
        st.info("El dataset no tiene la columna ANIO, no es posible mostrar la evolución.")
    else:
        por_defecto = seleccionados or grafico["Departamento"].head(5).tolist()
        elegidos = st.multiselect(
            "Departamentos a comparar",
            options=conteos["Departamento"].tolist(),
            default=por_defecto,
            key=f"evol_{'|'.join(por_defecto)}",
        )
        if elegidos:
            base_evol = datos_base[datos_base[COL_DEPTO].isin(conteos["Departamento"])]
            st.plotly_chart(
                grafico_evolucion(base_evol, elegidos),
                width="stretch",
                config={"displaylogo": False},
            )
        else:
            st.info("Selecciona al menos un departamento.")

with tab_part:
    st.plotly_chart(
        grafico_treemap(conteos),
        width="stretch",
        config={"displaylogo": False},
    )

with tab_datos:
    st.dataframe(
        conteos[["Posición", "Departamento", "Registros", "Participación"]],
        hide_index=True,
        width="stretch",
        column_config={
            "Posición": st.column_config.NumberColumn(format="#%d", width="small"),
            "Registros": st.column_config.ProgressColumn(
                format="%d",
                min_value=0,
                max_value=int(conteos["Registros"].max()),
            ),
            "Participación": st.column_config.NumberColumn(format="percent"),
        },
    )
    st.download_button(
        "⬇️ Descargar CSV",
        data=conteos.drop(columns=["Etiqueta"]).to_csv(index=False).encode("utf-8"),
        file_name="departamentos_mas_visitados.csv",
        mime="text/csv",
    )