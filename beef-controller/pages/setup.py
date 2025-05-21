import streamlit as st
from streamlit import session_state as ss
from utils.auth_utils import add_user, load_users

### Permission check ###
if len(load_users(ss.users_file_path)) != 0:
    st.error("Unauthorized Access")
    st.stop()

#### Functions ####
def register(username, password):
    if len(username) > 2 and len(password) > 7: 
        add_user(username, password, "Administrator", ss.users_file_path)
    else:
        ss.backlog_message = "Username or Password too short."

#### Body ####
## Backlog info message print ###
if ss.backlog_message != "":
    st.toast(ss.backlog_message)
    ss.backlog_message = ""

## Header ##
st.write("# Welcome to Beef Stack!")
st.write("### Please register the Administrator account")
st.write("The Username should be the same as your minecraft username")
### register form ####
with st.form("register_form"):
    username = st.text_input("Username", max_chars=50)
    password = st.text_input("Password", type="password", max_chars=100)
    submit = st.form_submit_button("Register")
    if submit:
        register(username, password)
        st.rerun()
