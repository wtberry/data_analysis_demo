from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pygwalker Demo",
    page_icon="🐍",
    layout="wide",
)

st.title("Data Analysis Dashboard Demo")

# uploaded file
uploaded_file = st.file_uploader("Upload a csv file", type=["csv"])

if uploaded_file is not None:
    # import data
    df = pd.read_csv(uploaded_file)


    pyg_app = StreamlitRenderer(df)
    pyg_app.explorer()