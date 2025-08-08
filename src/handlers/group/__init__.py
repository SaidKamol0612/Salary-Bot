__all__ = ("router",)

from aiogram import Router

from .handler import router as r

router = Router()

router.include_router(r)
