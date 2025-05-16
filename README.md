# beef-stack
Docker compose for minecraft server with a python frontend for managing it
### Containers
- minecraft-server
    - it's a minecraft server
    - incredible
- tailscale-minecraft   
    - VPN for encrypted remote connection to the server
    - if it's a local connection it's still encrypted and routed locally
    - I love Tailscale
- minecraft-samba
    - remote access of the minecraft folder with Windows File Explorer (SMB)