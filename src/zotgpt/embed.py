"""Module for managing different embedding models (OpenAI and Cohere)."""

import os

from dotenv import load_dotenv
from langchain.embeddings.base import Embeddings
from langchain_cohere import CohereEmbeddings
from langchain_openai import OpenAIEmbeddings


class EmbeddingsFactory:
    """Factory class for creating embedding model instances."""

    def __init__(self, embeddings_type: str, embeddings_model: str) -> None:
        """Initialize factory with embeddings type and model."""
        self.embeddings_type = embeddings_type
        self.embeddings_model = embeddings_model
        # Validate inputs immediately to fail fast
        self.validate_inputs()

    def __call__(self) -> Embeddings:
        """Create and return embeddings instance when called."""
        return self.create()

    def validate_inputs(self) -> None:
        """Validate embeddings type and model."""
        load_dotenv()
        valid_embeddings_types = ["openai", "cohere"]
        valid_embeddings_models = {
            "openai": ["text-embedding-ada-002", "text-embedding-3-small"],
            "cohere": ["embed-english-v3.0", "embed-english-light-v3.0"],
        }

        if self.embeddings_type not in valid_embeddings_types:
            raise ValueError(
                f"embeddings_type must be one of {valid_embeddings_types}"
            )

        if (
            self.embeddings_model
            not in valid_embeddings_models[self.embeddings_type]
        ):
            raise ValueError(
                f"Invalid model for {self.embeddings_type} embeddings. "
                f"Must be one of: {valid_embeddings_models[self.embeddings_type]}"
            )

        # Check for required environment variables
        required_env_var = f"{self.embeddings_type.upper()}_API_KEY"
        if not os.getenv(required_env_var):
            raise ValueError(
                f"Missing required environment variable: {required_env_var}"
            )

    @property
    def dimension(self) -> int:
        """Return the dimension of the embeddings based on the model."""
        dimensions = {
            "openai": {
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
            },
            "cohere": {
                "embed-english-v3.0": 1024,
                "embed-english-light-v3.0": 1024,
            },
        }
        return dimensions[self.embeddings_type][self.embeddings_model]

    def create(self) -> Embeddings:
        """Create and return the appropriate embeddings instance."""
        if self.embeddings_type == "openai":
            return OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model=self.embeddings_model,
            )

        elif self.embeddings_type == "cohere":
            return CohereEmbeddings(
                cohere_api_key=os.getenv("COHERE_API_KEY"),
                model=self.embeddings_model,
            )

        raise ValueError(f"Unsupported embeddings type: {self.embeddings_type}")
