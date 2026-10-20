import streamlit as st
import kagglehub
import pandas as pd

path=kagglehub.dataset_download("sumanbera19/laptop-price-dataset")

df=pd.read_csv(path+"/laptop.csv")

if "data" not in st.session_state:
    st.session_state.data = df

pg = st.navigation([
    st.Page("scripts/dataframe.py", title="Resumen de Datos"),
    st.Page("scripts/page_1.py", title="Grafico 1"),
    st.Page("scripts/page_2.py", title="Grafico 2"),
    st.Page("scripts/page_3.py", title="Grafico 3"), ])
pg.run()