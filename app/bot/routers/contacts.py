from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.callbacks import CalculatorCallback, FaqCallback
from app.bot.keyboards.inline import contacts_keyboard
from app.bot.text_catalog import text
from app.bot.utils import answer_or_edit_with_photo, asset_path
from app.config import Settings, get_settings

router = Router(name="contacts")
CONTACTS_PHOTO = asset_path("contacts_menu.jpg")


def render_contacts(settings: Settings):
    return text("contacts.main"), contacts_keyboard(settings.owner_telegram_url, settings.owner_max_url)


@router.message(F.text == text("keyboard.main.contacts"))
async def contacts(message: Message) -> None:
    settings = get_settings()
    text, keyboard = render_contacts(settings)
    await answer_or_edit_with_photo(message, text, CONTACTS_PHOTO, keyboard)


@router.callback_query(FaqCallback.filter(F.action == "contact"))
@router.callback_query(CalculatorCallback.filter(F.action == "contact"))
async def contacts_callback(callback: CallbackQuery) -> None:
    settings = get_settings()
    text, keyboard = render_contacts(settings)
    await answer_or_edit_with_photo(callback, text, CONTACTS_PHOTO, keyboard)
    await callback.answer()
