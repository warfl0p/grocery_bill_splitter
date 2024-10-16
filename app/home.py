import streamlit as st
import pandas as pd
from time import strftime
import os
import numpy as np


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


def handle_all_option(row, roommate_totals, split_amount):
    if "A" in row["Roommates"] and len(row["Roommates"]) > 1:
        st.write("Error: only one initial is allowed when using A")
        return False
    elif "A" not in row["Roommates"]:
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
    selected_filename = st.selectbox("Select a file", filenames, index=None, placeholder="None")
    if not selected_filename:
        return None
    return os.path.join(folder_path, selected_filename)


# Title for the app
st.title("Roommate Bill Splitter")

# File selection to load a saved grocery list
filename = file_selector()

if filename is not None:
    df = pd.read_csv(
        filename,
        # index_col=0,
    )
    df.drop("Unnamed: 0", axis=1, inplace=True)
    df = df.replace({np.nan: None})

else:
    # Sample data for initialization if no file is selected
    initial_data = {"VAT Code": ["A"], "Price": [0], "Roommates": [None]}
    df = pd.DataFrame(initial_data)
print(df.columns)
excl_vat = st.checkbox("prices excluding VAT", value=True)
if not excl_vat and "VAT Code" in df.columns:
    df.drop("VAT Code", axis=1, inplace=True)

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

roommate_totals = {"K": 0, "M": 0, "D": 0, "L": 0}

for index, row in df.iterrows():
    roommates = row["Roommates"]
    if not check_names(roommates):
        break
    roommates = roommates.upper().strip()
    if excl_vat:
        if row["VAT Code"].upper() == "A":
            vat = 1.21
        elif row["VAT Code"].upper() == "C":
            vat = 1.06
        else:
            st.write("Warning: Invalid VAT number")
            break
    else:
        vat = 1

    if roommates == "A":
        num_roommates = 4
    elif len(roommates) == 0:
        num_roommates = 1
    else:
        num_roommates = len(roommates)
    split_amount = row["Price"] * vat / num_roommates

    if not handle_all_option(row, roommate_totals, split_amount):
        for roommate in roommates:
            if roommate in roommate_totals:
                roommate_totals[roommate] += split_amount

# Display the final amounts each roommate owes
st.subheader("Amounts each roommate owes:")
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

if st.button("Save Grocery List"):
    save_grocery_list(df)