import streamlit as st

st.title("Info")

st.markdown(
    """
    In the `Roommate` column, the values can be `K`, `M`, `D`, `L`, or `A`, representing Koen, Matthias, Dries, Lucas, or `All` respectively.
    If the purchase is relevant to everyone, just enter `A`.
    For individual or multiple roommates, list their initials (in any order, case-insensitive).
    """
)
