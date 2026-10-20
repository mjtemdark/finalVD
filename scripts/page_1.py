import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

chart=px.line(chart_data)
st.plotly_chart(chart)