import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

URI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/CSV/1049-Modulo1963.zip"
CACHE_DIR = Path(".cache")
CSV_LOCAL = CACHE_DIR / "datos.csv"


def descargar_zip() -> Path:
    """Descarga el ZIP, extrae el CSV a disco y descarta el ZIP. Solo ocurre una vez."""
    if CSV_LOCAL.exists():
        return CSV_LOCAL

    CACHE_DIR.mkdir(exist_ok=True)
    tmp_csv = CSV_LOCAL.with_suffix(".csv.part")

    with requests.get(URI, timeout=120, stream=True) as r:
        r.raise_for_status()
        # El ZIP va a un archivo temporal en disco, no a memoria
        with tempfile.TemporaryFile() as tmp_zip:
            for chunk in r.iter_content(chunk_size=1 << 20):
                tmp_zip.write(chunk)
            tmp_zip.seek(0)

            with zipfile.ZipFile(tmp_zip) as z:
                nombre = next(f for f in z.namelist() if f.lower().endswith(".csv"))
                with z.open(nombre) as origen, open(tmp_csv, "wb") as destino:
                    shutil.copyfileobj(origen, destino)

    # Renombrar csv
    tmp_csv.replace(CSV_LOCAL)
    return CSV_LOCAL


@st.cache_data(show_spinner="Descargando y procesando datos")
def cargar_datos() -> pd.DataFrame:
    ruta = descargar_zip()
    return pd.read_csv(
        ruta,
        delimiter=";",
        low_memory=False,
        na_values=["#¡NULO!"],
    )


if "data" not in st.session_state:
    st.session_state.data = cargar_datos()

pg = st.navigation([
    st.Page("scripts/dataframe.py", title="Resumen de Datos"),
    st.Page("scripts/page_1.py", title="Grafico 1"),
    st.Page("scripts/page_2.py", title="Grafico 2"),
    st.Page("scripts/page_3.py", title="Grafico 3"),
])
pg.run()