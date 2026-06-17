from pathlib import Path

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto, Message

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(filename: str) -> str:
    return str(ASSETS_DIR / filename)


async def answer_or_edit(
    target: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message | bool | None:
    message = target.message if isinstance(target, CallbackQuery) else target
    if message is None:
        return None
    try:
        if message.photo:
            return await message.edit_caption(caption=text, reply_markup=reply_markup)
        return await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        return await message.answer(text, reply_markup=reply_markup)


async def answer_or_edit_with_photo(
    target: Message | CallbackQuery,
    text: str,
    photo_path: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message | bool | None:
    message = target.message if isinstance(target, CallbackQuery) else target
    if message is None:
        return None

    media = InputMediaPhoto(media=FSInputFile(photo_path), caption=text)
    try:
        return await message.edit_media(media=media, reply_markup=reply_markup)
    except TelegramBadRequest:
        return await message.answer_photo(FSInputFile(photo_path), caption=text, reply_markup=reply_markup)


async def edit_case_media(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup,
    media_group: list[str],
) -> Message | bool:
    if media_group:
        media = InputMediaPhoto(media=media_group[0], caption=text)
        try:
            return await message.edit_media(media=media, reply_markup=reply_markup)
        except TelegramBadRequest:
            return await message.answer_photo(media_group[0], caption=text, reply_markup=reply_markup)
    return await answer_or_edit(message, text, reply_markup)
