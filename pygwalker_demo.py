import toml
from pathlib import Path

from pygwalker.api.streamlit import StreamlitRenderer
import pandas as pd
from pandasai.llm import OpenAI, AzureOpenAI
from pandasai import SmartDataframe
from pandasai import Agent
from pandasai.responses.streamlit_response import StreamlitResponse
import streamlit as st


def chat_with_data(agent):

    with st.chat_message("assistant"):
        st.text("Hello! I'm here to help you with your transaction data 👏")
    # initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # go through the chat history
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            # questions
            if "question" in message:
                st.text(message["question"])
            # answers
            elif "answer" in message:
                st.write(message["answer"])
            elif "error" in message:    
                st.text(message["error"])

    user_input = st.chat_input("Enter a question to ask the data", key="chat_input")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        # add the user input to the chat history
        st.session_state["chat_history"].append({"role": "user", "question": user_input})
        
        # generate the response
        try:
            with st.spinner("AI is thinking..."):
                response = agent.chat(user_input)
                st.session_state["chat_history"].append({"role": "assistant", "answer": response})
                st.write(response)
        except Exception as e:
            st.error(str(e))
            error_message = "⚠️Sorry, Couldn't generate the answer! Please try rephrasing your question!"
            st.session_state["chat_history"].append({"role": "assistant", "error": error_message})
    
    # function to clear the chat history
    def clear_chat_history():
        st.session_state["chat_history"] = []

    st.button("Clear Chat History", on_click=clear_chat_history)





st.set_page_config(
    page_title="Data Analysis Dashboard Demo",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)


toml_path = Path(__file__).parent / ".streamlit" / "custom_config.toml"
with open(toml_path, "r") as f:
    config = toml.load(f)


encoding_options = config["data"]["encoding_options"]
encoding_default = config["data"]["encoding_default"]
agent_provider_options = config["chat"]["providers"]

st.title("Explore and Chat with your data")

st.markdown("From the left sidebar, you can upload data file, select LLM provider, and chat with your data.")

df = None
llm_key = None
agent = None
azure_openai_endpoint_url = None
azure_openai_api_version = None
azure_openai_deployment_name = None 


# uploaded file
with st.sidebar:
    st.header("Settings")
    st.markdown("## File Upload")
    st.markdown("### Upload own data file")
    uploaded_file = st.file_uploader("Upload a csv or excel (xlsx) file", type=["csv", "xlsx"])
    encoding = st.selectbox(
        label="Select Encoding for the file",
        options=encoding_options
    )
    
    st.markdown("### Download Sample Data")
    download_file = pd.read_csv("data/titanic.csv").to_csv(index=False)
    st.download_button("Download Sample Data", download_file, file_name="titanic.csv", mime="text/csv")

    # chat agent settings
    st.markdown("## Chat Agent Settings")
    llm_provider = st.selectbox(
        label="Select LLM Provider",
        options=agent_provider_options,
    )
    llm_key = st.text_input(
        label="Enter your LLM API key",
        placeholder="Enter your LLM API key",
        type="password",
        value=None,
    )
    if llm_provider == "azure":
        azure_openai_endpoint_url = st.text_input(
            label="Enter your Azure OpenAI Endpoint URL",
            placeholder="Enter your Azure OpenAI Endpoint URL",
            type="password",
            value=None,
        )
        azure_openai_api_version = st.text_input(
            label="Enter your Azure OpenAI API Version",
            placeholder="Enter your Azure OpenAI API Version",
            value=None,
        )
        azure_openai_deployment_name = st.text_input(
            label="Enter your Azure OpenAI Deployment Name",
            placeholder="Enter your Azure OpenAI Deployment Name",
            value=None,
        )

st.markdown("### Data Table")
if uploaded_file is None:
    st.write("Data table will be displayed here.")

elif uploaded_file is not None:
    try:
        with st.spinner("Loading data..."):
            # import data
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, encoding=encoding)  
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            else:
                pass
                # wrong file type should be already handled in st.file_uploader
    except UnicodeDecodeError:
        st.sidebar.error(f"The file is not encoded in {encoding}. Please select a different encoding.")
    else:
        st.sidebar.success("Data imported successfully.")
        st.dataframe(df)

    if llm_key is not None:
        # initialize chat agent
        if llm_provider == "openai":
            llm = OpenAI(api_token=llm_key)
            agent = Agent(
                df, config={
                    "llm":llm, "verbose":True, "response_parser":StreamlitResponse
                }
            )
            st.sidebar.success("Chat agent initialized successfully.")
        elif llm_provider == "azure":
            if all([azure_openai_endpoint_url, azure_openai_api_version, azure_openai_deployment_name]):
                llm = AzureOpenAI(
                    api_token=llm_key,
                    azure_endpoint=azure_openai_endpoint_url,
                    api_version=azure_openai_api_version,
                    deployment_name=azure_openai_deployment_name,
                )
                agent = Agent(
                    df, config={
                        "llm":llm, "verbose":True, "response_parser":StreamlitResponse
                    }
                )
                st.sidebar.success("Chat agent initialized successfully.")
            else:
                pass
        
        else:
            st.sidebar.error("Currently, only OpenAI and Azure Open AI are supported.")

tab1, tab2 = st.tabs(["**Data Explorer**", "**Chat with Data**"])
with tab1:
    st.markdown("### Data Explorer")
    if df is not None:
        pyg_app = StreamlitRenderer(df)
        pyg_app.explorer()
    else:
        st.warning("Please upload a file first.")

with tab2:
    st.markdown("### Chat with Data")
    if df is not None:
        if llm_provider in agent_provider_options:
            if llm_key is not None and agent is not None:
                st.markdown(f"#### {llm_provider} Chat")
                # user_input = st.chat_input(placeholder="Ask a question")
                # with st.spinner("AI is thinking..."):
                #     response = agent.chat(user_input)
                #     st.write(response)
                chat_with_data(agent)
            else:
                st.error(f"Please enter your {llm_provider} API key.")
        else:
            st.error(f"Currently, only {agent_provider_options} is supported.")
    else:
        st.warning("Please upload a file first.")



