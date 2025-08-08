from datetime import datetime, date as py_date

from aiogram import Router, F
from aiogram.types import Message

from utils import RecordParser, AdminUtil
from core.crud import ShiftCRUD
from core.db import db_helper

router = Router()


def get_today() -> str:
    return py_date.today().strftime("%d.%m.%Y")


@router.message(lambda m: m.text and m.text.startswith(get_today()))
async def set_record(message: Message):
    content = message.text.strip()
    date, *records = content.split("\n")

    records_data = []
    for r in records:
        try:
            data = RecordParser.parse_shift_message(r)
            records_data.append(data)
        except ValueError:
            await message.reply(
                "⚠️ Not'g'ri formatdagi xabar. Iltimos, to'g'ri formatda yuboring. Masalan, <b>Saidkamol | 10:00 - 18:00 | T</b>"
            )

            return

    async with db_helper.session_factory() as session:
        date_obj = datetime.strptime(date, "%d.%m.%Y").date()
        await ShiftCRUD.add_shifts(session, date_obj, records_data)

    await AdminUtil.send_records_to_admins(records_data)
    await message.reply("✅ Qabul qildim.")
