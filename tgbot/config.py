import configparser
from dataclasses import dataclass
from typing import Optional


@dataclass
class DbConfig:
    database: str


@dataclass
class TgBot:
    token: str
    admin_id: int
    torrent_path: Optional[str] = None


@dataclass
class Xbox:
    ip_address: str
    port: int
    user: str
    password: str
    games_path: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    xbox: Xbox


def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes")


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            admin_id=int(tg_bot["admin_id"]),
            torrent_path=tg_bot["torrent_path"] if tg_bot["torrent_path"] != "" else None
        ),
        db=DbConfig(**config["db"]),
        xbox=Xbox(
            ip_address=config["xbox"]["ip_address"],
            port=int(config["xbox"]["port"]),
            user=config["xbox"]["user"],
            password=config["xbox"]["password"],
            games_path=config["xbox"]["games_path"]
        ),
    )
