# Monitoring

## Logging in / Accounts

- Beszel :
  - Create account with email and password
  - The first time, copy the public SSH key in "Add New System" and paste it as env var for the agent if monitoring the same system and add it

- Speed test :
  - Create APP_KEY :
    - run `php artisan key:generate --show` from the container and add it to environment variables
  - Default credentials :
      - login : `admin@example.com` 
      - password : `password`
  Then change the default user name, email and password to yours

- Uptime Kuma :
  - Create a new user in the GUI
