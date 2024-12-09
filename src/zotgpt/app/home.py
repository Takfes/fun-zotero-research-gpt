import streamlit as st

st.set_page_config(
    page_title="Your App Title",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("ZotGPT: powered by LangChain🦜🔗")

st.subheader("Home")
st.write(
    "This is the home page of the ZotGPT app. Here you can find an overview of the app's features and functionalities."
)

st.subheader("Converse 💬")
st.write(
    "The Converse page allows you to search through your Zotero library using advanced search functionalities powered by LangChain."
)

st.subheader("Library 📚")
st.write(
    "In the Library page, you can view and manage your Zotero collections. You can add, remove, and organize your research materials."
)

st.subheader("Settings ⚙️")
st.write(
    "On the Settings page, you can configure the app's settings, including API keys, preferences, and other customization options."
)

st.subheader("Zi-Old-Chat 🚧")
st.write(
    "DEPRECATED! The Zi-Old-Chat page is an older version of the chat interface. It is no longer maintained and will be removed in future versions."
)
