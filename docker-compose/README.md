# Docker composes

Sets of containers ready to be deployed natively in docker-compose, in stacks komodo in gitops mode.
Some tweaking is needed to make it ready for portainer / docker compose standard stacks like removing use of komodo variables / secrets
Additional config may be needed for some containers. Details are in each stack folder.

## Usage

### Deployement informations

Made for deploying the other stacks from komodo with environment variables.
The default credentials, account creation commands, required files etc, will be referenced inside each stack directory.

By default, a stack will be configured to use godoxy as the reverse proxy, running in host mode. Traefik is also in the compose file if prefered.

I use 2 mounting points, one for the container data/config and one for common files to be shared everywhere (movies, shows...), but docker volumes or single mount point would work aswell. Some containers can't work without a docker volume though, so make sure to backup the docker volumes.

Environment variables are needed for the stacks, either by loading them or referencing a file. A .env-exemple is inside each stack directory, ready to be filled. Some variables are set at komodo level, using its interpolation with [[VAR]] in the **environment variables** like so: `MYVAR=[[VAR]]` where `VAR` is set in komodo variable / secret with a given a value, and MYVAR is the environment variable in the compose file, written like so : `${MYVAR}`

### Dashboard

Homepage is my dashboard for now and the Automatic Service Discovery is used here to add the services in my dashboard. Remove the homepage label if you don't need it.

## Services

- [Core](Core)
  - Komodo
- [Dashboard](Dashboard)
  - Homepage
- [Development](Development)
  - Code-server
  - Semaphore
- [Documents](Documents)
  - Immich
  - Paperless-NGX
  - Syncthing
  - Wiki.js
- [Games-Managed](Games-Managed)
  - Pterodactyl
- [Games-Standalone](Games-Standalone)
  - Satisfactory
- [Home](Home)
  - Home Assistant
  - Homebox
  - LubeLogger
- [Infrastructure](Infrastructure)
  - Autoheal
  - Docker Socket Proxy
- [Media](Media)
  - Bazarr
  - Calibre-web-automated
  - Cleanuparr
  - Deluge
  - FlareSolverr
  - Huntarr
  - Jellyfin
  - Jellyseerr
  - Overseerr
  - Plex
  - Prowlarr
  - Radarr
  - Shelfmark
  - Sonarr
  - Wizarr
- [Monitoring](Monitoring)
  - Beszel
  - Dozzle
  - Nutify
  - Scrutiny
  - Speedtest Tracker
  - Uptime Kuma
- [Network](Network)
  - AdGuard Home
  - DockFlare
  - Gluetun
  - Tailscale
- [Reverse-Proxy](Reverse-Proxy)
  - Godoxy
- [Tools](Tools)
  - BentoPDF
  - DumbAssets
  - DumbTerm
  - IT-Tools
  - Omni-Tools
  - PairDrop
  - Reactive Resume
  - Termix
  - Wallos
