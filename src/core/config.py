import logging

from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = ".env"

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class BotSettings(BaseModel):
    token: str


class DataBaseSettings(BaseModel):
    url: str | PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    log_date_format: str = LOG_DATE_FORMAT
    log_file: str = "bot.log"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]

class AdminSettings(BaseModel):
    admin_ids: list

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="BOT__",
    )

    bot: BotSettings
    db: DataBaseSettings
    logging: LoggingConfig = LoggingConfig()
    admin: AdminSettings

settings = Settings()
