import logging
from datetime import datetime, date as py_date

from aiogram import Router
from aiogram.types import Message

from utils import RecordParser, AdminUtil, ReportGenerator
from core.crud import ShiftCRUD, UserCRUD, PayoutCRUD
from core.db import db_helper

router = Router()


def get_today() -> str:
    return py_date.today().strftime("%d.%m.%Y")


@router.message(lambda m: m.text and m.text.startswith(get_today()))
async def set_record(message: Message):
    content = message.text.strip()
    date_str, *records = content.split("\n")

    # Foydalanuvchi bir kunda faqat bitta yozuv yuborishi kerak
    if len(records) > 1:
        await message.reply(
            "⚠️ Bir kishi faqat o‘zi uchun bitta ma’lumot yuborishi mumkin."
        )
        return

    # Xabar formatini tekshirish
    try:
        data = RecordParser.parse(records[0])
    except ValueError:
        await message.reply(
            "⚠️ Noto‘g‘ri formatdagi xabar. Iltimos, quyidagi ko‘rinishda yuboring:\n"
            "<b>Saidkamol | 10:00 - 18:00 | T</b>"
        )
        return

    async with db_helper.session_factory() as session:
        # Foydalanuvchini tekshirish
        user = await UserCRUD.get_user_by_tg_id(session, message.from_user.id)
        if not user:
            await message.reply("❌ Siz tizimda ro‘yxatdan o‘tmagansiz.")
            return

        # O‘z ma’lumotini kiritganini tekshirish
        if user.name != data.get("name"):
            await message.reply("⚠️ Har kim faqat o‘z ma’lumotini yuborishi mumkin.")
            return

        # Sanani tekshirish
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            await message.reply("⚠️ Sana formati noto‘g‘ri. Masalan: 10.08.2025")
            return
        # Yangi smenani qo‘shish
        try:
            await ShiftCRUD.add_shift(session, date_obj, data)
        except ValueError as e:
            logging.error(f"Value error: {e}")
            await message.reply(
                "⚠️ Ma’lumotni saqlashda xatolik yuz berdi. Iltimos, tekshirib qayta yuboring."
            )
            return

        # Avvalgi ma’lumotlarni olish
        shifts = await ShiftCRUD.get_shifts(session, user.id)
        payouts = await PayoutCRUD.get_payouts(session, user.id)

        # Umumiy hisobni qo‘shish
        data["total"] = await ReportGenerator.calculate_total(session, shifts, payouts)

    # Adminlarga yuborish
    txt = await AdminUtil.send_record_to_admins(data)
    await AdminUtil.send_msg(user.tg_id, txt)

    await message.reply("✅ Ma’lumot muvaffaqiyatli qabul qilindi.")
