from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.bot.text_catalog import text

HOME_BUTTON = text("keyboard.home")


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text=HOME_BUTTON)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=text("keyboard.menu.input_placeholder"))

