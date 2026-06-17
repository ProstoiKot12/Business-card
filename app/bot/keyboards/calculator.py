from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import CalculatorCallback, CalculatorYesNoCallback
from app.bot.keyboards.menu import home_button
from app.bot.text_catalog import text
from app.services.calculator import BOT_TYPES, DEADLINES


def calculator_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in BOT_TYPES.items():
        builder.button(text=item.title, callback_data=CalculatorCallback(action="type", value=key).pack())
    home_button(builder)
    builder.adjust(1)
    return builder.as_markup()


def calculator_yes_no_keyboard(
    action: str,
    back_to: str | None = None,
    yes_key: str = "keyboard.calculator.yes",
    no_key: str = "keyboard.calculator.no",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text(yes_key), callback_data=CalculatorYesNoCallback(action=action, value=True).pack())
    builder.button(text=text(no_key), callback_data=CalculatorYesNoCallback(action=action, value=False).pack())
    if back_to:
        home_button(builder)
        builder.button(text=text("keyboard.back"), callback_data=CalculatorCallback(action="back", value=back_to).pack())
        builder.adjust(2, 2)
    else:
        home_button(builder)
        builder.adjust(2, 1)
    return builder.as_markup()


def calculator_deadline_keyboard(back_to: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in DEADLINES.items():
        builder.button(text=item.title, callback_data=CalculatorCallback(action="deadline", value=key).pack())
    home_button(builder)
    if back_to:
        builder.button(text=text("keyboard.back"), callback_data=CalculatorCallback(action="back", value=back_to).pack())
        builder.adjust(1, 1, 1, 2)
    else:
        builder.adjust(1)
    return builder.as_markup()


def calculator_result_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text("keyboard.calculator.contact"), callback_data=CalculatorCallback(action="contact").pack())
    builder.button(text=text("keyboard.calculator.restart"), callback_data=CalculatorCallback(action="start").pack())
    home_button(builder)
    builder.button(text=text("keyboard.calculator.back_to_deadlines"), callback_data=CalculatorCallback(action="back", value="result").pack())
    builder.adjust(1, 1, 2)
    return builder.as_markup()
