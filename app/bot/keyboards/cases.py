from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import CaseStackCallback, CasesCallback
from app.bot.keyboards.menu import home_button
from app.bot.text_catalog import text
from app.db.models import Case


def cases_list_keyboard(cases: list[Case], page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    visible = cases[start:end]
    for case in visible:
        builder.button(
            text=f"{case.emoji} {case.title}",
            callback_data=CasesCallback(action="open", case_id=case.id).pack(),
        )
    if cases:
        builder.button(text=text("keyboard.cases.browse"), callback_data=CasesCallback(action="open", case_id=cases[0].id).pack())
    if len(cases) > per_page:
        prev_page = (page - 1) % ((len(cases) + per_page - 1) // per_page)
        next_page = (page + 1) % ((len(cases) + per_page - 1) // per_page)
        builder.button(text=text("keyboard.cases.prev"), callback_data=CasesCallback(action="list", page=prev_page).pack())
        builder.button(text=f"{page + 1}", callback_data=CasesCallback(action="noop").pack())
        builder.button(text=text("keyboard.cases.next"), callback_data=CasesCallback(action="list", page=next_page).pack())
    home_button(builder)
    builder.adjust(1)
    return builder.as_markup()


def case_card_keyboard(case: Case, cases: list[Case]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    ids = [item.id for item in cases]
    index = ids.index(case.id) if case.id in ids else 0
    prev_case = cases[(index - 1) % len(cases)] if cases else case
    next_case = cases[(index + 1) % len(cases)] if cases else case
    optional_rows = 0
    builder.button(text=text("keyboard.cases.stack"), callback_data=CaseStackCallback(action="list", case_id=case.id).pack())
    if case.bot_link:
        builder.button(text=text("keyboard.cases.open_bot"), url=case.bot_link)
        optional_rows += 1
    if case.extra_link:
        builder.button(text=text("keyboard.cases.more"), url=case.extra_link)
        optional_rows += 1
    builder.button(text=text("keyboard.cases.prev"), callback_data=CasesCallback(action="open", case_id=prev_case.id).pack())
    builder.button(text=f"{index + 1} / {len(cases)}", callback_data=CasesCallback(action="noop").pack())
    builder.button(text=text("keyboard.cases.next"), callback_data=CasesCallback(action="open", case_id=next_case.id).pack())
    home_button(builder)
    builder.adjust(1, *([1] * optional_rows), 3, 1)
    return builder.as_markup()


from app.services.techs import get_tech_info

def case_stack_keyboard(case: Case) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for tech in case.stack:
        info = get_tech_info(tech)
        label = f"{info.emoji} {info.name}"
        builder.button(text=label, callback_data=CaseStackCallback(action="tech", case_id=case.id, tech=tech).pack())
        
    home_button(builder)
    builder.button(text=text("keyboard.cases.back_to_case"), callback_data=CasesCallback(action="open", case_id=case.id).pack())
    
    sizes = [2] * (len(case.stack) // 2)
    if len(case.stack) % 2:
        sizes.append(1)
    sizes.append(2)
    builder.adjust(*sizes)
    return builder.as_markup()


def tech_keyboard(case_id: int, official_url: str | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if official_url:
        builder.button(text=text("keyboard.about.official_site"), url=official_url)
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=CaseStackCallback(action="list", case_id=case_id).pack())
    
    sizes = []
    if official_url:
        sizes.append(1)
    sizes.append(2)
    builder.adjust(*sizes)
    return builder.as_markup()
