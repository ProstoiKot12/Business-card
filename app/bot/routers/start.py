from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.bot.callbacks import HomeCallback
from app.bot.keyboards.inline import main_menu_inline_keyboard
from app.bot.keyboards.reply import HOME_BUTTON, main_menu_keyboard
from app.bot.text_catalog import text
from app.bot.utils import answer_or_edit_with_photo, asset_path
from app.config import Settings, get_settings

router = Router(name="start")
MAIN_MENU_PHOTO = asset_path("main_menu.jpg")


async def send_main_menu(message: Message, settings: Settings) -> None:
    photo = FSInputFile(MAIN_MENU_PHOTO)
    await message.answer(text("main.loading"), reply_markup=main_menu_keyboard())
    await message.answer_photo(
        photo,
        caption=text("main.menu"),
        reply_markup=main_menu_inline_keyboard(),
    )


@router.message(CommandStart())
@router.message(F.text == HOME_BUTTON)
async def start(message: Message, settings: Settings | None = None) -> None:
    await send_main_menu(message, settings or get_settings())


@router.callback_query(HomeCallback.filter(F.action == "main"))
async def callback_home(callback: CallbackQuery) -> None:
    await answer_or_edit_with_photo(
        callback,
        text("main.menu"),
        MAIN_MENU_PHOTO,
        main_menu_inline_keyboard(),
    )
    await callback.answer()
