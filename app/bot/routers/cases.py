from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callbacks import CaseStackCallback, CasesCallback
from app.bot.keyboards.inline import (
    case_card_keyboard,
    case_stack_keyboard,
    cases_list_keyboard,
    case_stack_keyboard,
    cases_list_keyboard,
    tech_keyboard,
)
from app.bot.text_catalog import text
from app.bot.utils import answer_or_edit_with_photo, asset_path, edit_case_media
from app.db.repositories import CaseRepository
from app.services.cases import format_case_card, format_stack, format_technology
from app.services.techs import get_tech_info

router = Router(name="cases")
CASES_PHOTO = asset_path("cases_menu.jpg")


@router.message(F.text == text("keyboard.main.cases"))
async def cases_entry(message: Message, session: AsyncSession) -> None:
    cases = await CaseRepository(session).list_visible()
    if not cases:
        await answer_or_edit_with_photo(message, text("cases.empty"), CASES_PHOTO)
        return
    if len(cases) <= 2:
        case = cases[0]
        await answer_or_edit_with_photo(message, format_case_card(case), CASES_PHOTO, case_card_keyboard(case, cases))
        return
    await answer_or_edit_with_photo(message, text("cases.intro"), CASES_PHOTO, cases_list_keyboard(cases))


@router.callback_query(CasesCallback.filter(F.action == "list"))
async def cases_list(callback: CallbackQuery, callback_data: CasesCallback, session: AsyncSession) -> None:
    cases = await CaseRepository(session).list_visible()
    await answer_or_edit_with_photo(callback, text("cases.intro"), CASES_PHOTO, cases_list_keyboard(cases, callback_data.page))
    await callback.answer()


@router.callback_query(CasesCallback.filter(F.action == "open"))
async def case_open(callback: CallbackQuery, callback_data: CasesCallback, session: AsyncSession) -> None:
    repo = CaseRepository(session)
    cases = await repo.list_visible()
    case = next((item for item in cases if item.id == callback_data.case_id), None)
    if case is None or callback.message is None:
        await callback.answer(text("cases.not_found"), show_alert=True)
        return
    await edit_case_media(callback.message, format_case_card(case), case_card_keyboard(case, cases), case.media_group)
    await callback.answer()


@router.callback_query(CasesCallback.filter(F.action == "noop"))
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(CaseStackCallback.filter(F.action == "list"))
async def case_stack(callback: CallbackQuery, callback_data: CaseStackCallback, session: AsyncSession) -> None:
    case = await CaseRepository(session).get(callback_data.case_id)
    if case is None:
        await callback.answer(text("cases.not_found"), show_alert=True)
        return
    await answer_or_edit_with_photo(callback, format_stack(case), CASES_PHOTO, case_stack_keyboard(case))
    await callback.answer()


@router.callback_query(CaseStackCallback.filter(F.action == "tech"))
async def case_tech(callback: CallbackQuery, callback_data: CaseStackCallback) -> None:
    info = get_tech_info(callback_data.tech)
    await answer_or_edit_with_photo(
        callback,
        format_technology(info),
        CASES_PHOTO,
        tech_keyboard(callback_data.case_id, info.url),
    )
    await callback.answer()
