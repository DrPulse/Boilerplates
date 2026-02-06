# Monitoring

## Logging in / Accounts

- Beszel :
  - Create account with email and password
  - The first time, copy the public SSH key in "Add New System" and paste it as env var for the agent if monitoring the same system and add it

- Nutify:
  - Connect to the NUT server as client
  - Create user and use auto conf (eventually explicit nut credentials)

- Scrutiny:
  Read the documentation and configure the devices in the [scrutiny_example.yaml](scrutiny_example.yaml) file if needed, sat or raid arrays can be finicky. Same if a disk had a self test error, --all" should be used instead of "xall", especially if this was a long time ago

- Speed test :
  - Create APP_KEY :
    - run `php artisan key:generate --show` from the container and add it to environment variables
  - Default credentials :
      - login : `admin@example.com` 
      - password : `password`
  Then change the default user name, email and password to yours

- Uptime Kuma :
  - Create a new user in the GUI
