import asyncio
import os
import uuid

import requests
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from bot.database import User

router = Router()

API_BASE = "http://localhost:8000/api/download"
BASE_URL = "http://localhost:8000"
MEDIA_DIR = os.path.abspath("media")
os.makedirs(MEDIA_DIR, exist_ok=True)

MAX_FILE_SIZE_MB = 49


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_data = message.from_user.model_dump(include={'id', 'first_name', 'last_name', 'username'})
    existing_user = await User.get_with_telegram_id(telegram_id=user_data['id'])

    if not existing_user:
        await User.create(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            username=user_data['username'],
            telegram_id=user_data['id'],
        )

    await message.answer(f"<i>Hi, <b>{message.from_user.full_name} 👋🏻</b> send me an Instagram link 👇🏻</i>")


def get_video_from_api(insta_url: str) -> str | None:
    try:
        response = requests.post(API_BASE, json={"url": insta_url}, timeout=90)
        response.raise_for_status()
        data = response.json()

        download_link = data.get("download_link")
        if not download_link:
            print("API javobida download_link topilmadi")
            return None

        if download_link.startswith("http"):
            file_url = download_link
        else:
            file_url = f"{BASE_URL}{download_link}"

        video_response = requests.get(file_url, stream=True, timeout=180)
        video_response.raise_for_status()

        filename = os.path.join(MEDIA_DIR, f"{uuid.uuid4()}.mp4")
        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=16384):
                f.write(chunk)

        return filename
    except requests.exceptions.Timeout:
        print("Xatolik: Timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP Xatolik: {e}")
        return None


@router.message()
async def handle_instagram_link(message: Message, bot: Bot):
    insta_url = message.text.strip()
    if not insta_url.startswith("https://www.instagram.com/"):
        await message.answer("Please send a valid Instagram link. 👈🏻")
        return

    status_msg = await message.answer("⏳ Downloading your video...")

    filename = await asyncio.to_thread(get_video_from_api, insta_url)

    if filename and os.path.exists(filename):
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            await status_msg.edit_text(f"Video is too large ({file_size_mb:.2f} MB). Telegram limit is 50 MB.")
            os.remove(filename)
            return

        await bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        video_file = FSInputFile(filename)
        await bot.send_video(chat_id=message.chat.id, video=video_file, caption="✅ Here is your video!")

        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
    else:
        await status_msg.edit_text("Failed to download the video. Please check the link.")
