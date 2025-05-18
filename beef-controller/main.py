import streamlit as st
from streamlit import session_state as ss
import requests, os
from PIL import Image
from io import BytesIO
from utils.auth_utils import load_users


## Page config ##
st.set_page_config(page_title="Beef Stack", layout="wide")

#### Session state inicializations ####
if "show_logout_confirm" not in ss: # init logout process tracking
    ss.show_logout_confirm = False

if "backlog_message" not in ss: # init message that passes through page reload
    ss.backlog_message = ""

if "username" not in ss: # init login status tracking
    ss.username = ""

if "role" not in ss: # init role
    ss.role = ""

if "users_file_path" not in ss: # static path for our users data file
    ss.users_file_path = "data\\users.csv"

if "pages" not in ss:
    ss.pages = {}

#### Functions ####
@st.cache_data
def fetch_image(username): # get profile picture, uses mineatar.io and mojang public API
    try:
        response_uuid = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}?')
        response_uuid.raise_for_status() # throws HTTPError if response is error
        uuid = response_uuid.json()['id']
        response_image = requests.get(f"https://api.mineatar.io/face/{uuid}")
        response_image.raise_for_status()
        return Image.open(BytesIO(response_image.content))
    except Exception:
        return False # probably should implement troll face instead

def check_if_admin_exists():
    users = load_users(ss.users_file_path)
    return (True if (len(users) != 0) else False)


#### Pages ####
## Login/Authentication ##
login_page = st.Page("pages/login.py", title="Log in", icon=":material/login:")
ss.pages["login"] = login_page
register_page = st.Page("pages/register.py", title="Register", icon=":material/person_add:")
ss.pages["register"] = register_page
setup_page = st.Page("pages/setup.py", title="Setup", icon=":material/login:")

## Dashboard ##
dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)

## Admin only pages ##
admin_manage_user = st.Page("pages/admin_user.py", title="Users managment", icon=":material/group:")

#### Body ####
## Sidebar navigation ##
if ss.username != "":
    navigation = {
            "Dashboard": [dashboard],
            }
    if "Administrator" == ss.role:
        navigation["Administrator"] = [admin_manage_user]
    pg = st.navigation(navigation, expanded=False)
elif check_if_admin_exists():
    pg = st.navigation([login_page,register_page], position="hidden")
else:
    pg = st.navigation([setup_page], position="hidden")
    

## Sidebar logged in stuff ##
# Default logged in state
if ss.username != "" and ss.show_logout_confirm == False:
    col1, col2 = st.sidebar.columns([1,2])
    col1.write("Logged in as:")
    if fetch_image(ss.username):
        col2.image(fetch_image(ss.username), caption=ss.username)
    else:
        col2.text(ss.username)
    if col1.button("Logout"):
        ss.show_logout_confirm = True
        st.rerun()

# Logging out state
if ss.show_logout_confirm:
    st.sidebar.warning("Are you sure you want to logout?")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Yes"):
        ss.show_logout_confirm = False
        ss.username = ""
        ss.backlog_message = "Successfully logged out"
        st.rerun()
    if col2.button("Cancel"):
        ss.show_logout_confirm = False
        st.rerun()


#### "Main" ####
pg.run()