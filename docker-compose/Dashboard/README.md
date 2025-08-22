# Dashboard

Dockerproxy is needed to safely pass the docker socket to homepage. The port can be changed as it's the default port for proxies. If the port is changed, use it in the homepage config.

The environment variable COMPOSE_PROFILES controls which dashboard is used. You have the option to use a unique one (ex: `homepage` for homepage), multiple unique ones (`homepage, dashy` for two of them) or all of them using `full`.

## Homepage

Check [the configuration documentation](https://gethomepage.dev) to set docker host, settings...
