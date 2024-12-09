import os

import streamlit as st
from dotenv import load_dotenv

from zotgpt.embed import EmbeddingsFactory
from zotgpt.metastore import MetaStore
from zotgpt.vectorstore import VectorStoreFactory
from zotgpt.zotero import ZoteroWrapper, make_zotero_client

load_dotenv()


def initialize_embeddings():
    if "embeddings" not in st.session_state:
        ef = EmbeddingsFactory(
            embeddings_type=os.environ["EMBEDDINGS_TYPE"],
            embeddings_model=os.environ["EMBEDDINGS_MODEL"],
        )
        st.session_state["embeddings"] = ef.create()


def initialize_vector_store():
    if "vector_store" not in st.session_state:
        vsf = VectorStoreFactory(
            embeddings=st.session_state["embeddings"],
            store_type=os.environ["VECTOR_STORE_TYPE"],
            collection_name=os.environ["VECTOR_STORE_INDEX"],
        )
        st.session_state["vector_store"] = vsf.create()


def initialize_metastore():
    if "metastore" not in st.session_state:
        st.session_state["metastore"] = MetaStore(
            os.environ["ZOTERO_APP_SQLITE"]
        )


def initialize_zotero_client():
    if "zotero_client" not in st.session_state:
        st.session_state["zotero_client"] = make_zotero_client()


def initialize_zotero_wrapper():
    if "zotero_wrapper" not in st.session_state:
        st.session_state["zotero_wrapper"] = ZoteroWrapper(
            st.session_state["zotero_client"]
        )


def initialize():
    initialize_embeddings()
    initialize_vector_store()
    initialize_metastore()
    initialize_zotero_client()
    initialize_zotero_wrapper()
