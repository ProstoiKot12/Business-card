from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import AboutCallback
from app.bot.keyboards.menu import home_button
from app.bot.text_catalog import text


def about_keyboard(telegram_url: str, github_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text("keyboard.about.skills"), callback_data=AboutCallback(action="skills").pack())
    builder.button(text=text("keyboard.about.experience"), callback_data=AboutCallback(action="experience").pack())
    links_count = 0
    if telegram_url:
        builder.button(text=text("keyboard.about.telegram"), url=telegram_url)
        links_count += 1
    if github_url:
        builder.button(text=text("keyboard.about.github"), url=github_url)
        links_count += 1
    home_button(builder)
    
    sizes = [2]
    if links_count > 0:
        sizes.append(links_count)
    sizes.append(1)
    builder.adjust(*sizes)
    return builder.as_markup()


def about_detail_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=AboutCallback(action="main").pack())
    builder.adjust(2)
    return builder.as_markup()


from app.services.techs import TECHS

def about_skills_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    skills = list(TECHS.keys())
    for tech_name in skills:
        info = TECHS.get(tech_name)
        if info:
            label = f"{info.emoji} {info.name}"
            builder.button(text=label, callback_data=AboutCallback(action="tech", tech=tech_name).pack())
    
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=AboutCallback(action="main").pack())
    
    sizes = [2] * (len(skills) // 2)
    if len(skills) % 2:
        sizes.append(1)
    sizes.append(2)
    builder.adjust(*sizes)
    return builder.as_markup()


def about_tech_keyboard(official_url: str | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if official_url:
        builder.button(text=text("keyboard.about.official_site"), url=official_url)
    home_button(builder)
    builder.button(text=text("keyboard.back"), callback_data=AboutCallback(action="skills").pack())
    
    sizes = []
    if official_url:
        sizes.append(1)
    sizes.append(2)
    builder.adjust(*sizes)
    return builder.as_markup()
