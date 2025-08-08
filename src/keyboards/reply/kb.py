from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_markup_by_list(lst: list):
    keyboard = ReplyKeyboardBuilder()

    for item in lst:
        keyboard.add(KeyboardButton(text=item))
    keyboard.add(KeyboardButton(text="🔙 Bekor qilib ortga qaytish."))

    return keyboard.adjust(1).as_markup(resize_keyboard=True)
