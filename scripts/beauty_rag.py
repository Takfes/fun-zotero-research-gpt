import os

from dotenv import load_dotenv

from zotgpt.backend import load_document
from zotgpt.embed import EmbeddingsFactory
from zotgpt.retrieval import Retriever, format_answer
from zotgpt.vectorstore import VectorStoreFactory
from zotgpt.zotero import (
    ZoteroItem,
    get_pdf_item_from_item_key,
    make_zotero_client,
)

if __name__ == "__main__":
    load_dotenv()

    ef = EmbeddingsFactory(
        embeddings_type=os.environ["EMBEDDINGS_TYPE"],
        embeddings_model=os.environ["EMBEDDINGS_MODEL"],
    )
    embeddings = ef.create()

    vsf = VectorStoreFactory(
        embeddings=embeddings,
        store_type=os.environ["VECTOR_STORE_TYPE"],
        collection_name=os.environ["VECTOR_STORE_INDEX"],
    )
    vs = vsf.create()

    zot = make_zotero_client()
    # item_key = "V4JYPRNW"
    # item_key = "7EDVIG8F"
    item_key = "5RYT6HXK"
    pdf_item = get_pdf_item_from_item_key(zot, item_key)
    pot = ZoteroItem(zot, pdf_item)
    metadata = {
        "source": pot.get_url(),
        "id": pot.key,
        "title": pot.get_title(),
    }

    documents = load_document(pot.get_pdf_path(), metadata=metadata)

    vs.add_documents(documents)

    r = Retriever(vector_store=vs)
    query = """
    What do you know about Decision Transformer in the context of Optimization and Reinforcement Learning?
    """
    response = r.retrieve(query, chat_history=[])
    format_answer(response, wrap_text=True, unique_references=True)
