import streamlit as st

from zotgpt.app.utils import initialize

initialize()

db = st.session_state["metastore"]
df = db.read_database()

selected_columns = ["key", "title", "tags", "embedded"]
tags_exclude_notion = [x.pop(x.index("notion")) for x in df["tags"].tolist()]
df_show = df[selected_columns].copy()
df_show["tags"] = tags_exclude_notion

st.dataframe(df[selected_columns])
