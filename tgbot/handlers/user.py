import asyncio
import re
import logging

import aiohttp
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiohttp.client_exceptions import InvalidURL
import qbittorrentapi

from tgbot.cb_data import torrent_status
from tgbot.handlers.inline.user import status_kb, main_kb
from tgbot.handlers.reply.user import status_reply_kb

logger = logging.getLogger(__name__)


async def user_start(m: Message):
    await m.answer(
        "Чтобы загрузить игру отправь ссылку на нее с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>\n\n"
        "Для проверки прогресса загрузки игр нажми на кнопку \"Прогресс загрузки\" под любой игрой в этом чате, "
        "Либо нажми кнопку \"Прогресс загрузки\" внизу\n\n"
        "<b>Описание картинок статуса загрузки</b>\n"
        "⬇️ - Загружается\n"
        "🔽 - Подготовка к загрузке\n"
        "🔃 - В очереди\n"
        "⏸ - Приостановлен\n"
        "✅ - Загружен",
        disable_web_page_preview=True,
        reply_markup=main_kb()
    )


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
                    logger.info(f"SUCCESS ADD TORRENT: {url}")

                # Not found
                elif resp.status == 404:
                    await m.reply(
                        "По этой ссылке ничего не найдено :("
                    )
                    return

                # Other errors
                else:
                    logger.error(f"RESP STATUS ERROR: {resp.__dict__}")
                    await m.reply(
                        "Во время загрузки данных произошла ошибка"
                    )

        # Invalid url
        except InvalidURL:
            logger.warning(f"InvalidURL: {url}")
            await m.reply(
                "Не та ссылка. Нужно прислать ссылку с сайта <a href=\"http://xbox-360.org/\">xbox-360.org</a>"
            )

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
    if any([x for x in ["freeboot", "jtag"] if x in firmware.lower()]):
        firmware = f"{firmware}✅"
    else:
        firmware = f"{firmware}⚠"

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
                   f"Прошивка: {firmware}\n\n" \
                   f"Добавлена к загрузке!"

    # Send message to user
    await m.answer_photo(
        photo=game_img, caption=message,
        reply_markup=status_kb()
    )


async def check_torrent_progress(callback: CallbackQuery):
    status_emoji = {
        "downloading": "⬇️",
        "uploading": "⬇️",
        "stalledUP": "⬇️",
        "stalledDL": "🔽",
        "complete": "✅",
        "queuedUP": "⬇️",
        "queuedDL": "🔃",
        "pausedUP": "✅",
        "pausedDL": "⏸",
    }
    # Init torrent client
    qbt_client = qbittorrentapi.Client(
        host='localhost',
        port=8080,
    )

    # Find bot torrents
    torrent = [x for x in qbt_client.torrents_info() if x.tags == "bot"]
    if not torrent:
        await callback.message.reply(
            "Ни одного торрента не было добавлено!\n"
            "Чтобы добавить отправь ссылку на игру с сайта "
            "<a href=\"http://xbox-360.org/\">xbox-360.org</a>"
        )
        return

    # Generate message
    message = "\n".join(
        f"{status_emoji.get(x.state) if status_emoji.get(x.state) is not None else x.state} "
        f"<b>{x.name}</b> - {x.progress * 100:.1f}%" for x in torrent
    )
    await callback.message.answer(message)


async def check_torrent_progress_reply(m: Message):
    status_emoji = {
        "downloading": "⬇️",
        "uploading": "⬇️",
        "stalledUP": "⬇️",
        "stalledDL": "🔽",
        "complete": "✅",
        "queuedUP": "⬇️",
        "queuedDL": "🔃",
        "pausedUP": "✅",
        "pausedDL": "⏸",
    }
    # Init torrent client
    qbt_client = qbittorrentapi.Client(
        host='localhost',
        port=8080,
    )

    # Find bot torrents
    torrent = [x for x in qbt_client.torrents_info() if x.tags == "bot"]
    if not torrent:
        await m.reply(
            "Ни одного торрента не было добавлено!\n"
            "Чтобы добавить отправь ссылку на игру с сайта "
            "<a href=\"http://xbox-360.org/\">xbox-360.org</a>"
        )
        return

    # Generate message
    message = "\n".join(
        f"{status_emoji.get(x.state) if status_emoji.get(x.state) is not None else x.state} "
        f"<b>{x.name}</b> - {x.progress * 100:.1f}%" for x in torrent
    )
    await m.answer(message)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"])
    dp.register_message_handler(
        check_torrent_progress_reply, lambda m: m.text == status_reply_kb().keyboard[0][0].text
    )
    dp.register_message_handler(parse_torrent, content_types=["text"])
    dp.register_callback_query_handler(check_torrent_progress, torrent_status.filter())
