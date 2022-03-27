from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.cb_data import torrent_status


def download_kb(url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Скачать игру", url=url
        )
    )

    return keyboard


def status_kb(hash: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Прогресс загрузки",
            callback_data=torrent_status.new(hash)
        )
    )

    return keyboard
