from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.callbacks import AdminCaseCallback, AdminFieldCallback
from app.bot.keyboards.inline import (
    admin_cases_keyboard,
    admin_panel_keyboard,
    admin_stack_keyboard,
    case_type_keyboard,
    delete_confirm_keyboard,
    edit_fields_keyboard,
    order_keyboard,
    preview_keyboard,
    skip_keyboard,
)
from app.bot.middlewares import AdminOnlyMiddleware
from app.bot.text_catalog import html_text, text, text_lines
from app.bot.utils import answer_or_edit
from app.db.repositories import CaseRepository
from app.services.case_editor import normalize_optional_link, to_case_data
from app.services.cases import format_case_card

router = Router(name="admin")
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())


class AdminStates(StatesGroup):
    title = State()
    other_type = State()
    emoji = State()
    task = State()
    context = State()
    approach = State()
    outcome = State()
    stack = State()
    custom_stack = State()
    media = State()
    bot_link = State()
    extra_link = State()
    preview = State()
    edit_value = State()


FIELD_LABELS = {
    "title": text("admin.field.title"),
    "type": text("admin.field.type"),
    "task": text("admin.field.task"),
    "context": text("admin.field.context"),
    "approach": text("admin.field.approach"),
    "outcome": text("admin.field.outcome"),
    "stack": text("admin.field.stack"),
    "media": text("admin.field.media"),
    "links": text("admin.field.links"),
}


async def show_admin_panel(target: Message | CallbackQuery, session: AsyncSession) -> None:
    count = await CaseRepository(session).count_all()
    panel_text = text("admin.panel", count=count)
    if isinstance(target, CallbackQuery):
        await answer_or_edit(target, panel_text, admin_panel_keyboard())
        await target.answer()
    else:
        await target.answer(panel_text, reply_markup=admin_panel_keyboard())


async def ask_emoji(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.emoji)
    await message.answer(text("admin.add.step2.emoji"))


async def ask_stack(target: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.stack)
    data = await state.get_data()
    selected = data.get("stack", [])
    message_text = text("admin.add.step7.stack")
    if isinstance(target, CallbackQuery):
        await answer_or_edit(target, message_text, admin_stack_keyboard(selected))
        await target.answer()
    else:
        await target.answer(message_text, reply_markup=admin_stack_keyboard(selected))


async def ask_media(target: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.media)
    message_text = text("admin.add.step8.media")
    if isinstance(target, CallbackQuery):
        await answer_or_edit(target, message_text, skip_keyboard("photo_done"))
        await target.answer()
    else:
        await target.answer(message_text, reply_markup=skip_keyboard("photo_done"))


async def show_preview(target: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.preview)
    data = await state.get_data()
    preview_text = text("admin.preview", case_card=format_case_card(type("DraftCase", (), to_case_data(data))()))
    if isinstance(target, CallbackQuery):
        await answer_or_edit(target, preview_text, preview_keyboard())
        await target.answer()
    else:
        media_group = data.get("media_group", [])
        if media_group:
            await target.answer_photo(media_group[0], caption=preview_text, reply_markup=preview_keyboard())
        else:
            await target.answer(preview_text, reply_markup=preview_keyboard())


async def finish_links_edit(target: Message | CallbackQuery, state: FSMContext, session: AsyncSession) -> bool:
    data = await state.get_data()
    if not data.get("edit_existing") or data.get("edit_field") != "links":
        return False
    case = await CaseRepository(session).get(data["case_id"])
    if case:
        await CaseRepository(session).update(
            case,
            {
                "bot_link": data.get("bot_link"),
                "extra_link": data.get("extra_link"),
            },
        )
    await state.clear()
    if isinstance(target, CallbackQuery):
        await show_admin_panel(target, session)
    else:
        await target.answer(text("admin.links.updated"))
        await show_admin_panel(target, session)
    return True


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await show_admin_panel(message, session)


@router.message(Command("cancel"))
async def admin_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(text("admin.cancel.done"))


@router.callback_query(AdminCaseCallback.filter(F.action == "panel"))
async def admin_panel_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await show_admin_panel(callback, session)


@router.callback_query(AdminCaseCallback.filter(F.action == "exit"))
async def admin_exit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await answer_or_edit(callback, text("admin.panel.closed"))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "add"))
async def add_case_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AdminStates.title)
    await state.set_data({"stack": [], "media_group": []})
    await answer_or_edit(callback, text("admin.add.step1.title"))
    await callback.answer()


@router.message(AdminStates.title)
async def add_case_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminStates.other_type)
    await message.answer(text("admin.case.choose_type"), reply_markup=case_type_keyboard())


@router.callback_query(AdminCaseCallback.filter(F.action == "type"))
async def add_case_type(callback: CallbackQuery, callback_data: AdminCaseCallback, state: FSMContext) -> None:
    if callback_data.field == "other":
        await state.set_state(AdminStates.other_type)
        await answer_or_edit(callback, text("admin.case.custom_type"))
        await callback.answer()
        return
    await state.update_data(type=callback_data.field)
    if callback.message:
        await ask_emoji(callback.message, state)
    await callback.answer()


