from datetime import date

from core.config import settings

from .load import BotLoader


def _format_data(data: dict) -> str:
    d = date.today().strftime("%d.%m.%Y")
    type = "Kunduzgi" if data.get("shift_type") == "day" else "Tungi"
    roles = " ".join([w.title() for w in data.get("roles")])

    text = (
        f"{d}\n"
        f"👤 <b>{data.get('name')}</b>\n"
        f"🕧 Ish vaqti: <b>{data.get('start_time')} - {data.get('end_time')}</b>\n"
        f"🌗 Smena: <b>{type}</b>\n"
        f"📌 Rol: <b>{roles}</b>\n"
    )

    if data.get("bonus", 0) != 0:
        text += f"💵 Qo'shimcha: +{data.get('bonus')}"

    return text


class AdminUtil:
    @staticmethod
    async def send_records_to_admins(records_data: list[dict]):
        bot = BotLoader.get_bot(settings.bot.token)

        for aid in settings.admin.admin_ids:
            for data in records_data:
                text = _format_data(data)

                await bot.send_message(chat_id=aid, text=text)
