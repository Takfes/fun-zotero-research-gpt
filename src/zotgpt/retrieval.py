from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


class VectorStoreManager:
    def __init__(self, store_type: str, embeddings: OpenAIEmbeddings):
        """
        Initialize the VectorStoreManager with the specified vector store type.

        :param store_type: Type of vector store ('chromadb' or 'pineconevectorstore').
        :param embeddings: Embedding function to use for the vector store.
        """
        self.store_type = store_type.lower()
        self.embeddings = embeddings
        self.vectorstore = self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize the appropriate vector store based on the store type."""
        if self.store_type == "chromadb":
            return Chroma(embedding_function=self.embeddings)
        elif self.store_type == "pineconevectorstore":
            return PineconeVectorStore(embedding_function=self.embeddings)
        else:
            raise ValueError(
                "Invalid store type. Choose 'chromadb' or 'pineconevectorstore'."
            )

    def retrieve_documents(self, query: str, filter: dict = None):
        """Retrieve documents based on a query and optional filter."""
        if filter:
            return self.vectorstore.similarity_search(query, filter=filter)
        return self.vectorstore.similarity_search(query)

    def create_qa_chain(self, retrieval_qa_chat_prompt: str):
        """Create a question-answering chain using a StuffDocumentsChain."""
        # Create the StuffDocumentsChain
        prompt_template = ChatPromptTemplate.from_template(
            retrieval_qa_chat_prompt
        )
        stuff_documents_chain = create_stuff_documents_chain(
            self.embeddings, prompt_template
        )

        # Create the retrieval chain
        qa_chain = create_retrieval_chain(
            retriever=self.vectorstore.as_retriever(),
            combine_docs_chain=stuff_documents_chain,
        )
        return qa_chain


# Example usage
if __name__ == "__main__":
    embeddings = OpenAIEmbeddings()  # Initialize your embeddings
    vector_store_manager = VectorStoreManager(
        store_type="chromadb", embeddings=embeddings
    )

    # Add documents
    documents = [
        Document(
            page_content="Document about AI.", metadata={"category": "AI"}
        ),
        Document(
            page_content="Document about Data Science.",
            metadata={"category": "Data Science"},
        ),
    ]
    vector_store_manager.add_documents(documents)

    # Retrieve documents
    retrieved_docs = vector_store_manager.retrieve_documents("What is AI?")
    print(retrieved_docs)

    # Create a QA chain
    retrieval_qa_chat_prompt = """Answer the following question based on the provided context:

<context>
{context}
</context>

Question: {input}"""
    qa_chain = vector_store_manager.create_qa_chain(retrieval_qa_chat_prompt)

    # Invoke the QA chain
    response = qa_chain.invoke({"input": "How does AI impact our daily lives?"})
    print(response)
