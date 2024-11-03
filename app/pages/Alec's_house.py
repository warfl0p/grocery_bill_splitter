import streamlit as st
import pandas as pd
from utilities.utils_alec import (
    calculate_split,
    write_split,
    save_grocery_list,
    read_grocery_list,
    file_selector,
)


def main():
    # Title for the app
    st.title("Roommate Bill Splitter")
    col1, col2 = st.columns([1, 5])
    with col2:
        st.write(
            """
                <p style="font-size: smaller; color: #D3D3D3; font-style: italic; padding-bottom: 0px;">
                Select a file
                </p>
            """,
            unsafe_allow_html=True,
        )
    col1, col2 = st.columns([1, 5])

    with col1:
        if st.button("Clear data"):
            initial_data = {"VAT Code": ["A"], "Price": [0.00], "Roommates": [None]}
            df = pd.DataFrame(initial_data)
            st.session_state.dataframe = df
            st.session_state.filename = None

    with col2:
        # File selection to load a saved grocery list
        filename = file_selector()

    if filename is not None:
        df = read_grocery_list(filename)
        st.session_state.dataframe = df
        if "VAT Code" in df.columns:
            st.session_state.vat_bool = True
            st.session_state.vat_required = True

    st.write("---")
    if "dataframe" not in st.session_state:
        # Sample data for initialization if no file is selected
        initial_data = {"VAT Code": ["A"], "Price": [0.00], "Roommates": [None]}
        df = pd.DataFrame(initial_data)
        st.session_state.dataframe = df
        st.session_state.vat_required = False
    else:
        df = st.session_state.dataframe

    def check_drop():
        global df
        df = st.session_state.dataframe
        if "vat_bool" in st.session_state:
            if "VAT Code" in df.columns and st.session_state.vat_bool:
                df.drop("VAT Code", axis=1, inplace=True)

    vat_code = st.checkbox("prices excluding VAT", key="vat_bool", on_change=check_drop)

    if not vat_code and "VAT Code" in df.columns:
        df.drop("VAT Code", axis=1, inplace=True)
    if vat_code and "VAT Code" not in df.columns:
        df.insert(0, "VAT Code", "")
        df["VAT Code"] = "A"

    # Display editable table
    df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Price": st.column_config.NumberColumn(
                "Price (€)",
                help="The price of the product in USD",
                min_value=0,
                step=0.01,
                format="%.2f",
                required=True,
            ),
            "Roommates": st.column_config.TextColumn(
                "Roommates",
                help="Write G for everyone, or the initials of the roommates",
                default="G",
                validate=r"^([gG]|[aAjJmM]*)$",
                required=True,
            ),
            "VAT Code": st.column_config.TextColumn(
                "VAT Code",
                help="A or C",
                default="A",
                max_chars=1,
                validate=r"^[acAC]$",
                required=True,
            ),
        },
    )
    roommate_totals = calculate_split(df, vat_code)
    write_split(roommate_totals)
    if st.button("Save Grocery List"):
        save_grocery_list(df)
        st.rerun()
        st.rerun()


if __name__ == "__main__":
    main()