@router.message(AdminStates.other_type)
async def add_case_other_type(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if "title" not in data:
        return
    await state.update_data(type=message.text.strip())
    await ask_emoji(message, state)


@router.message(AdminStates.emoji)
async def add_case_emoji(message: Message, state: FSMContext) -> None:
    await state.update_data(emoji=message.text.strip()[:8])
    await state.set_state(AdminStates.context)
    await message.answer(text("admin.add.step3.context"))


@router.message(AdminStates.context)
async def add_case_context(message: Message, state: FSMContext) -> None:
    await state.update_data(context=message.text.strip())
    await state.set_state(AdminStates.task)
    await message.answer(text("admin.add.step4.task"))


@router.message(AdminStates.task)
async def add_case_task(message: Message, state: FSMContext) -> None:
    await state.update_data(task=message.text.strip())
    await state.set_state(AdminStates.approach)
    await message.answer(text("admin.add.step5.approach"))


@router.message(AdminStates.approach)
async def add_case_approach(message: Message, state: FSMContext) -> None:
    await state.update_data(approach=message.text.strip())
    await state.set_state(AdminStates.outcome)
    await message.answer(text("admin.add.step6.outcome"))


@router.message(AdminStates.outcome)
async def add_case_outcome(message: Message, state: FSMContext) -> None:
    await state.update_data(outcome=message.text.strip())
    await ask_stack(message, state)


@router.callback_query(AdminCaseCallback.filter(F.action == "toggle_stack"))
async def toggle_stack(callback: CallbackQuery, callback_data: AdminCaseCallback, state: FSMContext) -> None:
    data = await state.get_data()
    selected = list(data.get("stack", []))
    tech = callback_data.field
    if tech in selected:
        selected.remove(tech)
    else:
        selected.append(tech)
    await state.update_data(stack=selected)
    await answer_or_edit(callback, text("admin.stack.choose"), admin_stack_keyboard(selected))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "add_stack"))
async def custom_stack_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminStates.custom_stack)
    await answer_or_edit(callback, text("admin.stack.custom"))
    await callback.answer()


@router.message(AdminStates.custom_stack)
async def custom_stack_save(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected = list(data.get("stack", []))
    tech = message.text.strip()
    if tech and tech not in selected:
        selected.append(tech)
    await state.update_data(stack=selected)
    await ask_stack(message, state)


@router.callback_query(AdminCaseCallback.filter(F.action == "stack_done"))
async def stack_done(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    if data.get("edit_existing") and data.get("edit_field") == "stack":
        case = await CaseRepository(session).get(data["case_id"])
        if case:
            await CaseRepository(session).update(case, {"stack": data.get("stack", [])})
        await state.clear()
        await show_admin_panel(callback, session)
        return
    await ask_media(callback, state)


@router.message(AdminStates.media, F.photo)
async def collect_media(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media_group = list(data.get("media_group", []))
    if len(media_group) < 10:
        media_group.append(message.photo[-1].file_id)
    await state.update_data(media_group=media_group)
    await message.answer(text("admin.media.added", count=len(media_group)), reply_markup=skip_keyboard("photo_done"))


@router.callback_query(AdminCaseCallback.filter(F.action == "photo_done"))
async def photo_done(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    if data.get("edit_existing") and data.get("edit_field") == "media":
        case = await CaseRepository(session).get(data["case_id"])
        if case:
            await CaseRepository(session).update(case, {"media_group": data.get("media_group", [])})
        await state.clear()
        await show_admin_panel(callback, session)
        return
    await state.set_state(AdminStates.bot_link)
    await answer_or_edit(callback, text("admin.link.bot"), skip_keyboard("bot_link_skip"))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "bot_link_skip"))
async def bot_link_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(bot_link=None)
    await state.set_state(AdminStates.extra_link)
    await answer_or_edit(callback, text("admin.link.extra"), skip_keyboard("extra_link_skip"))
    await callback.answer()


@router.message(AdminStates.bot_link)
async def bot_link_save(message: Message, state: FSMContext) -> None:
    await state.update_data(bot_link=normalize_optional_link(message.text))
    await state.set_state(AdminStates.extra_link)
    await message.answer(text("admin.link.extra"), reply_markup=skip_keyboard("extra_link_skip"))


@router.callback_query(AdminCaseCallback.filter(F.action == "extra_link_skip"))
async def extra_link_skip(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(extra_link=None)
    if await finish_links_edit(callback, state, session):
        return
    if callback.message:
        await show_preview(callback.message, state)
    await callback.answer()


@router.message(AdminStates.extra_link)
async def extra_link_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(extra_link=normalize_optional_link(message.text))
    if await finish_links_edit(message, state, session):
        return
    await show_preview(message, state)


@router.callback_query(AdminCaseCallback.filter(F.action == "save"))
async def save_case(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await CaseRepository(session).add(to_case_data(data))
    await state.clear()
    await show_admin_panel(callback, session)


@router.callback_query(AdminCaseCallback.filter(F.action == "cancel"))
async def cancel_case(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await answer_or_edit(callback, text("admin.case.cancelled"))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "change_field"))
async def change_field(callback: CallbackQuery) -> None:
    await answer_or_edit(callback, text("admin.field.choose"), edit_fields_keyboard())
    await callback.answer()


@router.callback_query(AdminFieldCallback.filter())
async def field_selected(callback: CallbackQuery, callback_data: AdminFieldCallback, state: FSMContext) -> None:
    field = callback_data.field
    await state.update_data(edit_field=field)
    if field == "stack":
        await ask_stack(callback, state)
        return
    if field == "media":
        await state.update_data(media_group=[])
        await ask_media(callback, state)
        return
    if field == "links":
        await state.set_state(AdminStates.bot_link)
        await answer_or_edit(callback, text("admin.link.bot"), skip_keyboard("bot_link_skip"))
        await callback.answer()
        return
    await state.set_state(AdminStates.edit_value)
    await answer_or_edit(callback, html_text("admin.field.enter_value", field_label=FIELD_LABELS[field]))
    await callback.answer()


@router.message(AdminStates.edit_value)
async def edit_value_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    field = data["edit_field"]
    value = message.text.strip()
    if data.get("edit_existing"):
        case = await CaseRepository(session).get(data["case_id"])
        if case:
            await CaseRepository(session).update(case, {field: value})
        await state.clear()
        await message.answer(text("admin.field.updated"))
        await show_admin_panel(message, session)
        return
    await state.update_data(**{field: value})
    await show_preview(message, state)


@router.callback_query(AdminCaseCallback.filter(F.action == "edit_list"))
async def edit_list(callback: CallbackQuery, session: AsyncSession) -> None:
    cases = await CaseRepository(session).list_all()
    await answer_or_edit(callback, text("admin.edit.choose_case"), admin_cases_keyboard(cases, "edit_open"))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "edit_open"))
async def edit_open(callback: CallbackQuery, callback_data: AdminCaseCallback, state: FSMContext, session: AsyncSession) -> None:
    case = await CaseRepository(session).get(callback_data.case_id)
    if case is None:
        await callback.answer(text("admin.case.not_found"), show_alert=True)
        return
    await state.set_data(
        {
            "edit_existing": True,
            "case_id": case.id,
            "stack": case.stack,
            "media_group": case.media_group,
        }
    )
    await answer_or_edit(callback, text("admin.field.choose"), edit_fields_keyboard())
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "delete_list"))
async def delete_list(callback: CallbackQuery, session: AsyncSession) -> None:
    cases = await CaseRepository(session).list_all()
    await answer_or_edit(callback, text("admin.delete.choose_case"), admin_cases_keyboard(cases, "delete_open"))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "delete_open"))
