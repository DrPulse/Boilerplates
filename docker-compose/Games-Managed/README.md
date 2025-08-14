# Games Managed

## Logging in / Accounts

- Panel:
    exec in container to create the first user: `php artisan p:user:make --email=admin@domain.com --username=admin --name-first=admin --name-last=user --password=admin --admin=1 --no-password`

## Node management

- Create node
- Copy the given config in settings page
- Enrich it with what's in [the config example file](config-example.yml)
- Place it in the folder mounted in wings container at : `/etc/pterodactyl/`
- Restart the wings container
