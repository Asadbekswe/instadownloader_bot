import asyncio
import os

import requests
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"<i>Assalomu aleykum, <b>{message.from_user.full_name} 👋🏻</b> link yuborishingiz mumkin 👇🏻!</i>")


def download_media(link: str):
    url = f"http://{os.getenv("SERVER_IP")}/igdl?url={link}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        media_url = data['url']['data'][0]['url']

        if not media_url:
            print("Media URL not found in response")
            return None

        media_response = requests.get(media_url, stream=True, timeout=10)
        media_response.raise_for_status()

        filename = "media/downloaded_video.mp4"
        with open(filename, "wb") as file:
            for chunk in media_response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Media file downloaded successfully: {filename}")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the media: {e}")
        return None


@router.message()
async def sent_to_video(message: Message, bot: Bot) -> None:
    try:
        video_link = message.send_copy(chat_id=message.chat.id).text
        filename = download_media(video_link)
        if video_link and video_link.startswith('https://www.instagram.com/') and len(video_link) >= 42 and filename:
            animation = await message.answer(text=f"⏳")
            await asyncio.sleep(2)
            for i in ["3️⃣", "2️⃣", "1️⃣"]:
                await asyncio.sleep(2)
                await animation.edit_text(text=f"<strong>{i} ...</strong>")
            await bot.delete_message(chat_id=message.chat.id, message_id=animation.message_id)
            await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
            video_file = FSInputFile(filename)
            await bot.send_video(chat_id=message.chat.id, video=video_file)

        else:
            sent = await message.answer("The URL may be incorrect, please check and try again. 👈🏻🫤")
            await asyncio.sleep(3)
            await bot.delete_message(chat_id=message.chat.id, message_id=sent.message_id)
        os.remove(filename)
    except Exception as e:
        print(f"An error occurred in the bot handler: {e}")
        await message.answer("The URL may be incorrect, please check and try again. 👈🏻🫤")

# @router.message()
# async def sent_to_video(message: Message, bot: Bot) -> None:
#     try:
#         # await message.answer(media)
#         copy = message.send_copy(chat_id=message.chat.id).text
#         if copy and copy.startswith('https://www.instagram.com/') and len(copy) >= 42:
#             copy = copy[:12] + "dd" + copy[12:]
#             animation = await message.answer(text=f"⏳")
#             await asyncio.sleep(1)
#             for i in ["3️⃣", "2️⃣", "1️⃣"]:
#                 await asyncio.sleep(1)
#                 await animation.edit_text(text=f"<strong>{i} ...</strong>")
#             await bot.delete_message(chat_id=message.chat.id, message_id=animation.message_id)
#             await message.answer(text=f"<strike>{copy}</strike>", parse_mode=ParseMode.HTML)
#         else:
#             await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#             sent = await message.answer(text=f"<b>Error(Link, Url) or Post Not Found !!! </b>")
#             await asyncio.sleep(3)
#             await bot.delete_message(chat_id=message.chat.id, message_id=sent.message_id)
#     except TelegramForbiddenError:
#         print("Failed to send a message: Forbidden")
