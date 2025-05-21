import streamlit as st
from streamlit import session_state as ss
from utils.auth_utils import add_user

#### Functions ####
def register(username, password):
    username_free = False
    if (len(username) > 2 and len(password) > 7): 
        username_free = add_user(username, password, "Guest", ss.users_file_path)
        if username_free:
            ss.backlog_message = "User successfully added."
            st.switch_page(ss.pages["login"])
        else:
            ss.backlog_message = "User already exists."
    else:
        ss.backlog_message = "Username or Password too short."

#### Body ####
## Backlog info message print ###
if ss.backlog_message != "":
    st.toast(ss.backlog_message)
    ss.backlog_message = ""

## Header ##
st.write("# Register")

### register form ####
with st.form("register_form"):
    username = st.text_input("Username", max_chars=50, help="Minimal length of 3 characters")
    password = st.text_input("Password", type="password", max_chars=100, help="Minimal length of 8 characters")
    submit = st.form_submit_button("Register")
    if submit:
        register(username, password)
        st.rerun()
st.page_link(page=ss.pages["login"], label="Login",icon=":material/login:")