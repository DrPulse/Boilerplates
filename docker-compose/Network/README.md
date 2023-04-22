# Network

This stack must be detached from git if used in gitops mode because the network interface needs to be custom set and can't be passed as a variable yet.

## Pihole

- SERVER_ADDRESS is the ip address of the machine pihole is deployed on.
- PIHOLE_ADDRESS is the ip address you want to set for pihole. You better assign a static ip in your dhcp server.

For the network address attribution, replace the interface by what you have.
The watchtower label prevent the container from being updated. Remove it if needed. I prefer update it manually on major releases to not break it (already happened).

## Tailscale

Don't forget to go to [admin panel](https://login.tailscale.com/admin/machines) and activate the subnet routes in the route settings of the machine.
