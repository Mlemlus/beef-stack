# beef-stack
<h3 align="center">Self hosted Minecraft server with Web Management and SMB Access</h3>

### Quick-start

> [!NOTE]  
> Needs Docker installed (or Docker Desktop for Windows and macOS)
> Also you have to download the actual minecraft server

1. Get a new Auth key from [Tailscale](https://tailscale.com/)
	1. Assign it a tag so it doesn't expire
2. Download the source files of the [latest release](https://github.com/Mlemlus/beef-stack/releases)
	1. Rename the `beef-stack` directory if you want to
3. Edit the hidden `.env` configuration file
5. In directory with `docker-compose.yaml` run command `docker compose up -d --build`
	1. Make sure docker is turned on
	2. Tailscale takes about a minute for the first build
6. After the build finishes the MC server and web will be accessible on IP from [Tailscale](https://tailscale.com/)
#### Giving access to another user
1. In [Tailscale](https://tailscale.com/) get a share link of the `minecraft` (or however you called it) machine
2. After the user accepts, they can copy the IP from [Tailscale](https://tailscale.com/) and with it access the web, server etc.
	1. They can create an account on the web, but the Administrator must give them a role to turn the server on and off
> [!TIP]
> Avoid giving more access than required
### Containers
- minecraft-server
   - it's a minecraft server
   - incredible
- minecraf-controller
  - WebUI to show logs and controll the server status
  - Includes some basic user management
- tailscale-minecraft
  - VPN for encrypted remote connection to the server
  - if it's a local connection it's still encrypted and routed locally
  - I love [Tailscale](https://tailscale.com/)
- minecraft-samba
  - remote access of the minecraft folder with Windows File Explorer (SMB)
