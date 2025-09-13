# ntfyer/main.py

import click

from dataclasses import dataclass
from httpx import post, Response
from json import load, dump
from os import environ
from os.path import exists, join
from sys import exit
from typing import Optional


# consts
DB_PATH: str = join(".", "src", "ntfyer", "settings.json")
# vars
# > no vars declared


# # program classes
@dataclass
class Configurations:
    notifier_url: Optional[str] = None

    def __init__(self) -> None:
        self.notifier_url = f"{self.read_config_value(prop='URL')}/{self.read_config_value(prop='TOPIC')}"
        return None
    
    def initialize_database(self) -> None:
        CONFIGS_DEFAULT: dict[str, str] = {
            "URL": "https://ntfy.sh",
            "FMT": "md",
            "TOPIC": "test_topic",
        }
        for key, val in CONFIGS_DEFAULT.items():
            self.write_config_values(prop=key, val=val)
        return None
    
    def read_config_value(self, prop: str) -> Optional[str]:
        with open(file=DB_PATH, mode="r") as fp:
            configs: dict[str, str] = load(fp=fp)
        # print(f"DEBUG {configs = }")
        prop_value: Optional[str] = configs.get(prop, None)
        return prop_value

    def write_config_values(self, prop: str, val: str) -> None:
        with open(file=DB_PATH, mode="r") as fp:
            configs: dict[str, str] = load(fp=fp)
        configs[prop] = val
        # print(f"DEBUG {configs = }")
        with open(file=DB_PATH, mode="w") as fp:
            _ = dump(obj=configs, fp=fp)
        # >> if modified url or topic, regenerate notifier_url
        if prop == "URL" or prop == "TOPIC":
            self.notifier_url = f"{self.read_config_value(prop='URL')}/{self.read_config_value(prop='TOPIC')}"
        return None


# methods
def check_settings_database(path: str) -> None:
    if not exists(path=path):
        raise FileNotFoundError
    else:
        return None


def create_settings_database(path: str) -> None:
    with open(file=DB_PATH, mode="w") as fp:
        init_dict: dict[str, str] = {"TEST": "test"}
        dump(obj=init_dict, fp=fp)
    return None


def is_first_run() -> bool:
    RUN_FILE: str = join(".", "src", "ntfyer", ".use")
    with open(file=RUN_FILE, mode="r") as fp:
        data: str = fp.read()
    if data == "0":
        return True
    else:
        return False


def first_run_setup() -> None:
    RUN_FILE: str = join(".", "src", "ntfyer", ".use")
    configs: Configurations = Configurations()
    configs.initialize_database()
    with open(file=RUN_FILE, mode="w") as fp:
        fp.write("1")
    return None


# main
def main():
    # # init database
    try:
        check_settings_database(path=DB_PATH)
    except FileNotFoundError:
        create_settings_database(path=DB_PATH)
        configs: Configurations = Configurations()
        configs.initialize_database()
    except Exception as e:
        print("ERROR: An unknown exception was found")
        print(f"ERROR: Exception found: {e}")
        exit(1)
    try:
        init_fg: bool = is_first_run()
        print(f"{init_fg = }")
        if init_fg:
            first_run_setup()
    except Exception as e:
        print("ERROR: An unknown exception was found")
        print(f"ERROR: Exception found: {e}")
        exit(1)
    return None


# groups
@click.group("cli")
def cli():
    pass


@cli.group("config")
def configs():
    pass


# commands
@configs.command(name="url")
@click.argument("url")
def change_notifier_url(url) -> None:
    configs: Configurations = Configurations()
    configs.write_config_values(prop="URL", val=url)
    print(f"The new notifier URL is {configs.notifier_url}")
    return None


@configs.command(name="topic")
@click.argument("topic")
def change_notifier_topic(topic) -> None:
    configs: Configurations = Configurations()
    configs.write_config_values(prop="TOPIC", val=topic)
    print(f"The new notifier URL is {configs.notifier_url}")
    return None


@configs.command(name="get")
def get_nntfy_url() -> None:
    configs: Configurations = Configurations()
    print(f"The notifier URL is {configs.notifier_url}")
    return None


@configs.command(name="defaults")
def set_default_configs() -> None:
    configs: Configurations = Configurations()
    configs.initialize_database()
    print("Settings set to default values")
    print(f"Current notifier URL is {configs.notifier_url}")
    return None


@cli.command(name="send")
@click.argument("text")
def notify(text) -> None:
    configs: Configurations = Configurations()
    if configs.notifier_url is None:
        raise ValueError
    req: Response = post(
        url=configs.notifier_url,
        data=text,
    )
    if req.status_code != 200:
        raise RuntimeError("Error sending notification")
    return None


# exec
if __name__ == "__main__":
    main()
    cli()
else:
    pass
