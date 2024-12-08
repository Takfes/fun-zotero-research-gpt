"""Module for managing vector stores (Chroma and Pinecone) for document embeddings."""

import os
from pathlib import Path
from typing import Optional, Union

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain_chroma import Chroma
from langchain_pinecone import Pinecone, PineconeVectorStore


class VectorDB:
    """Class for initializing and managing Chroma or Pinecone vector stores."""

    def __init__(
        self,
        store_type: str,
        documents: list[Document],
        embeddings: Embeddings,
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize vector store with documents and embeddings."""
        self.store_type = store_type
        self.documents = documents
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.validate_inputs()
        self.vector_store = self.initialize_vector_store()

    def __call__(self) -> Union[Chroma, PineconeVectorStore]:
        """Return the initialized vector store instance."""
        return self.get_vector_store()

    def validate_inputs(self) -> None:
        """Validate initialization parameters and environment variables."""
        valid_store_types = ["chroma", "pinecone"]

        if self.store_type not in valid_store_types:
            raise ValueError(f"store_type must be one of {valid_store_types}")

        if self.store_type == "chroma" and not self.persist_directory:
            raise ValueError(
                "persist_directory must be provided for Chroma vector store"
            )

        if self.store_type == "pinecone":
            required_env_vars = ["PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
            missing_vars = [
                var for var in required_env_vars if not os.getenv(var)
            ]
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables: {missing_vars}"
                )

    def get_vector_store(self) -> Union[Chroma, PineconeVectorStore]:
        """Return the vector store instance."""
        return self.vector_store

    def initialize_vector_store(self) -> Union[Chroma, PineconeVectorStore]:
        """Initialize and return either Chroma or Pinecone vector store."""
        if self.store_type == "chroma":
            # Ensure the persist directory exists
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            return Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

        elif self.store_type == "pinecone":
            return PineconeVectorStore(
                embedding=self.embeddings,
                index_name=os.getenv("PINECONE_INDEX_NAME"),
            )

        raise ValueError(f"Unsupported store type: {self.store_type}")
