# Network

This stack needs some tweaking, because I use a mcvlan network, to run adguard or pihole on the same host than a NAS or similar appliance.

- LOCAL_DNS_ADDRESS is the ip address you want to set for the local DNS.
- SERVER_ADDRESS is the ip address of the machine pihole is deployed on.

For the network address attribution, replace the interface by what you have. Or moreve it if a mcvlan is not needed in your serup.

The komodo label prevent the container from being updated. Remove it if needed. I prefer update it manually on major releases to not break it (already happened).

## Adguard

Go to the web ui, complete the wizerd setup, and add the local DNS settings with wildcard subdomain pointing to the reverse proxy host.

## Pihole

Subdomains must be written one by one, have fun :D

## Gluetun

Retrieves the necessary credentials from your VPN provider to configure the VPN connection.

## Tailscale

Don't forget to go to [admin panel](https://login.tailscale.com/admin/machines) and activate the subnet routes in the route settings of the machine.
