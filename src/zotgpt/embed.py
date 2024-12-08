import os

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings


class Embeddings:
    def __init__(self, embeddings_type, embeddings_model):
        self.embeddings_type = embeddings_type
        self.embeddings_model = embeddings_model
        self.validate_inputs()
        self.embeddings = self.initialize_embeddings()

    def __call__(self):
        return self.get_embeddings()

    def validate_inputs(self):
        valid_empeddigns_types = ["openai", "cohere"]
        valid_embbdings_models = {
            "openai": ["text-embedding-ada-002", "text-embedding-3-small"],
            "cohere": ["embed-english-v3.0", "embed-english-light-v3.0"],
        }

        if self.embeddings_type not in valid_empeddigns_types:
            raise ValueError(
                f"embeddings_type must be one of {valid_empeddigns_types}"
            )

        if (
            self.embeddings_type == "openai"
            and self.embeddings_model
            not in valid_embbdings_models.get(self.embeddings_type)
        ):
            raise ValueError(
                f"Invalid model for {self.embeddings_type} embeddings. Must be one of : {valid_embbdings_models.get(self.embeddings_type)}"
            )

        if self.embeddings_type == "cohere" and self.embeddings_model not in [
            "embed-english-v3.0",
            "embed-english-light-v3.0",
        ]:
            raise ValueError(
                f"Invalid model for {self.embeddings_type} embeddings. Must be one of : {valid_embbdings_models.get(self.embeddings_type)}"
            )

    def get_embeddings(self):
        return self.embeddings

    def initialize_embeddings(self):
        load_dotenv()

        if self.embeddings_type == "openai":
            return OpenAIEmbeddings(
                openai_api_key=os.environ["OPENAI_API_KEY"],
                model=self.embeddings_model,
            )
        elif self.embeddings_type == "cohere":
            return CohereEmbeddings(
                cohere_api_key=os.environ["COHERE_API_KEY"],
                model=self.embeddings_model,
            )
