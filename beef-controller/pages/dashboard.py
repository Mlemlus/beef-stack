import streamlit as st
from streamlit import session_state as ss
from mcstatus import JavaServer as mcjav
import docker, time, os
from datetime import timedelta

#### Permission check ####
if not ss.role or ss.role not in ["Administrator", "User", "Guest"]:
    st.error("Unauthorized Access")
    st.stop()


#### CONST ####
# Minecraft color and format codes
COLOR_CODES = {
    '0': '#000000', '1': '#0000AA', '2': '#00AA00', '3': '#00AAAA',
    '4': '#AA0000', '5': '#AA00AA', '6': '#FFAA00', '7': '#AAAAAA',
    '8': '#555555', '9': '#5555FF', 'a': '#55FF55', 'b': '#55FFFF',
    'c': '#FF5555', 'd': '#FF55FF', 'e': '#FFFF55', 'f': '#FFFFFF',
}

FORMAT_CODES = {
    'l': 'font-weight: bold;',
    'n': 'text-decoration: underline;',
    'o': 'font-style: italic;',
    'm': 'text-decoration: line-through;',
    'r': 'reset'
}

#### CONF ####
MINECRAFT_CONTAINER_NAME = os.getenv("CONTAINER_NAME") 
MINECRAFT_SERVER_HOST = "localhost"
MINECRAFT_SERVER_PORT = 25565
AUTO_REFRESH_INTERVAL = 30 # seconds

#### Session state inicializations ####
if "last_refresh_time" not in ss:
    ss.last_refresh_time = time.time()

#### Functions ####
def refresh_dashboard(): # get docker container, refresh elements
    container_status_str = get_container_status_string(client, MINECRAFT_CONTAINER_NAME)
    container_is_running = (container_status_str == "running")
    live_container = None # holds the container object
    col1,col2 = st.columns(2)

    # Container stats
    with col1:  
        st.subheader("Docker Container Control")
        st.caption(f"Managing container: `{MINECRAFT_CONTAINER_NAME}` | Querying server: `{MINECRAFT_SERVER_HOST}:{MINECRAFT_SERVER_PORT}`")
        st.metric("Container Status", container_status_str.capitalize())

        if container_status_str not in ["Not Found", "Docker client unavailable"] and \
           not container_status_str.startswith("API Error") and \
           not container_status_str.startswith("Error fetching status"):
            live_container = get_live_container_object(client, MINECRAFT_CONTAINER_NAME)

        if live_container:
            if container_is_running:
                if st.button("⏹️ Stop Container", type="primary", 
                             use_container_width=False, 
                             key="stop_button", 
                             disabled=(ss.role not in ["Administrator", "User"])):
                    with st.spinner(f"Stopping {MINECRAFT_CONTAINER_NAME}..."):
                        try:
                            live_container.stop()
                            st.toast(f"Container {MINECRAFT_CONTAINER_NAME} stopping.", icon="🛑")
                            time.sleep(1)
                            get_container_status_string.clear() # force re-fetch status
                            st.rerun()
                        except docker.errors.APIError as e:
                            st.error(f"Error stopping container: {e}")
            else: # Container is not running (exited/created ...)
                if st.button("▶️ Start Container", type="primary", 
                             use_container_width=False, 
                             key="start_button",
                             disabled=(ss.role not in ["Administrator", "User"])):
                    with st.spinner(f"Starting {MINECRAFT_CONTAINER_NAME}..."):
                        try:
                            live_container.start()
                            st.toast(f"Container {MINECRAFT_CONTAINER_NAME} starting.", icon="🚀")
                            time.sleep(3)
                            get_container_status_string.clear() # force re-fetch status
                            st.rerun()
                        except docker.errors.APIError as e:
                            st.error(f"Error starting container: {e}")
        elif container_status_str == "Not Found": # wrong container name
             st.error(f"Container '{MINECRAFT_CONTAINER_NAME}' not found.")
        elif container_status_str == "Docker client unavailable":
            # error already shown by get_docker_client
            pass
        else: # other error states from get_container_status_string
            st.error(f"Container Status: {container_status_str}")


    # Server stats
    with col2:
        st.subheader("Server Statistics")
        mc_status = get_minecraft_server_status(MINECRAFT_SERVER_HOST, MINECRAFT_SERVER_PORT, container_is_running)

        if mc_status["online"]:
            st.success("Server is Online!")
            cols_stats = st.columns(3)
            cols_stats[0].metric("Players", f"{mc_status['players_online']}/{mc_status['players_max']}")
            cols_stats[1].metric("Version", mc_status['version'])
            cols_stats[2].metric("Latency", f"{mc_status['latency']:.2f} ms")
            motd_display = mc_status['motd']
            if isinstance(motd_display, dict) and 'text' in motd_display:
                motd_display = motd_display['text']
            elif isinstance(motd_display, dict) and 'extra' in motd_display:
                 motd_display = "".join([item['text'] for item in motd_display['extra'] if 'text' in item])
            st.markdown(parse_motd(str(motd_display).strip()), unsafe_allow_html=True)
        elif container_is_running:
            st.warning(f"Server appears Offline. Reason: {mc_status.get('error', 'Unknown')}")
        else:
            st.error("Server is Offline (Container is not running).")
    
    # Logs
    if live_container:
        lines = st.slider("Lines of Logs to display", min_value=0, max_value=500, value=20)
        logs = live_container.logs(stdout=True, tail=lines, timestamps=False).decode("utf-8")
        st.code(logs, language="log")


