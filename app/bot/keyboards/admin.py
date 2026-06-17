from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import AdminCaseCallback, AdminFieldCallback
from app.bot.text_catalog import text as t, text_lines
from app.db.models import Case


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("keyboard.admin.add_case"), callback_data=AdminCaseCallback(action="add").pack())
    builder.button(text=t("keyboard.admin.edit_case"), callback_data=AdminCaseCallback(action="edit_list").pack())
    builder.button(text=t("keyboard.admin.delete_case"), callback_data=AdminCaseCallback(action="delete_list").pack())
    builder.button(text=t("keyboard.admin.order"), callback_data=AdminCaseCallback(action="order").pack())
    builder.button(text=t("keyboard.admin.exit"), callback_data=AdminCaseCallback(action="exit").pack())
    builder.adjust(1)
    return builder.as_markup()


def case_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in [
        (t("keyboard.admin.case_type.ai"), t("admin.field.type.ai")),
        (t("keyboard.admin.case_type.sales"), t("admin.field.type.sales")),
        (t("keyboard.admin.case_type.crm"), t("admin.field.type.crm")),
        (t("keyboard.admin.case_type.mini_app"), t("admin.field.type.mini_app")),
        (t("keyboard.admin.case_type.other"), "other"),
    ]:
        builder.button(text=label, callback_data=AdminCaseCallback(action="type", field=value).pack())
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def admin_stack_keyboard(selected: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    options = text_lines("admin.stack.options")
    for tech in options:
        mark = t("admin.stack.selected_mark") if tech in selected else ""
        builder.button(text=f"{tech}{mark}", callback_data=AdminCaseCallback(action="toggle_stack", field=tech).pack())
    builder.button(text=t("keyboard.admin.add_custom_stack"), callback_data=AdminCaseCallback(action="add_stack").pack())
    builder.button(text=t("keyboard.admin.done"), callback_data=AdminCaseCallback(action="stack_done").pack())
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


def skip_keyboard(action: str = "skip") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("keyboard.admin.skip"), callback_data=AdminCaseCallback(action=action).pack())
    return builder.as_markup()


def preview_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("keyboard.admin.save"), callback_data=AdminCaseCallback(action="save").pack())
    builder.button(text=t("keyboard.admin.change_field"), callback_data=AdminCaseCallback(action="change_field").pack())
    builder.button(text=t("keyboard.admin.cancel"), callback_data=AdminCaseCallback(action="cancel").pack())
    builder.adjust(1)
    return builder.as_markup()


def edit_fields_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, field in [
        (t("keyboard.admin.field.title"), "title"),
        (t("keyboard.admin.field.type"), "type"),
        (t("keyboard.admin.field.context"), "context"),
        (t("keyboard.admin.field.task"), "task"),
        (t("keyboard.admin.field.approach"), "approach"),
        (t("keyboard.admin.field.outcome"), "outcome"),
        (t("keyboard.admin.field.stack"), "stack"),
        (t("keyboard.admin.field.media"), "media"),
        (t("keyboard.admin.field.links"), "links"),
    ]:
        builder.button(text=label, callback_data=AdminFieldCallback(field=field).pack())
    builder.adjust(2)
    return builder.as_markup()


def admin_cases_keyboard(cases: list[Case], action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for case in cases:
        builder.button(text=f"{case.emoji} {case.title}", callback_data=AdminCaseCallback(action=action, case_id=case.id).pack())
    builder.button(text=t("keyboard.admin.to_panel"), callback_data=AdminCaseCallback(action="panel").pack())
    builder.adjust(1)
    return builder.as_markup()


def delete_confirm_keyboard(case_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("keyboard.admin.delete_yes"), callback_data=AdminCaseCallback(action="delete_confirm", case_id=case_id).pack())
    builder.button(text=t("keyboard.admin.delete_no"), callback_data=AdminCaseCallback(action="panel").pack())
    builder.adjust(2)
    return builder.as_markup()


def order_keyboard(cases: list[Case]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, case in enumerate(cases):
        if index > 0:
            builder.button(text=t("keyboard.admin.move_up", case_label=f"{case.emoji} {case.title}"), callback_data=AdminCaseCallback(action="move_up", case_id=case.id).pack())
        if index < len(cases) - 1:
            builder.button(text=t("keyboard.admin.move_down", case_label=f"{case.emoji} {case.title}"), callback_data=AdminCaseCallback(action="move_down", case_id=case.id).pack())
    builder.button(text=t("keyboard.admin.save_order"), callback_data=AdminCaseCallback(action="panel").pack())
    builder.adjust(1)
    return builder.as_markup()



