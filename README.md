# Flask-BigApp Boilerplate
### This is a quick deployment tool for a Flask-BigApp application.
It includes pre-setup configs and a server module that can handle docker-compose deployments.

Configuration files to check over:
```text
# This config file is standard config file.
/app/default.config.toml

# This config file is tagged to have the env variables injected by the
# server module
/app/env.config.toml

# These are the docker compose config files
/server/docker-c-*.yml

# These are the environment variable files
/server/env_files/*.env
- these files are only used when using the 
- docker-compose, or python3 server start commands

# You can adjust the __main__.py file to adapt these options
/server/__main__.py
```


### Flask

#### Start Flask
```
flask run
```

### Gunicorn Server Launcher

#### Start the server normally:
```
server start
```
Use RUN_ENV env variable to dictate the mode of running (default is "production").


### Docker Compose

#### Runs docker-compose with development env variables:
```
server docker development up
server docker development down
```

#### Runs docker-compose with production env variables:
```
server docker production up
server docker production down
```
