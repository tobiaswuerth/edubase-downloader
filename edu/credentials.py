from typing import NamedTuple
import os
import yaml

CONFIG_PATH = "config.yaml"


class Credentials(NamedTuple):
    username: str
    password: str


def load_credentials() -> Credentials:
    assert os.path.exists(CONFIG_PATH), f"Config file not found: {CONFIG_PATH}"
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert "username" in config, "Username not found in config file"
    assert "password" in config, "Password not found in config file"
    username = config.get("username")
    password = config.get("password")
    assert username, "Username cannot be empty"
    assert password, "Password cannot be empty"

    return Credentials(username=username, password=password)
