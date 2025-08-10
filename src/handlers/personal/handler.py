from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import RegistrationState, AdminState
from core.db import db_helper
from core.crud import UserCRUD, ShiftCRUD, ShiftRoleCRUD, RoleCRUD, PayoutCRUD
from core.config import settings
from keyboards.reply import get_markup_by_list
from utils import ReportGenerator, AdminUtil


router = Router()


@router.message(F.text, RegistrationState.request_name)
async def reg_user(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    name = message.text.strip()

    async with db_helper.session_factory() as session:
        u = await UserCRUD.get_user_by_name(session, name)
        if u:
            txt = (
                f"⚠️ <b>{name}</b> ismi allaqachon botimizda ro'yxatdan o'tgan.\n\n"
                f"Agar bu sizning haqiqiy ismingiz bo‘lsa, iltimos, kichik qo‘shimcha bilan yuboring. "
                f"Masalan: <b>{name} A</b> yoki <b>{name} B</b>"
            )
            await message.answer(txt)
            return

        await UserCRUD.reg_user(session, tg_id, name)

    await state.clear()
    await message.answer(
        "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz! Botdan foydalanishni davom ettirishingiz mumkin."
    )


@router.message(Command("report"))
async def request_report(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    if tg_id not in settings.admin.admin_ids:
        async with db_helper.session_factory() as session:
            worker = await UserCRUD.get_user_by_tg_id(session, tg_id)

        shifts = await ShiftCRUD.get_shifts(session, worker.id)
        payouts = await PayoutCRUD.get_payouts(session, worker.id)

        report = await ReportGenerator.calculate_total(session, worker, shifts, payouts)
        await message.reply(report)
        return

    await state.set_state(AdminState.choose_worker_for_report)

    async with db_helper.session_factory() as session:
        workers = await UserCRUD.get_workers_names(session)

    markup = get_markup_by_list(workers)
    await message.reply(
        "Iltimos, sizga oylik haqidagi hisoboti kerak ishchi tanlang: ",
        reply_markup=markup,
    )


@router.message(F.text, AdminState.choose_worker_for_report)
async def show_report(message: Message, state: FSMContext):
    txt = message.text.strip()

    if txt == "🔙 Bekor qilib ortga qaytish.":
        await state.clear()
        await message.reply("✅ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        return

    async with db_helper.session_factory() as session:
        worker = await UserCRUD.get_user_by_name(session, txt)

    if not worker:
        await message.answer("⚠️ Bunday ishchi yo'q.")
        return

    shifts = await ShiftCRUD.get_shifts(session, worker.id)
    payouts = await PayoutCRUD.get_payouts(session, worker.id)

    report = await ReportGenerator.calculate_total(session, worker, shifts, payouts)
    await message.reply(report)


@router.message(Command("pay"))
async def request_report(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    if tg_id not in settings.admin.admin_ids:
        return

    await state.set_state(AdminState.choose_worker_for_payout)

    async with db_helper.session_factory() as session:
        workers = await UserCRUD.get_workers_names(session)

    markup = get_markup_by_list(workers)
    await message.reply(
        "Iltimos, pul to'lamoqchi bolgan ishchingizni tanlang: ",
        reply_markup=markup,
    )


@router.message(F.text, AdminState.choose_worker_for_payout)
async def choose_worker_for_payout(message: Message, state: FSMContext):
    worker_name = message.text.strip()

    if worker_name == "🔙 Bekor qilib ortga qaytish.":
        await state.clear()
        await message.reply("✅ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        return

    async with db_helper.session_factory() as session:
        worker = await UserCRUD.get_user_by_name(session, worker_name)

    if not worker:
        await message.answer(f"⚠️ <b>{worker_name}</b> ismli ishchi topilmadi.")
        return

    await state.update_data(
        user_name=worker.name, user_id=worker.id, user_tg_id=worker.tg_id
    )

    await state.set_state(AdminState.request_amount)

    await message.reply(
        f"<b>{worker.name}</b>ga to'lamoqchi bo'lgan pul miqdorini jo'nating.\n"
        f"Bekor qilish uchun <b>0</b> yuboring.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text, AdminState.request_amount)
async def show_report(message: Message, state: FSMContext):
    txt = message.text.strip()

    if txt == "0":
        await state.clear()
        await message.reply("✅ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(amount=txt)
    await state.set_state(AdminState.request_note)
    await message.reply(
        f"Bu qanday to'lo'v ekanligini yuboring. Masalan, <b>Avans</b>, <b>Oylik</b> yoki <b>Boshqa</b>.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text, AdminState.request_note)
async def show_report(message: Message, state: FSMContext):
    txt = message.text.strip()

    date = datetime.now().astimezone()
    data = await state.get_data()

    async with db_helper.session_factory() as session:
        await PayoutCRUD.add_payout(
            session, data.get("user_id"), data.get("amount"), date, txt
        )

    txt_for_worker = f"✅ Sizga {date.strftime('%d/%m/%Y')} sanada {txt} sifatida {data.get('amount')} so'm miqdorida to'lov o'tkazildi."
    txt = f"✅ Tayyor. {date.strftime('%d/%m/%Y')} sanada <b>{data.get('user_name')}</b>ga {data.get('amount')} so'm miqdorida to'lov amalga oshirildi."

    await AdminUtil.send_msg(data.get("user_tg_id"), txt_for_worker)

    await state.clear()
    await message.reply(txt, reply_markup=ReplyKeyboardRemove())
