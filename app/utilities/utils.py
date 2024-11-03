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
    if "A" in roommates and len(roommates) > 1:
        st.write("Error: only one initial is allowed when using A")
        return False
    for name in roommates:
        if name.upper() not in ["K", "M", "D", "L", "A"]:
            st.write("Error: Only initials K,M,D,L or A are allowed")
            return False
    return True


def handle_all_options(row, roommate_totals, split_amount):
    if "A" in row["Roommates"].upper() and len(row["Roommates"]) > 1:
        st.write("Error: only one initial is allowed when using A")
        return False
    elif "A" not in row["Roommates"].upper():
        return False
    roommates = ["K", "M", "D", "L"]
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
    roommate_totals = {"K": 0, "M": 0, "D": 0, "L": 0}

    for index, row in df.iterrows():
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

        if roommates.upper() == "A":
            num_roommates = 4
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
    total_total: int = 0
    for roommate, total in roommate_totals.items():
        total_total += total
    # Display the final amounts each roommate owes
    st.subheader("Amount each roommate owes:")
    for roommate, total in roommate_totals.items():
        if roommate.upper() == "K":
            name = "Koen"
        elif roommate.upper() == "M":
            name = "Matthias"
        elif roommate.upper() == "D":
            name = "Dries"
        elif roommate.upper() == "L":
            name = "Lucas"
        st.write(f"{name}: :blue-background[€{total:.2f}]")
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
