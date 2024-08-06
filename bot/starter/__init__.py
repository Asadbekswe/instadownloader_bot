from aiogram import Router

from bot.handlers.handler import router

begin_router = Router()

begin_router.include_router(
    router,
)
