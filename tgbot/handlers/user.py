import re
import logging

import aiohttp
from aiohttp.client_exceptions import InvalidURL
from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.handlers.inline.user import download_kb

logger = logging.getLogger(__name__)


async def parse_torrent(m: Message):
    url = m.text
    if not url.startswith("http://xbox-360.org/"):
        await m.reply(
            "Не та ссылка. Нужно прислать ссылку с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>"
        )
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.text()

                elif resp.status == 404:
                    await m.reply(
                        "По этой ссылке ничего не найдено :("
                    )
                    return

                else:
                    await m.reply(
                        "Во время загрузки данных произошла ошибка"
                    )
                    logger.error(f"RESP STATUS ERROR: {resp.__dict__}")

        except InvalidURL:
            await m.reply(
                "Не та ссылка. Нужно прислать ссылку с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>"
            )
            logger.warning(f"InvalidURL: {url}")

    search = re.findall(">Название:.+?<br", content)
    game_name = search[0][10:-3].strip() if search else ""

    search = re.findall(">Год выпуска:.+?<br", content)
    age = search[0][13:-3].strip() if search else ""

    search = re.findall(">Прошивка:.+?<br", content)
    firmware = search[0][10:-3].strip() if search else ""

    search = re.findall('<a target="_blank" href=".*"', content)
    game_url = search[0][25:-1].strip() if search else ""

    search = re.findall('<div style="text-align:center;">.*?<img src=".*?"', content)
    game_img_raw = search[0].strip() if search else ""

    if game_img_raw:
        search = re.findall('<img src=".*?"', game_img_raw)
        game_img = "http://xbox-360.org" + search[0][10:-1].strip() if search else ""

    else:
        game_img = ""

    message: str = f"{game_name}\n\n" \
                   f"Год выпуска: {age}\n" \
                   f"Прошивка: {firmware + '✅' if 'freeboot' in firmware.lower() else firmware + '⚠️'}"
    await m.answer_photo(
        photo=game_img, caption=message,
        reply_markup=download_kb(game_url)
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(parse_torrent, content_types=["text"])
