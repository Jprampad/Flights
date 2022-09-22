import os
import secrets
import subprocess
import sys

path = "/".join(os.path.realpath(os.path.dirname(__file__)).split("/")[:-1])
project = os.path.realpath(os.path.dirname(__file__)).split("/")[-2]

sys.path.append(path)


def run():
    from app import create_app
    from server.ServerLauncher import Server

    os.environ["COMPOSE_PROJECT_NAME"] = project
    os.environ['SK'] = secrets.token_urlsafe(128)

    if "--help" in sys.argv:
        print("""
Commands:

server start
- starts the server normally. Use RUN_ENV env variable to dictate the mode of running (default is "production").

server docker development up
server docker development down
- runs docker-compose with development env variables

server docker production up
server docker production down
- runs docker-compose with production env variables
        """)

    if "start" in sys.argv:
        server = Server()
        server.start(create_app)

    if "docker" in sys.argv:
        if "development" in sys.argv:
            os.environ["ENV_FILE"] = f"{path}/server/env_files/development.env"
            os.environ["COMPOSE_FILE"] = f"{path}/server/docker-c-dev.yml"

        if "production" in sys.argv:
            os.environ["ENV_FILE"] = f"{path}/server/env_files/production.env"
            os.environ["COMPOSE_FILE"] = f"{path}/server/docker-c-pro.yml"

        if "up" in sys.argv:
            subprocess.call([f"docker-compose", "build"])
            subprocess.call([f"docker-compose", "up", "--force-recreate", "--no-deps"])

        if "down" in sys.argv:
            subprocess.call([f"docker-compose", "down"])


if __name__ == '__main__':
    run()
