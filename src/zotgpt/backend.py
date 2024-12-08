import os
import re
import textwrap
from ast import mod
from typing import Optional, Union

from dotenv import load_dotenv
from langchain import hub

# from langchain.chains import VectorDBQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.document_loaders import PyPDFLoader

# from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# from langchain.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pyprojroot import here

from zotgpt.embed import Embeddings
from zotgpt.zotero import (
    ZoteroItem,
    get_pdf_item_from_item_key,
    make_zotero_client,
)

# Load environment variables
load_dotenv()


# class Plumber:
#     def __init__(
#         self,
#         embeddings_type: str = "cohere",
#         vector_store_type: str = "chromadb",
#         db_path: Optional[str] = None,
#     ):
#         self.chunk_size: int = 1000
#         self.chunk_overlap: int = 200
#         self.embeddings: Union[OpenAIEmbeddings, CohereEmbeddings] = (
#             self._create_embeddings(embeddings_type)
#         )
#         self.vector_store: Union[PineconeVectorStore, Chroma] = (
#             self._create_vector_store(vector_store_type, db_path)
#         )

#     def _create_embeddings(
#         self, embeddings_type: str
#     ) -> Union[OpenAIEmbeddings, CohereEmbeddings]:
#         if embeddings_type == "openai":
#             return OpenAIEmbeddings()
#         elif embeddings_type == "cohere":
#             return CohereEmbeddings()
#         else:
#             raise ValueError(f"Unsupported embeddings type: {embeddings_type}")

#     def _create_vector_store(
#         self, vector_store_type: str, db_path: Optional[str]
#     ) -> Union[PineconeVectorStore, Chroma]:
#         if vector_store_type == "pinecone":
#             return PineconeVectorStore()
#         elif vector_store_type == "chromadb":
#             if db_path is None:
#                 raise ValueError(
#                     "A database path must be provided for ChromaDB"
#                 )
#             return Chroma(db_path=db_path)
#         else:
#             raise ValueError(
#                 f"Unsupported vector store type: {vector_store_type}"
#             )

#     def load_from_path(
#         self, pdf_paths: Union[str, list[str]], reference: str
#     ) -> list:
#         if isinstance(pdf_paths, str):
#             pdf_paths = [pdf_paths]

#         all_documents_splitted = []

#         for pdf_path in pdf_paths:
#             # load documents
#             loader = PyPDFLoader(pdf_path)
#             documents_loaded = loader.load()

#             # split documents into chunks
#             text_splitter = RecursiveCharacterTextSplitter(
#                 chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
#             )
#             documents_splitted = text_splitter.split_documents(documents_loaded)

#             # update metadata
#             for doc in documents_splitted:
#                 doc.metadata.update({"source": reference})

#             all_documents_splitted.extend(documents_splitted)

#         return all_documents_splitted

#     def retrieve_data(self, query):
#         # Implement data retrieval logic here
#         pass


if __name__ == "__main__":
    # Load an example document
    zot = make_zotero_client()
    item_key = "446PVAFU"
    item_key = "VZVATVKP"
    item_key = "ZRPTUR3W"
    item_key = "22TS3QH8"
    pdf_item = get_pdf_item_from_item_key(zot, item_key)
    pot = ZoteroItem(zot, pdf_item)
    pdf_path = pot.get_pdf_path()
    # pot_source = {
    #     "title": pot.parent_item_title,
    #     "url": pot.get_url(),
    # }

    # ==============================================================
    # Storing Section
    # ==============================================================

    # Doing process manually
    loader = PyPDFLoader(pdf_path)
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

    embeddings = Embeddings(
        embeddings_type="cohere", embeddings_model="embed-english-v3.0"
    )

    # Define Pinecone vectorstore
    vector_store = PineconeVectorStore.from_documents(
        documents_splitted,
        embeddings,
        index_name=os.environ["PINECONE_INDEX_NAME"],
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
    # Retrieval Section
    # ==============================================================

    llm = ChatOpenAI(verbose=True, temperature=0.0)
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
                "filter": {"id": {"$in": ["22TS3QH8", "ZRPTUR3W"]}},
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

    print(wrapped_answer)
    print()
    for ref in references:
        print(ref)
