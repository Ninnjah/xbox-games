from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.cb_data import torrent_status


def download_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Найти игру", url="http://xbox-360.org/"
        )
    )

    return keyboard


def status_kb(torrent_hash: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Прогресс загрузки",
            callback_data=torrent_status.new(torrent_hash)
        )
    )

    return keyboard
