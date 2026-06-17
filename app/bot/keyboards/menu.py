from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import AboutCallback, CalculatorCallback, CasesCallback, FaqCallback, HomeCallback
from app.bot.text_catalog import text
from app.config import get_settings


def home_button(builder: InlineKeyboardBuilder) -> None:
    builder.button(text=text("keyboard.home"), callback_data=HomeCallback(action="main").pack())


def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Web App", web_app=WebAppInfo(url=settings.webapp_url))
    builder.button(text=text("keyboard.main.cases"), callback_data=CasesCallback(action="list").pack())
    builder.button(text=text("keyboard.main.about"), callback_data=AboutCallback(action="main").pack())
    builder.button(text=text("keyboard.main.calculator"), callback_data=CalculatorCallback(action="start").pack())
    builder.button(text=text("keyboard.main.faq"), callback_data=FaqCallback(action="list").pack())
    builder.button(text=text("keyboard.main.contacts"), callback_data=FaqCallback(action="contact").pack())
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()
