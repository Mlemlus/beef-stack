import streamlit as st
from streamlit import session_state as ss
import csv, pandas as pd
from utils.auth_utils import load_users

#### Admin check ####
if "Administrator" != ss.role:
    st.error("Unauthorized Access")
    st.stop()

#### Session state inicializations ####
if "delete_user_clicked_username" not in ss:
    ss.delete_user_clicked_username = ""

roles = ["Administrator", "User", "Guest"]

#### Functions ####
def updateUser(username):
    updated_users = []
    users = load_users(ss.users_file_path)
    # change the role for the edited user
    for u in users:
        if u["username"] != username:
            updated_users.append(u)
        else:
            u["role"] = ss[f"update_{username}"]
            updated_users.append(u)

    # overwrite the file with updated users
    with open(ss.users_file_path, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = ["username", "role", "salt", "password_hash"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_users)

    # refresh the delete state
    ss["delete_user_clicked_username"] = ""

def deleteUser():
    updated_users = []
    user_deleted = False

    # create a new array of non-deleted users
    with open(ss.users_file_path, "r", newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] != ss.delete_user_clicked_username:
                updated_users.append(row)
            else:
                user_deleted = True

    # overwrite the file with non-delted users
    with open(ss.users_file_path, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(updated_users)

    ss.backlog_message = ("User deleted!" if user_deleted else "User not found")
    ss["delete_user_clicked_username"] = ""


#### Body ####
## Backlog info message print ##
if ss.backlog_message != "":
    st.toast(ss.backlog_message)
    if ss.backlog_message == "User deleted!":
        st.balloons()
    ss.backlog_message = ""

## Header ##
st.write("# Admin User Managment")

## select users form ##
users = load_users(ss.users_file_path)
df = pd.DataFrame(users)


# List of users container
with st.container(height=600):
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.write("Username")
    col2.write("Role")
    for _ , row in df.iterrows(): # iterate throught entries
        user_self = row["username"] == ss.username # cant edit himself
        col1, col2, col3 = st.columns([2, 2, 1]) # columns for values and buttons
        col1.write(row["username"])
        col2.selectbox(
            "Role",
            options=roles,
            index=roles.index(row["role"]),
            label_visibility="collapsed",
            disabled=user_self,
            key=f"update_{row["username"]}",
            on_change=updateUser,
            kwargs={"username": row["username"]}
            )
        # Delete button logic
        if col3.button(label="Delete", key=f"delete_{row["username"]}", disabled=user_self): # needs unique key
            ss["delete_user_clicked_username"] = row["username"] # sets the username to be delete in dataframe
            st.rerun()
        # Delete row confirmation
        if ss["delete_user_clicked_username"] == row["username"]:
            if st.button(f"Confirm deletion of {row['username']}", disabled=user_self):
                deleteUser()
                st.rerun()