__all__ = ("router",)

from aiogram import Router

from middlewares import GroupChatOnlyMiddleware, PrivateChatOnlyMiddleware

from .group import router as group_router
from .personal import router as personal_router
from .helper import router as helper_router

router = Router()

group_router.message.middleware(GroupChatOnlyMiddleware())
router.include_router(group_router)

personal_router.message.middleware(PrivateChatOnlyMiddleware())
router.include_router(personal_router)

router.include_router(helper_router)
