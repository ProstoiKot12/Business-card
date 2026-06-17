from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.menu import home_button
from app.bot.text_catalog import text


def contacts_keyboard(telegram_url: str, max_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    links_count = 0
    if telegram_url:
        builder.button(text=text("keyboard.contacts.telegram"), url=telegram_url)
        links_count += 1
    if max_url:
        builder.button(text=text("keyboard.contacts.max"), url=max_url)
        links_count += 1
    home_button(builder)
    builder.adjust(links_count, 1) if links_count > 1 else builder.adjust(1)
    return builder.as_markup()
