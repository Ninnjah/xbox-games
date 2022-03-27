from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def status_reply_kb():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        KeyboardButton(
            text="Прогресс загрузки"
        )
    )

    return keyboard
