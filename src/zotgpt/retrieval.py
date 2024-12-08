import os

from dotenv import load_dotenv
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI

load_dotenv()


def format_answer(result, unique_references=True):
    import textwrap

    wrapped_answer = textwrap.fill(result["answer"], width=80)
    references = [
        x.metadata["source"] + " page " + str(x.metadata["page"])
        for x in result["context"]
    ]
    if unique_references:
        references = list(set(references))
    print(wrapped_answer)
    for reference in references:
        print(reference)


class Retriever:
    def __init__(self, vector_store):
        self.llm = self.make_llm()
        self.retrieval_prompt = self.make_retrieval_prompt()
        self.vector_store = vector_store

    def make_llm(self):
        return ChatOpenAI(
            verbose=True, temperature=0.0, model=os.environ["LLM_MODEL"]
        )

    def make_retrieval_prompt(self):
        return hub.pull("langchain-ai/retrieval-qa-chat")

    def retrieve(self, query, k=5, ids=None):
        search_kwargs = {"k": k}
        if ids:
            search_kwargs["filter"] = {"id": {"$in": ids}}

        stuff_documents_chain = create_stuff_documents_chain(
            self.llm, self.retrieval_prompt
        )
        self.retrieval_chain = create_retrieval_chain(
            retriever=self.vector_store.as_retriever(
                search_kwargs=search_kwargs
            ),
            combine_docs_chain=stuff_documents_chain,
        )
        response = self.retrieval_chain.invoke(input={"input": query})
        return response
