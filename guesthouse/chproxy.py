import signal
from pathlib import Path
from subprocess import Popen
from tempfile import TemporaryDirectory

import yaml
from yaml import Dumper, Loader


# A line of comment.
class ChProxy:
    def __init__(self, chproxy_path: Path, template_path: Path, user_prefix: str):
        self.config_dir = TemporaryDirectory()
        self.config_path = Path(self.config_dir.name) / "config.yml"
        self.chproxy_path = chproxy_path
        self.process: Popen | None = None
        self.template_path = template_path
        self.user_prefix = user_prefix
        self.users: dict = {}

    def start(self) -> None:
        assert not self.process, "chproxy is already running"
        self.write_config()
        self.process = Popen([self.chproxy_path, "-config", self.config_path])

    def stop(self) -> None:
        assert self.process, "chproxy is not running"
        self.process.terminate()
        self.process = None

    def reload(self) -> None:
        assert self.process, "chproxy is not running"
        self.write_config()
        self.process.send_signal(signal.SIGHUP)

    def add_user(self, username: str, password: str, cluster: str) -> None:
        assert username not in self.users, "user already exists"
        self.users[username] = {
            "username": username,
            "password": password,
            "cluster": cluster,
        }

    def remove_user(self, username: str) -> None:
        self.users.pop(username, None)

    def generate_config(self, template: dict) -> dict:
        config = template.copy()
        # cluster name -> cluster index
        cluster_idx = {
            cluster["name"]: i for i, cluster in enumerate(config.get("clusters", []))
        }
        # Remove chproxy users
        for cluster in config.get("clusters", []):
            cluster["users"] = [
                user
                for user in cluster.get("users", [])
                if not user["name"].startswith(self.user_prefix)
            ]
        config["users"] = [
            user
            for user in config.get("users", [])
            if not user["name"].startswith(self.user_prefix)
        ]
        # Add chproxy users
        for user in self.users.values():
            config["users"].append(
                {
                    "name": user["username"],
                    "password": user["password"],
                    "to_cluster": user["cluster"],
                    "to_user": user["username"],
                    # TODO: Parameterize these.
                    "allow_cors": True,
                    "max_execution_time": "1h",
                }
            )
            config["clusters"][cluster_idx[user["cluster"]]]["users"].append(
                {"name": user["username"], "password": user["password"]}
            )
        return config

    def write_config(self) -> None:
        with self.template_path.open() as f:
            template = yaml.load(f, Loader)
        config = self.generate_config(template)
        with self.config_path.open("w") as f:
            yaml.dump(config, f, Dumper)