async def delete_open(callback: CallbackQuery, callback_data: AdminCaseCallback, session: AsyncSession) -> None:
    case = await CaseRepository(session).get(callback_data.case_id)
    if case is None:
        await callback.answer(text("admin.case.not_found"), show_alert=True)
        return
    await answer_or_edit(
        callback,
        html_text("admin.delete.confirm", case_title=case.title),
        delete_confirm_keyboard(case.id),
    )
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action == "delete_confirm"))
async def delete_confirm(callback: CallbackQuery, callback_data: AdminCaseCallback, session: AsyncSession) -> None:
    repo = CaseRepository(session)
    case = await repo.get(callback_data.case_id)
    if case:
        await repo.delete(case)
    await show_admin_panel(callback, session)


@router.callback_query(AdminCaseCallback.filter(F.action == "order"))
async def order_cases(callback: CallbackQuery, session: AsyncSession) -> None:
    cases = await CaseRepository(session).list_all()
    lines = [text("admin.order.title") + "\n"]
    lines.extend(f"{index}. {case.emoji} {case.title}" for index, case in enumerate(cases, start=1))
    await answer_or_edit(callback, "\n".join(lines), order_keyboard(cases))
    await callback.answer()


@router.callback_query(AdminCaseCallback.filter(F.action.in_({"move_up", "move_down"})))
async def move_case(callback: CallbackQuery, callback_data: AdminCaseCallback, session: AsyncSession) -> None:
    repo = CaseRepository(session)
    cases = await repo.list_all()
    ids = [case.id for case in cases]
    index = ids.index(callback_data.case_id)
    if callback_data.action == "move_up" and index > 0:
        ids[index - 1], ids[index] = ids[index], ids[index - 1]
    if callback_data.action == "move_down" and index < len(ids) - 1:
        ids[index + 1], ids[index] = ids[index], ids[index + 1]
    await repo.reorder(ids)
    cases = await repo.list_all()
    lines = [text("admin.order.title") + "\n"]
    lines.extend(f"{position}. {case.emoji} {case.title}" for position, case in enumerate(cases, start=1))
    await answer_or_edit(callback, "\n".join(lines), order_keyboard(cases))
    await callback.answer()
