from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def download_kb(url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text="Скачать игру", url=url
        )
    )

    return keyboard
