from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.cb_data import torrent_status


def main_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1 )

    keyboard.add(
        InlineKeyboardButton(
            text="🔎 Найти игру", url="http://xbox-360.org/"
        ),
        InlineKeyboardButton(
            text="⬇️Прогресс загрузки",
            callback_data=torrent_status.new()
        )
    )

    return keyboard


def download_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="🔎 Найти игру", url="http://xbox-360.org/"
        )
    )

    return keyboard


def status_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="⬇️Прогресс загрузки",
            callback_data=torrent_status.new()
        )
    )

    return keyboard
