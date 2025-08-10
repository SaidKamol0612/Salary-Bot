from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router as main_router
from utils import BotLoader
from states import RegistrationState
from core.config import settings
from core.db import db_helper
from core.crud import UserCRUD

dp = Dispatcher(storage=MemoryStorage())


async def start_bot() -> None:
    bot = BotLoader.get_bot(settings.bot.token)
    await BotLoader.set_bot_commands(
        bot, {"start": "launch a bot", "report": "request a report"}
    )

    dp.include_router(main_router)

    await dp.start_polling(bot)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    if message.chat.type == "private":
        async with db_helper.session_factory() as session:
            u = await UserCRUD.get_user_by_tg_id(session, tg_id)
        name = u.name if u else message.from_user.first_name
        start_msg = f"Assalomu alaykum, <b>{name}</b>! 👋\n"

        if not u:
            start_msg += "Iltimos, botdan foydalanishni davom ettirish uchun avval o‘zingizning <b>haqiqiy ismingizni</b> yuboring."
            await state.set_state(RegistrationState.request_name)
        else:
            await state.clear()
    else:
        start_msg = "Assalomu alaykum, guruh a'zolari! 👋"

    await message.reply(text=start_msg)
