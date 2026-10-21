import streamlit as st
import kagglehub
import pandas as pd
import requests
import zipfile
from io import BytesIO
uri="https://proyectos.inei.gob.pe/iinei/srienaho/descarga/CSV/1049-Modulo1963.zip"
response = requests.get(uri)
response.raise_for_status()

with zipfile.ZipFile(BytesIO(response.content)) as z:
    #SOLO CSV
    csv_file = next(
        f for f in z.namelist()
        if f.lower().endswith(".csv")
    )
    # Leer CSV
    with z.open(csv_file) as f:
        df = pd.read_csv(f,delimiter=";", low_memory=False)

#LIMPIAR CADENA ERROR
df.replace('#¡NULO!',pd.NA,inplace=True)
df.info()
df.head(5)
if "data" not in st.session_state:
    st.session_state.data = df

pg = st.navigation([
    st.Page("scripts/dataframe.py", title="Resumen de Datos"),
    st.Page("scripts/page_1.py", title="Grafico 1"),
    st.Page("scripts/page_2.py", title="Grafico 2"),
    st.Page("scripts/page_3.py", title="Grafico 3"), ])
pg.run()