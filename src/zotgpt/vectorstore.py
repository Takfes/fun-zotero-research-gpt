"""Module for managing vector stores (Chroma and Pinecone) for document embeddings."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain.embeddings.base import Embeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from langchain_pinecone import PineconeVectorStore


class VectorStoreFactory:
    """Factory class for creating vector store instances."""

    def __init__(
        self,
        store_type: str,
        embeddings: Embeddings,
        collection_name: str,
        persist_directory: Optional[str] = None,
    ) -> None:
        """Initialize factory with store configuration."""
        self.store_type = store_type
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        # Validate inputs immediately to fail fast
        self.validate_inputs()

    def __call__(self) -> VectorStore:
        """Create and return vector store instance when called."""
        return self.create()

    def validate_inputs(self) -> None:
        """Validate initialization parameters and environment variables."""
        load_dotenv()

        valid_store_types = ["chroma", "pinecone"]
        if self.store_type not in valid_store_types:
            raise ValueError(f"store_type must be one of {valid_store_types}")

        if not self.collection_name:
            raise ValueError("collection_name must be provided")

        if self.store_type == "chroma":
            if not self.persist_directory:
                raise ValueError(
                    "persist_directory must be provided for Chroma"
                )

        elif self.store_type == "pinecone":
            if not os.getenv("PINECONE_API_KEY"):
                raise ValueError(
                    "Missing PINECONE_API_KEY environment variable"
                )

    def create(self) -> VectorStore:
        """Create and return the appropriate vector store instance."""
        if self.store_type == "chroma":
            path = Path(self.persist_directory)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {self.persist_directory}")

            return Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
            )

        elif self.store_type == "pinecone":
            from pinecone import Pinecone

            # Initialize Pinecone client
            pc = Pinecone(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT", "gcp-starter"),
            )

            # Get embedding dimension if available
            dimension = getattr(self.embeddings, "dimension", None)
            if (
                not dimension
                and self.collection_name not in pc.list_indexes().names()
            ):
                raise ValueError(
                    "Embedding dimension is required for creating new "
                    "Pinecone index. Use EmbeddingsFactory to create "
                    "embeddings with dimension info."
                )

            # Check if index exists, create if it doesn't
            if self.collection_name not in pc.list_indexes().names():
                print(f"Creating Pinecone index: {self.collection_name}")
                pc.create_index(
                    name=self.collection_name,
                    dimension=dimension,
                    metric="cosine",
                )
                print(f"Created Pinecone index: {self.collection_name}")
            else:
                print(f"Using existing Pinecone index: {self.collection_name}")

            return PineconeVectorStore(
                embedding=self.embeddings,
                index_name=self.collection_name,
            )

        raise ValueError(f"Unsupported store type: {self.store_type}")
