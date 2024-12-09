import os
import re
import textwrap
from ast import mod

from dotenv import load_dotenv
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pyprojroot import here

from zotgpt.embed import EmbeddingsFactory
from zotgpt.vectorstore import VectorStoreFactory
from zotgpt.zotero import (
    ZoteroItem,
    get_pdf_item_from_item_key,
    make_zotero_client,
)

# Load environment variables
load_dotenv()


if __name__ == "__main__":
    # Load an example document
    zot = make_zotero_client()

    item_key = "RP5LBBBC"
    item_key = "446PVAFU"
    item_key = "VZVATVKP"
    item_key = "ZRPTUR3W"
    item_key = "22TS3QH8"
    item_key = "V4JYPRNW"
    pdf_item = get_pdf_item_from_item_key(zot, item_key)
    pot = ZoteroItem(zot, pdf_item)

    pot.key
    pot.get_title()
    pot.get_url()

    # ==============================================================
    # Storing Section
    # ==============================================================

    # Doing process manually
    # loader = PyPDFLoader(pot.get_url())
    loader = PyPDFLoader(pot.get_pdf_path())
    documents_loaded = loader.load()

    # Splitting text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    documents_splitted = text_splitter.split_documents(documents_loaded)
    len(documents_splitted)

    # Update metadata
    for doc in documents_splitted:
        doc.metadata.update({"source": pot.get_url()})
        doc.metadata.update({"id": pot.key})
        doc.metadata.update({"title": pot.get_title()})
        # doc.metadata.update({"source": pot_source})
        # print(doc.metadata)

    # Define the OpenAI embedding model
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ["OPENAI_API_KEY"],
        model="text-embedding-ada-002",
    )

    # Define the Cohere embedding model
    # https://docs.cohere.com/v2/docs/embed-on-langchain
    embeddings = CohereEmbeddings(
        cohere_api_key=os.environ["COHERE_API_KEY"], model="embed-english-v3.0"
    )

    # Define Embeddings from EmbeddingsFactory
    # Method 1: Using __call__
    ef = EmbeddingsFactory("openai", "text-embedding-ada-002")
    print(ef.embeddings_type, ef.embeddings_model, ef.dimension)
    embeddings = ef.create()  # or directly calling ef()
    embeddings = EmbeddingsFactory("openai", "text-embedding-ada-002")()

    embeddings = EmbeddingsFactory("cohere", "embed-english-v3.0")()

    vector = embeddings.embed_query(doc.page_content)
    len(vector)

    # Define Pinecone vectorstore
    vector_store = PineconeVectorStore.from_documents(
        documents_splitted,
        embeddings,
        index_name=os.environ["VECTOR_STORE_INDEX"],
        # upsert=True,  # This will add new documents to the existing index
    )

    # Define Chroma vectorstore
    # https://github.com/hwchase17/chroma-langchain/blob/master/persistent-qa.ipynb
    # persist_directory = here("./data/chroma_db").__str__()
    persist_directory = "../../data/chroma_db"

    vector_store = Chroma.from_documents(
        documents=documents_splitted,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    # ==============================================================
    # ==============================================================
    # ==============================================================

    persist_directory = here("./data/chroma_db").__str__()
    # persist_directory = "../../data/chroma_db"
    collection_name = "fun-zotero-research-gpt"

    vector_store_factory = VectorStoreFactory(
        store_type="chroma",
        embeddings=embeddings,  # Pass embeddings instance
        collection_name=collection_name,
        persist_directory=persist_directory,
    )

    vector_store = vector_store_factory.create()  # or vector_store_factory()

    vector_store.from_documents(
        documents=documents_splitted,
        embedding=embeddings,
        index_name=collection_name,
    )

    vector_store.add_documents(documents_splitted)
    len(documents_splitted)

    # ==============================================================
    # Retrieval Section
    # ==============================================================

    llm = ChatOpenAI(verbose=True, temperature=0.0, model="gpt-3.5-turbo")

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    stuff_documents_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )

    qa = create_retrieval_chain(
        retriever=vector_store.as_retriever(),
        combine_docs_chain=stuff_documents_chain,
    )

    qa = create_retrieval_chain(
        retriever=vector_store.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"id": {"$in": ["V4JYPRNW"]}},
            }
        ),
        combine_docs_chain=stuff_documents_chain,
    )

    # query = "Can you explain the main concepts relative to Simulation-guided Beam Search for Neural Combinatorial Optimization?"
    query = "What do you know about RL in optimization?"
    result = qa.invoke(input={"input": query})

    wrapped_answer = textwrap.fill(result["answer"], width=80)
    references = [
        x.metadata["source"] + " page " + str(x.metadata["page"])
        for x in result["context"]
    ]
    references = list(set(references))

    print(wrapped_answer)
    print()
    for ref in references:
        print(ref)
