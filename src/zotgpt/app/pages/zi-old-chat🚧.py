import os

import streamlit as st
from streamlit_chat import message

from zotgpt.embed import EmbeddingsFactory
from zotgpt.retrieval import Retriever, format_answer
from zotgpt.storage import VectorStoreFactory

ef = EmbeddingsFactory(
    embeddings_type=os.environ["EMBEDDINGS_TYPE"],
    embeddings_model=os.environ["EMBEDDINGS_MODEL"],
)

embeddings = ef.create()

vsf = VectorStoreFactory(
    embeddings=embeddings,
    store_type=os.environ["VECTOR_STORE_TYPE"],
    collection_name=os.environ["VECTOR_STORE_INDEX"],
)
vs = vsf.create()
r = Retriever(vector_store=vs)

# Initialize session state
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []

# Create two columns for a more modern layout
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_input("Prompt", placeholder="Enter your message here...")
    # prompt = st.chat_input(placeholder="Enter your message here...")

with col2:
    if st.button("Submit", key="submit"):
        prompt = prompt or "Hello"

if prompt:
    with st.spinner("Generating response..."):
        response = r.retrieve(
            query=prompt, chat_history=st.session_state["chat_history"]
        )
        formatted_response = format_answer(response, wrap_text=False)

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append((
            "ai",
            response["answer"],
        ))

# Display chat history
if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"],
    ):
        message(user_query, is_user=True, key=f"user_{user_query}")
        message(generated_response, key=f"bot_{generated_response}")

# Add a footer
st.markdown("---")
st.markdown("Powered by LangChain and Streamlit")
