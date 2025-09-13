# main.py

import click

from dataclasses import dataclass
from httpx import post, Response
from os import environ
from os.path import exists, join
from pendulum import DateTime as PDateTime, now
from sqlalchemy import (
    create_engine,
    Column,
    DateTime,
    Engine,
    Integer,
    Result,
    select,
    Select,
    String,
    update,
    Update,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sys import exit
from typing import Optional


# consts
DB_PATH: str = join(".", "ntfy", "settings.db")
DB_URL: str = "sqlite:///ntfy/settings.db"
# vars
Base = declarative_base()


# classes
# # database classes
class Settings(Base):
    __tablename__ = "settings"
    property = Column(String, primary_key=True)
    value = Column(String)

    def __init__(self, property: str, value: str):
        self.property = property
        self.value = value
        return None


class SettingsHistory(Base):
    __tablename__ = "settings_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property = Column(String)
    value = Column(String)
    updated_at = Column(DateTime)

    def __init__(self, property: str, value: str, updated_at: PDateTime):
        self.property = property
        self.value = value
        self.updated_at = updated_at
        return None


# # program classes
@dataclass
class Configurations:
    session: Session
    notifier_url: Optional[str] = None

    def __init__(self, session: Session) -> None:
        self.session = session
        self.notifier_url = f"{self.read_config_value(prop='URL')}/{self.read_config_value(prop='TOPIC')}"
        return None
    
    def initialize_database(self) -> None:
        CONFIGS_DEFAULT: dict[str, str] = {
            "URL": "https://ntfy.sh/",
            "FMT": "md",
            "TOPIC": "test_topic",
        }
        # print("DEBUG initializing settings database with default values")
        for key, val in CONFIGS_DEFAULT.items():
            self.write_config_values(prop=key, val=val)
        return None

    def write_config_values(self, prop: str, val: str) -> None:
        def update_setting() -> None:
            query: Select = select(Settings).where(Settings.property == prop)
            results: Result = self.session.execute(query).all()
            if len(results) == 0:
                # print(f"DEBUG no settings found for property '{prop}'")
                new_setting: Settings = Settings(property=prop, value=val)
                self.session.add(new_setting)
            elif len(results) == 1:
                # print(f"DEBUG property '{prop}' found with 1 value")
                upd_setting: Update = (
                    update(Settings)
                    .where(Settings.property == prop)
                    .values(value=val)
                )
                # print(f"{upd_setting = }")
                self.session.execute(upd_setting)
            else:
                raise RuntimeError("Something is wrong in the settings database")
            self.session.commit()
            return None
        
        curr_ts: PDateTime = now(tz="America/Santiago")
        setting_history: SettingsHistory = SettingsHistory(
            property=prop,
            value=val,
            updated_at=curr_ts,
        )
        try:
            update_setting()
            self.session.add(setting_history)
            self.session.commit()
        except Exception as e:
            print("ERROR: Unable to update settings")
            print(f"ERROR: Exception {e}")
            raise RuntimeError
        # >> if modified url or topic, regenerate notifier_url
        if prop == "URL" or prop == "TOPIC":
            self.notifier_url = f"{self.read_config_value(prop='URL')}/{self.read_config_value(prop='TOPIC')}"
        return None


    def read_config_value(self, prop: str) -> str:
        query: Select = select(Settings.value).where(Settings.property == prop)
        results: Result = self.session.execute(query).all()
        if len(results) > 1:
            raise RuntimeError("Illegal number of return values")
        prop_value: str = results[0][0]
        return prop_value


# methods
def check_settings_database(path: str) -> None:
    if not exists(path=path):
        # print("Settings database not found!")
        raise FileNotFoundError
    else:
        return None
        # print("Settings database found! Proceeding...")


def create_settings_database(url: str) -> Engine:
    echo: bool = True if environ.get("ENVIRON", "dev") == "dev" else False
    engine: Engine = create_engine(url=url, echo=echo)
    Base.metadata.create_all(engine)
    # print("Settings base created! Proceeding...")
    return engine


def create_db_engine(url: str) -> Engine:
    echo: bool = True if environ.get("ENVIRON", "dev") == "dev" else False
    engine: Engine = create_engine(url=url, echo=echo)
    return engine    


def create_db_session(engine: Engine) -> Session:
    sess = sessionmaker(bind=engine)
    session: Session = sess()
    return session


# main
def main():
    # # init database
    try:
        check_settings_database(path=DB_PATH)
    except FileNotFoundError:
        eng: Engine = create_settings_database(url=DB_URL)
        session: Session = create_db_session(engine=eng)
        configs: Configurations = Configurations(session=session)
        configs.initialize_database()
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
    eng: Engine = create_db_engine(url=DB_URL)
    session: Session = create_db_session(engine=eng)
    configs: Configurations = Configurations(session=session)
    configs.write_config_values(prop="URL", val=url)
    print(f"The new notifier URL is {configs.notifier_url}")
    return None


@configs.command(name="topic")
@click.argument("topic")
def change_notifier_topic(topic) -> None:
    eng: Engine = create_db_engine(url=DB_URL)
    session: Session = create_db_session(engine=eng)
    configs: Configurations = Configurations(session=session)
    configs.write_config_values(prop="TOPIC", val=topic)
    print(f"The new notifier URL is {configs.notifier_url}")
    return None


@configs.command(name="get")
def get_nntfy_url() -> None:
    eng: Engine = create_db_engine(url=DB_URL)
    session: Session = create_db_session(engine=eng)
    configs: Configurations = Configurations(session=session)
    print(f"The notifier URL is {configs.notifier_url}")
    return None


@cli.command(name="send")
@click.argument("text")
def notify(text) -> None:
    eng: Engine = create_db_engine(url=DB_URL)
    session: Session = create_db_session(engine=eng)
    configs: Configurations = Configurations(session=session)
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
