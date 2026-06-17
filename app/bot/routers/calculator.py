from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks import CalculatorCallback, CalculatorYesNoCallback
from app.bot.keyboards.inline import (
    calculator_deadline_keyboard,
    calculator_result_keyboard,
    calculator_type_keyboard,
    calculator_yes_no_keyboard,
)
from app.bot.text_catalog import text
from app.bot.utils import answer_or_edit_with_photo, asset_path
from app.services.calculator import BOT_TYPES, DEADLINES, calculate_price, money, wizard_back

router = Router(name="calculator")
CALCULATOR_PHOTO = asset_path("calculator_menu.jpg")


class CalculatorStates(StatesGroup):
    choosing_type = State()
    choosing_integrations = State()
    choosing_admin = State()
    choosing_deadline = State()


CALC_START_TEXT = text("calculator.start")
INTEGRATIONS_TEXT = text("calculator.integrations")
ADMIN_PANEL_TEXT = text("calculator.admin_panel")
DEADLINE_TEXT = text("calculator.deadline")


@router.message(F.text == text("keyboard.main.calculator"))
async def calculator_start_message(message: Message, state: FSMContext) -> None:
    await state.set_state(CalculatorStates.choosing_type)
    await state.set_data({})
    await answer_or_edit_with_photo(message, CALC_START_TEXT, CALCULATOR_PHOTO, calculator_type_keyboard())


@router.callback_query(CalculatorCallback.filter(F.action == "start"))
async def calculator_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CalculatorStates.choosing_type)
    await state.set_data({})
    await answer_or_edit_with_photo(callback, CALC_START_TEXT, CALCULATOR_PHOTO, calculator_type_keyboard())
    await callback.answer()


@router.callback_query(CalculatorCallback.filter(F.action == "type"))
async def calculator_type(callback: CallbackQuery, callback_data: CalculatorCallback, state: FSMContext) -> None:
    if callback_data.value not in BOT_TYPES:
        await callback.answer(text("calculator.error.type_not_found"), show_alert=True)
        return
    await state.update_data(bot_type=callback_data.value)
    await state.set_state(CalculatorStates.choosing_integrations)
    await answer_or_edit_with_photo(
        callback,
        INTEGRATIONS_TEXT,
        CALCULATOR_PHOTO,
        calculator_yes_no_keyboard(
            "integrations",
            back_to="integrations",
            yes_key="keyboard.calculator.integrations.yes",
            no_key="keyboard.calculator.integrations.no",
        ),
    )
    await callback.answer()


@router.callback_query(CalculatorYesNoCallback.filter(F.action == "integrations"))
async def calculator_integrations(callback: CallbackQuery, callback_data: CalculatorYesNoCallback, state: FSMContext) -> None:
    await state.update_data(integrations=callback_data.value)
    await state.set_state(CalculatorStates.choosing_admin)
    await answer_or_edit_with_photo(
        callback,
        ADMIN_PANEL_TEXT,
        CALCULATOR_PHOTO,
        calculator_yes_no_keyboard(
            "admin",
            back_to="admin",
            yes_key="keyboard.calculator.admin.yes",
            no_key="keyboard.calculator.admin.no",
        ),
    )
    await callback.answer()


@router.callback_query(CalculatorYesNoCallback.filter(F.action == "admin"))
async def calculator_admin(callback: CallbackQuery, callback_data: CalculatorYesNoCallback, state: FSMContext) -> None:
    await state.update_data(admin_panel=callback_data.value)
    await state.set_state(CalculatorStates.choosing_deadline)
    await answer_or_edit_with_photo(callback, DEADLINE_TEXT, CALCULATOR_PHOTO, calculator_deadline_keyboard(back_to="deadline"))
    await callback.answer()


@router.callback_query(CalculatorCallback.filter(F.action == "deadline"))
async def calculator_deadline(callback: CallbackQuery, callback_data: CalculatorCallback, state: FSMContext) -> None:
    data = await state.get_data()
    bot_type = data["bot_type"]
    integrations = bool(data["integrations"])
    admin_panel = bool(data["admin_panel"])
    deadline = callback_data.value
    await state.update_data(deadline=deadline)
    min_price, max_price = calculate_price(bot_type, integrations, admin_panel, deadline)
    price_text = (
        text("calculator.price.individual")
        if bot_type == "other"
        else text("calculator.price.range", min_price=money(min_price), max_price=money(max_price))
    )
    result_text = text(
        "calculator.result",
        bot_type=BOT_TYPES[bot_type].title,
        integrations_text=text("calculator.answer.yes") if integrations else text("calculator.answer.no"),
        admin_panel_text=text("calculator.answer.yes") if admin_panel else text("calculator.answer.no"),
        deadline=DEADLINES[deadline].title,
        price_text=price_text,
    )
    await answer_or_edit_with_photo(callback, result_text, CALCULATOR_PHOTO, calculator_result_keyboard())
    await callback.answer()


@router.callback_query(CalculatorCallback.filter(F.action == "back"))
async def calculator_back(callback: CallbackQuery, callback_data: CalculatorCallback, state: FSMContext) -> None:
    previous = wizard_back(callback_data.value)
    if previous is None:
        await callback.answer(text("calculator.error.step_not_found"), show_alert=True)
        return

    if previous.id == "bot_type":
        await state.set_state(CalculatorStates.choosing_type)
        await answer_or_edit_with_photo(callback, CALC_START_TEXT, CALCULATOR_PHOTO, calculator_type_keyboard())
    elif previous.id == "integrations":
        await state.set_state(CalculatorStates.choosing_integrations)
        await answer_or_edit_with_photo(
            callback,
            INTEGRATIONS_TEXT,
            CALCULATOR_PHOTO,
            calculator_yes_no_keyboard(
                "integrations",
                back_to="integrations",
                yes_key="keyboard.calculator.integrations.yes",
                no_key="keyboard.calculator.integrations.no",
            ),
        )
    elif previous.id == "admin_panel":
        await state.set_state(CalculatorStates.choosing_admin)
        await answer_or_edit_with_photo(
            callback,
            ADMIN_PANEL_TEXT,
            CALCULATOR_PHOTO,
            calculator_yes_no_keyboard(
                "admin",
                back_to="admin",
                yes_key="keyboard.calculator.admin.yes",
                no_key="keyboard.calculator.admin.no",
            ),
        )
    elif previous.id == "deadline":
        await state.set_state(CalculatorStates.choosing_deadline)
        await answer_or_edit_with_photo(callback, DEADLINE_TEXT, CALCULATOR_PHOTO, calculator_deadline_keyboard(back_to="deadline"))
    await callback.answer()
