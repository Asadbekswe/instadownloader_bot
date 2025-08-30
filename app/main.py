from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.routers import download

app = FastAPI(title="Instagram Video Downloader")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(download.router)
