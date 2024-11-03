from time import strftime
import os
import numpy as np
import streamlit as st
import pandas as pd


def save_grocery_list(df: pd.DataFrame):
    timestamp = strftime("%Y_%m_%d_%H_%M_%S")
    df.to_csv(f"app/data/grocery_list_{timestamp}.csv")


def check_names(roommates):
    # check it only contains a,k,l,m or d
    if roommates is None:
        return False
    if "G" in roommates and len(roommates) > 1:
        st.write("Error: only one initial is allowed when using G")
        return False
    for name in roommates:
        if name.upper() not in ["A", "M", "J", "G"]:
            st.write("Error: Only initials A,M,J or G are allowed")
            return False
    return True


def handle_all_options(row, roommate_totals, split_amount):
    if "G" in row["Roommates"].upper() and len(row["Roommates"]) > 1:
        st.write("Error: only one initial is allowed when using G")
        return False
    elif "G" not in row["Roommates"].upper():
        return False
    roommates = ["A", "M", "J"]
    for roommate in roommates:
        if roommate in roommate_totals:
            roommate_totals[roommate] += split_amount
        else:
            roommate_totals[roommate] = split_amount
    return roommate_totals


def file_selector(folder_path="app/data"):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox(
        "Select a file",
        filenames,
        index=None,
        placeholder="None",
        label_visibility="collapsed",
        key="filename",
    )
    if not selected_filename:
        return None
    return os.path.join(folder_path, selected_filename)


def calculate_split(df: pd.DataFrame, excl_vat: bool):
    roommate_totals = {"A": 0, "M": 0, "J": 0}

    for _, row in df.iterrows():
        roommates = row["Roommates"]
        if not check_names(roommates):
            break
        roommates = roommates.upper().strip()
        if excl_vat:
            if row["VAT Code"].upper() == "A":
                vat = 1.06
            elif row["VAT Code"].upper() == "C":
                vat = 1.21
            else:
                st.write("Warning: Invalid VAT number")
                break
        else:
            vat = 1

        if roommates.upper() == "G":
            num_roommates = 3
        elif len(roommates) == 0:
            num_roommates = 1
        else:
            num_roommates = len(roommates)
        split_amount = (row["Price"] * vat) / num_roommates

        if not handle_all_options(row, roommate_totals, split_amount):
            for roommate in roommates:
                if roommate in roommate_totals:
                    roommate_totals[roommate] += split_amount
    return roommate_totals


def write_split(roommate_totals):
    # Display the final amounts each roommate owes
    st.subheader("Amount each roommate owes:")
    total_total: int = 0
    for roommate, total in roommate_totals.items():
        if roommate.upper() == "A":
            name = "Alec"
        elif roommate.upper() == "J":
            name = "Jules (J)"
        elif roommate.upper() == "M":
            name = "Jonathan (M)"
        st.write(f"{name}: :blue-background[€{total:.2f}]")
        total_total += total
    st.write("---")

    st.write(f"total amount: :blue-background[€{total_total:.2f}]")


def read_grocery_list(filename):
    df = pd.read_csv(
        filename,
        # index_col=0,
    )
    df.drop("Unnamed: 0", axis=1, inplace=True)
    df = df.replace({np.nan: None})
    return df
