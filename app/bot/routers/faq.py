from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks import FaqCallback
from app.bot.keyboards.inline import faq_answer_keyboard, faq_final_keyboard, faq_menu_keyboard
from app.bot.text_catalog import text
from app.bot.utils import answer_or_edit_with_photo, asset_path
from app.config import get_settings
from app.services.faq import FAQ_ITEMS

router = Router(name="faq")
FAQ_PHOTO = asset_path("faq_menu.jpg")

FAQ_MENU_TEXT = text("faq.menu")


@router.message(F.text == text("keyboard.main.faq"))
async def faq(message: Message) -> None:
    await answer_or_edit_with_photo(message, FAQ_MENU_TEXT, FAQ_PHOTO, faq_menu_keyboard())


@router.callback_query(FaqCallback.filter(F.action == "list"))
async def faq_list(callback: CallbackQuery) -> None:
    await answer_or_edit_with_photo(callback, FAQ_MENU_TEXT, FAQ_PHOTO, faq_menu_keyboard())
    await callback.answer()


@router.callback_query(FaqCallback.filter(F.action == "item"))
async def faq_item(callback: CallbackQuery, callback_data: FaqCallback) -> None:
    item = next((item for item in FAQ_ITEMS if item.id == callback_data.question_id), None)
    if item is None:
        await callback.answer(text("faq.not_found"), show_alert=True)
        return
    text = f"<b>{escape(item.title)}</b>\n\n{item.answer}"
    await answer_or_edit_with_photo(callback, text, FAQ_PHOTO, faq_answer_keyboard(item.id))
    await callback.answer()


@router.callback_query(FaqCallback.filter(F.action == "final"))
async def faq_final(callback: CallbackQuery) -> None:
    settings = get_settings()
    await answer_or_edit_with_photo(
        callback,
        text("faq.final"),
        FAQ_PHOTO,
        faq_final_keyboard(settings.owner_telegram_url),
    )
    await callback.answer()
