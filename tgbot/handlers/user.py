import asyncio
import re
import logging

import aiohttp
from aiohttp.client_exceptions import InvalidURL
from aiogram import Dispatcher
from aiogram.types import Message
import qbittorrentapi

from tgbot.handlers.inline.user import status_kb

logger = logging.getLogger(__name__)


async def parse_torrent(m: Message):
    url = m.text
    # Simple validator
    if not url.startswith("http://xbox-360.org/"):
        await m.reply(
            "Не та ссылка. Нужно прислать ссылку с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>"
        )
        return

    # Download web page
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                # Success
                if resp.status == 200:
                    content = await resp.text()

                # Not found
                elif resp.status == 404:
                    await m.reply(
                        "По этой ссылке ничего не найдено :("
                    )
                    return

                # Other errors
                else:
                    await m.reply(
                        "Во время загрузки данных произошла ошибка"
                    )
                    logger.error(f"RESP STATUS ERROR: {resp.__dict__}")

        # Invalid url
        except InvalidURL:
            await m.reply(
                "Не та ссылка. Нужно прислать ссылку с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>"
            )
            logger.warning(f"InvalidURL: {url}")

    # Parsing
    # Parse game title
    search = re.findall(">Название:.+?<br", content)
    game_name = search[0][10:-3].strip() if search else ""

    # Parse game age
    search = re.findall(">Год выпуска:.+?<br", content)
    age = search[0][13:-3].strip() if search else ""

    # Parse game firmware
    search = re.findall(">Прошивка:.+?<br", content)
    firmware = search[0][10:-3].strip() if search else ""

    # Parse game torrent url
    search = re.findall('<a target="_blank" href=".*"', content)
    game_url = search[0][25:-1].strip() if search else ""

    # Parse game image first block
    search = re.findall('<div style="text-align:center;">.*?<img src=".*?"', content)
    game_img_raw = search[0].strip() if search else ""

    # Parse game image url
    if game_img_raw:
        search = re.findall('<img src=".*?"', game_img_raw)
        game_img = "http://xbox-360.org" + search[0][10:-1].strip() if search else ""

    else:
        game_img = ""

    # Init torrent client
    qbt_client = qbittorrentapi.Client(
        host='localhost',
        port=8080,
    )

    # Add torrent to download
    r = qbt_client.torrents.add(urls=game_url, tags="bot", rename=game_name)
    # Success
    if r == "Ok.":
        await asyncio.sleep(5)

    # Fail
    else:
        await m.reply("При добавлении торрента произошла ошибка!")
        logger.error(r.__dict__)
        return

    # Find game torrent
    torrent = [x for x in qbt_client.torrents_info() if x.tags == "bot" and x.name == game_name][0]

    # Create caption
    message: str = f"{game_name}\n\n" \
                   f"Год выпуска: {age}\n" \
                   f"Прошивка: {firmware + '✅' if 'freeboot' in firmware.lower() else firmware + '⚠️'}\n\n" \
                   f"Добавлена к загрузке!"

    # Send message to user
    await m.answer_photo(
        photo=game_img, caption=message,
        reply_markup=status_kb(torrent.hash)
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(parse_torrent, content_types=["text"])
