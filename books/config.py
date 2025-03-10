from functools import lru_cache  # least recent used cache
from typing import Optional

# from pydantic import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None  # to choose dev, test or production

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None  # if not found in .env file
    DB_FORCE_ROLL_BACK: bool = False  # to clear the db after each test


class DevConfig(GlobalConfig):
    class Config:
        env_prefix: str = "DEV_"  # values populated from .env if they have the prefix


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"  # not username and password, automatically generated by the code
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    class Config:
        env_prefix: str = "PROD_"


# the returned values are only three possible values (environments), we can cache the function
@lru_cache()  # we don't need maximum size of cached values
def get_config(env_state: str):
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(
    BaseConfig().ENV_STATE
)  # BaseConfig only has one attribute defined by us, ENV_STATE
