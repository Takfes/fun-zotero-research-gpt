import streamlit as st

from zotgpt.app.utils import (
    initialize_embeddings_and_vector_store,
    initialize_zotero_client,
)
from zotgpt.zotero import collection_constructor, make_zotero_client

# Initialize embeddings and vector store only once
initialize_embeddings_and_vector_store()

# Initialize Zotero client only once
initialize_zotero_client()

zot = st.session_state["vector_store"]

collections = collection_constructor(zot)

st.write(collections.get_collection_count())
st.write(collections.get_collection_dict())
