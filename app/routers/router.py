import os
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.schemas import DownloadRequest
from app.services.service import download_instagram_video
from app.utils.cleaner import schedule_file_delete

router = APIRouter(prefix="/api", tags=["Instagram Reels Download"])

VIDEO_DIR = os.path.join("app", "static", "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)


@router.post("/download")
async def download_by_url(data: DownloadRequest, background_tasks: BackgroundTasks, request: Request):
    url = data.url

    file_name = f"{uuid.uuid4()}.mp4"  # noqa
    file_path = os.path.join(VIDEO_DIR, file_name)

    success = await download_instagram_video(url, file_path)
    if not success:
        raise HTTPException(status_code=404, detail="Video topilmadi")

    background_tasks.add_task(schedule_file_delete, file_path, delay=300)

    base_url = str(request.base_url).rstrip("/")
    return {
        "status": "ok",
        "download_link": f"{base_url}/static/videos/{file_name}"
    }
