import streamlit as st
from streamlit import session_state as ss
from utils.auth_utils import load_users, authenticate

#### Functions ####
def login(username: str, password: str):
    users = load_users(ss.users_file_path)
    # check if the credentials are incorrect
    auth_data = authenticate(username, password, users)
    if not auth_data["auth"]:
        ss.backlog_message ="Email or password is not valid."
        return # reload page
    # load permissions
    ss.username = auth_data["username"]
    ss.role = auth_data["role"]


#### Body ####
## Backlog info message print ###
if ss.backlog_message != "":
    st.toast(ss.backlog_message)
    ss.backlog_message = ""

## Header ##
st.write("# Login")
st.write("> Please log in to continue")

## login form ####
with st.form("login_form"):
    username = st.text_input("Username", max_chars=50)
    password = st.text_input("Password", type="password", max_chars=100)
    submit = st.form_submit_button("Login")
    if submit:
        login(username, password)
        st.rerun()
st.page_link(page=ss.pages["register"], label="Register", icon=":material/person_add:")