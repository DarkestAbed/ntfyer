# main.py

from httpx import post
from os import getcwd
from os.path import exists, join
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sys import exit
from typing import Any


# consts
# vars
Base = declarative_base()


# classes
class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property = Column(String)
    value = Column(String)


class SettingsHistory(Base):
    __tablename__ = "settings_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    property = Column(String)
    value = Column(String)
    updated_at = Column(DateTime)


# methods
def check_settings_database(path: str) -> None:
    if not exists(path=path):
        print("Settings database not found!")
        raise FileNotFoundError
    else:
        print("Settings database found! Proceeding...")
    return None


def create_settings_database(url: str) -> Any:
    engine = create_engine(url=url, echo=True)
    Base.metadata.create_all(engine)
    print("Settings base created! Proceeding...")
    return engine


# main
def main():
    # vars & consts
    DB_PATH: str = join(".", "settings.db")
    DB_URL: str = "sqlite:///settings.db"
    try:
        check_settings_database(path=DB_PATH)
    except FileNotFoundError:
        create_settings_database(url=DB_URL)
    except Exception as e:
        print("ERROR: An unknown exception was found")
        print(f"ERROR: Exception found: {e}")
        exit(1)
    return None


# exec
if __name__ == "__main__":
    main()
else:
    pass
