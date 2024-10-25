from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import LoginError
import yaml
from yaml.loader import SafeLoader


def run_analysis():
    # uploaded file
    uploaded_file = st.file_uploader("Upload a csv file", type=["csv"])
    if uploaded_file is not None:
        # import data
        df = pd.read_csv(uploaded_file)

        pyg_app = StreamlitRenderer(df)
        pyg_app.explorer()


st.set_page_config(
    page_title="Pygwalker Demo",
    page_icon="🐍",
    layout="wide",
)

st.title("Data Analysis Dashboard Demo")

# user auth logic here
with open("config.yaml", "r") as f:
    config = yaml.load(f, Loader=SafeLoader)


# Please remember to pass the authenticator object to each and every page in a multi-page application as a session state variable.

authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=False
)

authenticator.login(
    location='main', 
    max_login_attempts=3,
)

if st.session_state["authentication_status"]:
    authenticator.logout(
        'Logout',
        location='sidebar',
    )
    st.sidebar.write(f'Welcome {st.session_state["name"]}!')
    run_analysis()
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
elif not st.session_state["authentication_status"]:
    st.error('Username/password is incorrect')

