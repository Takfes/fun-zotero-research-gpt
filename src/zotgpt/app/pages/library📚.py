import pandas as pd
import streamlit as st

from zotgpt.app.utils import initialize


@st.cache_data
def load_data():
    db = st.session_state["metastore"]
    return db.read_database()


def dataframe_with_selections(
    df: pd.DataFrame, init_value: bool = False
) -> pd.DataFrame:
    # https://playground.streamlit.app/?q=df-with-selection
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", init_value)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(required=True)
        },
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop("Select", axis=1)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    st.write("Filter the dataframe by entering text in the box below.")
    filter_text = st.text_input(
        "Filter Dataframe", label_visibility="collapsed"
    )
    if filter_text:
        df = df[
            df.apply(
                lambda row: row.astype(str)
                .str.contains(filter_text, case=False)
                .any(),
                axis=1,
            )
        ]
        st.write(f"Filtered {len(df)} rows.")
    return df


def library():
    initialize()
    df = load_data()

    selected_columns = ["key", "embedded", "title", "tags"]
    df_show = df[selected_columns].copy()

    col1, col2, col3 = st.columns([16, 1, 6])
    with col1:
        current_selection = dataframe_with_selections(
            filter_dataframe(df_show)
        )["key"].tolist()

    with col3:
        st.write(f"{len(current_selection)} Candidate Items")
        st.write(current_selection)

        if st.button("Add Selected"):
            for x in current_selection:
                if x not in st.session_state["selected_keys"]:
                    st.session_state["selected_keys"].append(x)

    with st.expander(
        f"Show Selected ({len(st.session_state['selected_keys'])})"
    ):
        st.write(st.session_state["selected_keys"])
        if st.button("Clear Selection"):
            st.success("Selection Cleared")
            st.session_state["selected_keys"] = []
            # st.rerun()


if __name__ == "__main__":
    library()
