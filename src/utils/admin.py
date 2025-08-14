import logging
from datetime import date

from core.config import settings
from core.db import models

from .load import BotLoader


def _format_data(data: dict) -> str:
    d = date.today().strftime("%d.%m.%Y")
    type = "Kunduzgi" if data.get("shift_type") == "day" else "Tungi"
    roles = " ".join([w.title() for w in data.get("roles")])

    text = f"{d}\n" f"👤 <b>{data.get('name')}</b>\n"
    if data.get("start_time"):
        text += (
            f"🕧 Ish vaqti: <b>{data.get('start_time')} - {data.get('end_time')}</b>\n"
        )
    else:
        text += f"🥖 Xamirlar soni: <b>{data.get('count_dough')}</b>"

    text += f"🌗 Smena: <b>{type}</b>\n" f"📌 Rol: <b>{roles}</b>\n"

    if data.get("bonus", 0) != 0:
        text += f"💵 Qo'shimcha: +{data.get('bonus')}"

    text += f"<b>Bugun jami:</b> {data.get('daily_total')}\n"
    text += f"<b>Umumiy jami(to'lo'vlarni ayirib tashlaganda):</b> {data.get('total')}"
    return text


class AdminUtil:
    @staticmethod
    async def send_record_to_admins(data: dict):
        bot = BotLoader.get_bot(settings.bot.token)
        text = _format_data(data)

        for aid in settings.admin.admin_ids:
            try:
                await bot.send_message(chat_id=aid, text=text)
            except Exception as e:
                logging.warning(f"Message to admin {aid} failed: {e}")
        return text

    @staticmethod
    async def send_msg(chat_id: int, msg: str):
        bot = BotLoader.get_bot(settings.bot.token)
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.warning(f"Message to {chat_id} failed: {e}")
