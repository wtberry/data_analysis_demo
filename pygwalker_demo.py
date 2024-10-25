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
uploaded_file = st.file_uploader("Upload a csv or excel (xlsx) file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # import data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)  
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        pass
        # wrong file type should be already handled in st.file_uploader


    pyg_app = StreamlitRenderer(df)
    pyg_app.explorer()