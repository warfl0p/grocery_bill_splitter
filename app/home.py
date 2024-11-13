import streamlit as st
import pandas as pd
from utilities.utils import calculate_split, write_split


def main():
    # Title for the app
    st.title("Roommate Bill Splitter")
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
                help="Write A for everyone, or the initials of the roommates",
                default="A",
                validate=r"^([aA]|[kldmKLDM]*)$",
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


if __name__ == "__main__":
    main()
