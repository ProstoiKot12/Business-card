from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import CalculatorCallback, FaqCallback
from app.services.faq import FAQ_ITEMS
from app.bot.keyboards.menu import home_button
from app.bot.text_catalog import text


def faq_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in FAQ_ITEMS:
        builder.button(text=item.title, callback_data=FaqCallback(action="item", question_id=item.id).pack())
    builder.button(text=text("keyboard.faq.contact"), callback_data=FaqCallback(action="contact").pack())
    home_button(builder)
    builder.adjust(1)
    return builder.as_markup()


def faq_answer_keyboard(question_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if question_id == "price":
        builder.button(text=text("keyboard.main.calculator"), callback_data=CalculatorCallback(action="start").pack())
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=FaqCallback(action="list").pack())
    
    if question_id == "price":
        builder.adjust(1, 2)
    else:
        builder.adjust(2)
        
    return builder.as_markup()


def faq_final_keyboard(owner_telegram_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if owner_telegram_url:
        builder.button(text=text("keyboard.faq.contact"), url=owner_telegram_url)
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=FaqCallback(action="list").pack())
    builder.adjust(1, 2) if owner_telegram_url else builder.adjust(2)
    return builder.as_markup()
