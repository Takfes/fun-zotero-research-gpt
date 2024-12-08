import os

from dotenv import load_dotenv
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import (
    create_history_aware_retriever,
)
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI

load_dotenv()


def format_answer(result, wrap_text=True, unique_references=True):
    # Initialize response string
    response = ""
    # If wrap_text is True, wrap the answer to 80 characters
    if wrap_text:
        import textwrap

        response += textwrap.fill(
            result["answer"], width=80
        )  # Wrap text to 80 chars
    # Else -wrap_text is False- add answer directly if no wrapping
    else:
        response += result["answer"]
    # Extract references from context
    references = [
        "[" + x.metadata["title"]
        if x.metadata["title"]
        else ""
        + "]("
        + x.metadata["source"]
        + ") (p."
        + str(int(x.metadata["page"] + 1))
        + ")"
        for x in result["context"]
    ]
    # If unique_references is True
    if references:
        # Ensure references are unique
        if unique_references:
            references = list(set(references))
        # Add newline before references
        response += "\n\n"
    # Append each reference to response
    for idx, reference in enumerate(references, start=1):
        response += f"{idx}. {reference}\n"
    return response


class Retriever:
    def __init__(self, vector_store):
        self.llm = self.make_llm()
        self.vector_store = vector_store

    def make_llm(self):
        return ChatOpenAI(
            verbose=True, temperature=0.0, model=os.environ["LLM_MODEL"]
        )

    def retrieve(self, query, chat_history, k=5, ids=None):
        search_kwargs = {"k": k}
        if ids:
            search_kwargs["filter"] = {"id": {"$in": ids}}

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

        stuff_documents_chain = create_stuff_documents_chain(
            self.llm, retrieval_qa_chat_prompt
        )

        history_aware_retriever = create_history_aware_retriever(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(
                search_kwargs=search_kwargs
            ),
            prompt=rephrase_prompt,
        )

        retrieval_chain = create_retrieval_chain(
            retriever=history_aware_retriever,
            combine_docs_chain=stuff_documents_chain,
        )

        response = retrieval_chain.invoke(
            input={"input": query, "chat_history": chat_history}
        )
        return response
