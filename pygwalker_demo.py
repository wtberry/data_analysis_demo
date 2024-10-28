import toml
from pathlib import Path

from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pygwalker Demo",
    page_icon="🐍",
    layout="wide",
)


toml_path = Path(__file__).parent / ".streamlit" / "custom_config.toml"
with open(toml_path, "r") as f:
    config = toml.load(f)


encoding_options = config["data"]["encoding_options"]
encoding_default = config["data"]["encoding_default"]

st.title("Data Analysis Dashboard Demo")

# uploaded file
uploaded_file = st.file_uploader("Upload a csv or excel (xlsx) file", type=["csv", "xlsx"])
encoding = st.selectbox(
    label="Select Encoding for the file",
    options=encoding_options
)
if uploaded_file is not None:
    try:
        # import data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding=encoding)  
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, encoding=encoding)
        else:
            pass
            # wrong file type should be already handled in st.file_uploader
    except UnicodeDecodeError:
        st.error(f"The file is not encoded in {encoding}. Please select a different encoding.")
    else:
        pyg_app = StreamlitRenderer(df)
        pyg_app.explorer()

