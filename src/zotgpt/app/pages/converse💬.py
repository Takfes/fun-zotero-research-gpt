import os

import streamlit as st

from zotgpt.app.utils import initialize_embeddings_and_vector_store
from zotgpt.retrieval import Retriever, format_answer

# # Initialize embeddings and vector store only once
initialize_embeddings_and_vector_store()

# Initialize session state for chat history and components
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []

# Initialize retriever with stored vector store
r = Retriever(vector_store=st.session_state["vector_store"])

# Display chat history
for user_msg, ai_msg in zip(
    st.session_state["user_prompt_history"],
    st.session_state["chat_answers_history"],
):
    with st.chat_message("user"):
        st.write(user_msg)
    with st.chat_message("assistant"):
        st.write(ai_msg)

# Chat input
if prompt := st.chat_input("What would you like to know about your research?"):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"), st.spinner("Thinking..."):
        response = r.retrieve(
            query=prompt, chat_history=st.session_state["chat_history"]
        )
        formatted_response = format_answer(response, wrap_text=False)
        st.write(formatted_response)

    # Update session state
    st.session_state["user_prompt_history"].append(prompt)
    st.session_state["chat_answers_history"].append(formatted_response)
    st.session_state["chat_history"].append(("human", prompt))
    st.session_state["chat_history"].append(("ai", response["answer"]))

# Add a footer
st.markdown("---")
st.markdown("Powered by LangChain and Streamlit")
