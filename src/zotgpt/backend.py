import os
import re
from ast import mod
from typing import Union

from dotenv import load_dotenv
from langchain import hub
from langchain.chains import VectorDBQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings  # , CohereEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import Pinecone, PineconeVectorStore
from pyprojroot import here

from zotgpt.zotero import (
    ZoteroItem,
    collection_constructor,
    get_pdf_item_from_item_key,
    get_pdf_items_from_collection_key,
    make_zotero_client,
)

# Load environment variables
load_dotenv()


class Plumber:
    def __init__(self):
        self.chunk_size: int = 1000
        self.chunk_overlap: int = 200
        self.reference_sources: str = None
        self._embeddings: str = "cohere"
        self.embeddings: Union[OpenAIEmbeddings, CohereEmbeddings] = None
        self._vector_store: str = "chromadb"
        self.vector_store = Union[PineconeVectorStore, Chroma]

    def prepare_pdf(pdf_path: str):
        # load documents
        loader = PyPDFLoader(pdf_path)
        documents_loaded = loader.load()

        # split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        documents_splitted = text_splitter.split_documents(documents_loaded)

        # update metadata
        for doc in documents_splitted:
            doc.metadata.update({"source": pot.parent_item_title})

    def make_embeddings(
        model: str = "openai",
    ) -> Union[OpenAIEmbeddings, CohereEmbeddings]:
        if model == "openai":
            return OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
        elif model == "cohere":
            return CohereEmbeddings(model="embed-english-v3.0")

    def make_vectorstore(
        model: str = "pinecone",
    ):
        if model == "pinecone":
            return PineconeVectorStore
        elif model == "chromadb":
            return CohereEmbeddings(model="embed-english-v3.0")


if __name__ == "__main__":
    # Load an example document
    zot = make_zotero_client()
    item_key = "446PVAFU"
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
        doc.metadata.update({"source": pot.parent_item_title})
        # doc.metadata.update({"source": pot_source})
        # print(doc.metadata)

    # Define the OpenAI embedding model
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    # Define Pinecone vectorstore
    vector_store = PineconeVectorStore.from_documents(
        documents_splitted,
        embeddings,
        index_name=os.environ["PINECONE_INDEX_NAME"],
        upsert=True,  # This will add new documents to the existing index
    )

    # Define the Cohere embedding model
    # https://docs.cohere.com/v2/docs/embed-on-langchain
    embeddings = CohereEmbeddings(model="embed-english-v3.0")

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

    query = "Can you explain the main concepts relative to Simulation-guided Beam Search for Neural Combinatorial Optimization?"
    result = qa.invoke(input={"input": query})

    result["answer"]
    references = [
        x.metadata["source"] + " page " + str(x.metadata["page"])
        for x in result["context"]
    ]

    """
    Simulation-guided Beam Search (SGBS) is a technique proposed for Neural Combinatorial Optimization (CO) that combines Monte Carlo Tree Search (MCTS) with beam search. The goal of SGBS is to enable neural CO methods to effectively search for high-quality solutions to CO problems.
    \n\nSGBS works by performing rollouts for nodes identified as promising by a neural network, which acts as a mechanism to correct any incorrect decisions made by the network. Only a select number of promising nodes identified by the rollouts are expanded, and this process is repeated. 
    \n\nThe implementation of SGBS is straightforward and requires minimal modification from existing neural CO algorithms. It maintains high throughput efficiency, characteristic of neural network-based sampling, as it does not involve complicated backpropagation that would hinder batch parallelization of the search.
    \n\nAdditionally, SGBS can be combined with efficient active search (EAS) to achieve even better performance over longer time spans. EAS updates a small subset of model parameters at test time to improve the quality of solutions backpropagated in SGBS, while SGBS enhances the quality of the policy used in EAS.
    \n\nThe experiments conducted with SGBS on various CO problem settings, such as the Traveling Salesman Problem (TSP), Capacitated Vehicle Routing Problem (CVRP), and Flexible Flow Shop Problem (FFSP), have shown promising results. 
    The combination of SGBS with EAS has reduced the gap between neural CO methods and state-of-the-art handcrafted heuristics, and in some cases, outperformed methods that were considered state-of-the-art just a few years ago.
    \n\nIn conclusion, SGBS provides a powerful search procedure for neural CO approaches, allowing them to find high-quality solutions efficiently. 
    The integration of SGBS with EAS further enhances performance by sharing information about finding solutions. Future work includes dynamically setting the parameters of SGBS and exploring deeper integration with EAS.
    """
