import asyncio
import os


async def schedule_file_delete(file_path: str, delay: int = 300):
    await asyncio.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)