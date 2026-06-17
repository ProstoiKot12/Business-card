from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks import AboutCallback
from app.bot.keyboards.inline import about_detail_keyboard, about_keyboard, about_skills_keyboard, about_tech_keyboard
from app.bot.text_catalog import html_text, text
from app.bot.utils import answer_or_edit_with_photo, asset_path
from app.config import get_settings
from app.services.techs import get_tech_info

router = Router(name="about")
ABOUT_PHOTO = asset_path("about_menu.jpg")
SKILLS_PHOTO = asset_path("skills_menu.jpg")
EXPERIENCE_PHOTO = asset_path("experience_menu.jpg")


def render_about_main():
    settings = get_settings()
    return html_text("about.main", owner_name=settings.owner_name), about_keyboard(settings.owner_telegram_url, settings.owner_github_url)


@router.message(F.text == text("keyboard.main.about"))
async def about(message: Message) -> None:
    text, keyboard = render_about_main()
    await answer_or_edit_with_photo(message, text, ABOUT_PHOTO, keyboard)


@router.callback_query(AboutCallback.filter(F.action == "main"))
async def about_main_callback(callback: CallbackQuery) -> None:
    text, keyboard = render_about_main()
    await answer_or_edit_with_photo(callback, text, ABOUT_PHOTO, keyboard)
    await callback.answer()


@router.callback_query(AboutCallback.filter(F.action == "skills"))
async def about_skills_callback(callback: CallbackQuery) -> None:
    await answer_or_edit_with_photo(callback, text("about.skills"), SKILLS_PHOTO, about_skills_keyboard())
    await callback.answer()


@router.callback_query(AboutCallback.filter(F.action == "tech"))
async def about_tech_callback(callback: CallbackQuery, callback_data: AboutCallback) -> None:
    info = get_tech_info(callback_data.tech)
    await answer_or_edit_with_photo(
        callback,
        html_text("about.tech", emoji=info.emoji, name=info.name, desc=info.desc, reason=info.reason),
        SKILLS_PHOTO,
        about_tech_keyboard(info.url),
    )
    await callback.answer()


@router.callback_query(AboutCallback.filter(F.action == "experience"))
async def about_detail(callback: CallbackQuery, callback_data: AboutCallback) -> None:
    await answer_or_edit_with_photo(callback, text("about.experience"), EXPERIENCE_PHOTO, about_detail_keyboard())
    await callback.answer()
