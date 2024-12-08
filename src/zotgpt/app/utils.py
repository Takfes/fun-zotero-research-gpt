import os

import streamlit as st

from zotgpt.embed import EmbeddingsFactory
from zotgpt.storage import VectorStoreFactory
from zotgpt.zotero import make_zotero_client


def initialize_embeddings_and_vector_store():
    # Initialize embeddings and vector store only once
    if "embeddings" not in st.session_state:
        ef = EmbeddingsFactory(
            embeddings_type=os.environ["EMBEDDINGS_TYPE"],
            embeddings_model=os.environ["EMBEDDINGS_MODEL"],
        )
        st.session_state["embeddings"] = ef.create()

    if "vector_store" not in st.session_state:
        vsf = VectorStoreFactory(
            embeddings=st.session_state["embeddings"],
            store_type=os.environ["VECTOR_STORE_TYPE"],
            collection_name=os.environ["VECTOR_STORE_INDEX"],
        )
        st.session_state["vector_store"] = vsf.create()


def initialize_zotero_client():
    # Initialize Zotero client only once
    if "zotero_client" not in st.session_state:
        st.session_state["zotero_client"] = make_zotero_client()