@st.cache_resource # Cache the Docker client
def get_docker_client():
    try:
        client = docker.from_env()
        client.ping() # Test connection
        return client
    except docker.errors.DockerException:
        st.error("🚨 Could not connect to Docker. Is the Docker daemon running and docker.sock accessible?")
        st.stop()
        return None # Should not be reached due to st.stop()

@st.cache_data(ttl=10) # Cache container status string for 10 seconds
def get_container_status_string(_client, container_name: str) -> str:
    """Gets the status string of the specified container."""
    if not _client:
        return "Docker client unavailable"
    try:
        container = _client.containers.get(container_name)
        return container.status  # This is a string, so it's picklable
    except docker.errors.NotFound:
        return "Not Found"
    except docker.errors.APIError as e:
        return f"API Error: {e}"
    except Exception as e: # Catch any other unexpected error during status fetch
        return f"Error fetching status: {e}"

def get_live_container_object(_client, container_name: str):
    if not _client:
        return None
    try:
        return _client.containers.get(container_name)
    except docker.errors.NotFound:
        return None # Handled by status string check mostly
    except docker.errors.APIError:
        return None # Handled by status string check

@st.cache_data(ttl=5) # Cache Minecraft status for 5 seconds
def get_minecraft_server_status(host, port, container_is_running):
    """Queries the Minecraft server for its status."""
    if not container_is_running:
        return {"online": False, "error": "Container not running"}

    try:
        server = mcjav.lookup(f"{host}:{port}")
        status = server.status()
        return {
            "online": True,
            "version": status.version.name,
            "motd": status.description, # mcstatus uses 'description' for MOTD
            "players_online": status.players.online,
            "players_max": status.players.max,
            "latency": status.latency
        }
    except ConnectionRefusedError:
        return {"online": False, "error": "Connection refused (server likely starting)"}
    except Exception as e: # Catch other mcstatus or socket errors
        return {"online": False, "error": f"Query error: {str(e)}"}

def parse_motd(motd):
    output = ""
    i = 0
    style = ""

    while i < len(motd):
        if motd[i] == '§' and i + 1 < len(motd):
            code = motd[i + 1].lower()

            if code == 'r':
                style = ""
            elif code in COLOR_CODES:
                style = f"color: {COLOR_CODES[code]};"
            elif code in FORMAT_CODES:
                style += FORMAT_CODES[code]

            i += 2
        else:
            # Escape HTML special characters
            char = motd[i].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            output += f'<span style="{style}">{char}</span>'
            i += 1

    return output

# Initialize Docker client
client = get_docker_client()
#### Body ####
# Initial call to display everything
refresh_dashboard()

st.sidebar.markdown("---")
cols = st.sidebar.columns(2)
if cols[0].button("🔄 Manual Refresh"):
    # Clear caches for immediate rerun
    get_container_status_string.clear()
    get_minecraft_server_status.clear()
    st.rerun()
if cols[1].button("🛑 Stop Refreshing"):
    st.stop()

# refresh logic
refresh_time = st.sidebar.empty()
refresh_time_interval = st.sidebar.slider("Auto-refresh interval", 
                                          value=AUTO_REFRESH_INTERVAL,
                                          step=30,
                                          min_value=30,
                                          max_value=600, 
                                          format="%ds")

for remaining in range(refresh_time_interval, 0, -5):
    refresh_time.text(f"Refreshing in {remaining} seconds…")
    time.sleep(5)
get_container_status_string.clear()
get_minecraft_server_status.clear()
st.rerun()