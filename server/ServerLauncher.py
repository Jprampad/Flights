import importlib
import multiprocessing
import os
import subprocess
import sys
import socket
import time
from abc import ABC

import gunicorn.app.base
from dotenv import load_dotenv


class SGIapp(gunicorn.app.base.BaseApplication, ABC):
    def __init__(self, application, options):
        self.application = application
        self.options = options or dict()
        super().__init__()

    def load_config(self):
        _config = {key: value for key, value in self.options.items()
                   if key in self.cfg.settings and value is not None}
        for key, value in _config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


class Server:
    def __init__(self, env_file: str = None, project_root: str = None):
        if project_root is None:
            project_root = "/".join(os.path.realpath(os.path.dirname(__file__)).split("/")[:-1])
        self.ACCESS_LOG, self.ERROR_LOG = self.sgi_log_files(project_root)
        self.load_env_file(env_file)
        self.WORKERS = self.set_workers(os.environ.get('WORKERS', '3'))
        self.package_check(("gevent", "gevent"))
        self.SGI_CONFIG = {
            'bind': os.environ.get('BIND', '0.0.0.0:5000'),
            'workers': self.WORKERS,
            'worker_class': "gevent",
        }

    @staticmethod
    def package_check(package: tuple) -> None:
        """
        package = ("pip install ref", "import ref")
        :param package:
        :return None:
        """
        try:
            importlib.import_module(package[1])
        except ImportError:
            subprocess.call([f'{sys.executable}', '-m', 'pip', 'install', package[0]])

    @staticmethod
    def set_workers(workers):
        if workers == "auto":
            return (multiprocessing.cpu_count() * 2) + 1
        return int(workers)

    @staticmethod
    def sgi_log_files(project_root) -> tuple:
        logs_path = f"{project_root}/logs"
        a_log = f"{logs_path}/sgi.access.log"
        e_log = f"{logs_path}/sgi.error.log"
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        if not os.path.isfile(a_log):
            with open(a_log, "w") as a:
                a.write("")
        if not os.path.isfile(e_log):
            with open(e_log, "w") as e:
                e.write("")
        return a_log, e_log

    @staticmethod
    def envs_required(list_of_env: list) -> bool:
        for env in list_of_env:
            if env not in os.environ:
                return False
        return True

    def load_env_file(self, env_file: str) -> None:
        self.package_check(("python-dotenv", "dotenv"))
        env_file = env_file
        os_env_file = os.environ.get("ENV_FILE", None)
        if env_file is not None:
            load_dotenv(env_file)
        if os_env_file is not None:
            load_dotenv(os_env_file)

    def start(self, app_factory):

        db_type = os.environ.get("DB_TYPE", None)

        # if the database type is postgres or mysql, wait until the database is live before starting.
        if db_type == "postgresql" or db_type == "mysql":
            if self.envs_required(
                    ["DB_LOCATION", "DB_USERNAME", "DB_PASSWORD", "DB_NAME"]
            ):
                db = os.environ.get("DB_LOCATION").split(":")

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                while sock.connect_ex((db[0], int(db[1]))) != 0:
                    time.sleep(2)
                sock.close()

        run_env = os.environ.get("RUN_ENV", "development")

        if run_env == "production":
            self.SGI_CONFIG.update({
                'loglevel': 'info',
                'accesslog': self.ACCESS_LOG,
                'errorlog': self.ERROR_LOG
            })
            SGIapp(app_factory(), self.SGI_CONFIG).run()
            return

        if run_env == "development":
            self.SGI_CONFIG.update({
                'reload': True,
                'debug': True,
                'loglevel': 'info',
            })
            SGIapp(app_factory(), self.SGI_CONFIG).run()
            return

        app = app_factory()
        app.run(host="0.0.0.0", port=5000, debug=True)
