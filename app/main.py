import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.bot.middlewares import DbSessionMiddleware
from app.bot.routers import setup_routers
from app.bot.text_catalog import text
from app.config import get_settings
from app.db.session import create_sessionmaker


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.remove()
    logger.add(lambda message: print(message, end=""), level=settings.log_level)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)
    sessionmaker = create_sessionmaker(settings)

    dp.update.middleware(DbSessionMiddleware(sessionmaker))
    dp.include_router(setup_routers())

    logger.info("Bot started")
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description=text("system.command.start.description"))
        ])
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Web App", web_app=WebAppInfo(url=settings.webapp_url))
        )
        await bot.send_message(
            chat_id=settings.owner_id,
            text=text("system.startup.owner_message"),
        )
    except Exception as e:
        logger.error(f"Failed to send startup message: {e}")

    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(dp.start_polling(bot, settings=settings))

    yield

    logger.info("Bot is shutting down")
    try:
        await bot.send_message(
            chat_id=settings.owner_id,
            text=text("system.shutdown.owner_message"),
        )
    except Exception as e:
        logger.error(f"Failed to send shutdown message: {e}")

    polling_task.cancel()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "webapp" / "static"), name="static")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "bot" / "assets"), name="assets")

from app.webapp.routes import router as webapp_router
app.include_router(webapp_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
