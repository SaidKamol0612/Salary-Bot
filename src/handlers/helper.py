import logging

from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def debug_handler(message: Message):
    logging.warning(f"An unrecognized message: {repr(message.text)}")
    await message.answer("❗ Bu buyruq menga nomaʼlum.")
