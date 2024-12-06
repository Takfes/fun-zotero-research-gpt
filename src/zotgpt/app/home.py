import streamlit as st

from zotgpt.zotero import (
    collection_constructor,
    make_zotero_client,
)

st.set_page_config(
    page_title="Your App Title",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header("ZotGPT: powered by LangChain🦜🔗")

zot = make_zotero_client()

collections = collection_constructor(zot)

st.write(collections.get_collection_count())
st.write(collections.get_collection_dict())
