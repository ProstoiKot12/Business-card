from aiogram import Router

from app.bot.routers import about, admin, calculator, cases, contacts, faq, start


def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(cases.router)
    router.include_router(about.router)
    router.include_router(calculator.router)
    router.include_router(faq.router)
    router.include_router(contacts.router)
    router.include_router(admin.router)
    return router

