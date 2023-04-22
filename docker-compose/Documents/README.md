# Documents

## Logging in / Accounts

- Nextcloud :
  - Create an admin account in the GUI

- Paperless :
  - CLI deployement : `docker-compose run --rm webserver createsuperuser`
  - Portainer/GUI deployement : `python3 manage.py createsuperuser` inside the container. Reach it via GUI or using `docker exec -it paperless-server bash`
  Then follow the required informations to create accounts
