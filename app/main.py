from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.routers import router

app = FastAPI(
    title="Instagram Video Downloader API",
    description="",
    summary="Creator Asadbek",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Asadbek",
        "url": "http://asadbekmehmonjonov5@gmail.com/contact/",
        "email": "asadbekmehmonjonov5@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router.router)
