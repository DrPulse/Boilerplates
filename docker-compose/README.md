# Docker composes

Sets of containers ready to be deployed natively is docker-compose, in stacks portainer / yacht or in gitops mode.
Additional config may be needed for some containers. Details are in each stack folder.

## Usage

### Deployement informations

Made for deploying the other stacks from portainer / docker-compose with environment variables.
The default credentials, account creation commands, required files etc, will be referenced inside each stack directory.

By default, a stack will be configured to use traefik as the reverse proxy, using the docker network called proxy. The ports will still be commented, in case a reverse proxy is not needed. Be careful, the ports are the defaults ones and some containers use commons ports like 8080, so change them to not used ones. If not running through traefik, the network field can be changed/deleted to fit your needs.

I use 2 mounting points, one for the container data/config and one for common files to be shared everywhere (movies, shows...), but docker volumes or single mount point would work aswell. some containers can't work without a docker volume though, so make sure to backup the docker volumes.

Environment variables are needed for the stacks, either by loading them or referencing a file. A .env-exemple is inside each stack directory, ready to be filled.  

### Dashboard

Homepage is my dashboard for now and the Automatic Service Discovery is used here to add the services in my dashboard. Remove the homepage label if you don't need it.

## Services

- [Core](Core)
  - Dockerproxy
  - Portainer
  - Watchtower
- [Dashboards](Dashboard)
  - Dashy  
  - Homepage
- [Development](Development)
  - Code-server
  - Semaphore
- [Documents](Documents)
  - Drawio
  - Excalidraw
  - Nextcloud
  - Onlyoffice
  - Paperless
  - Wikijs
- [Games](Games)
  - Minecraft server
- [Media](Media)
  - Bazarr
  - Deluge
  - Flaresolverr
  - Flemarr
  - Jellyfin
  - Jellyseerr
  - Ombi
  - Overseerr
  - Plex
  - Prowlarr
  - Radarr
  - Requestrr
  - Sonarr
  - Wizarr
- [Monitoring](Monitoring)
  - Dozzle
  - Netdata
  - Nutify
  - Scrutiny
  - Speedtest
  - Uptime-kuma
- [Network](Network)
  - Pihole
  - Tailscale
- [Reverse proxy](ReverseProxy)
  - Traefik
- [Tools](Tools)
  - Blaze
  - Focalboard
  - Homebox
  - It-tools
  - Mealie
  - Pairdrop
  - Stirling pdf
  - Wallos

## Coming Soon

- Crowdsec
- Organize
