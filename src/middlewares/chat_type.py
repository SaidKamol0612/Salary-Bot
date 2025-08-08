from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable


class PrivateChatOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.chat.type != "private":
            await event.answer("⚠️ Bu buyruq faqat shaxsiy suhbatda ishlaydi.")
            return
        return await handler(event, data)


class GroupChatOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.chat.type not in ("group", "supergroup"):
            await event.answer("Bu buyruq faqat guruhlarda ishlaydi.")
            return
        return await handler(event, data)
