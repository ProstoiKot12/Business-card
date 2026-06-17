from dataclasses import dataclass

from app.bot.text_catalog import text


@dataclass(frozen=True)
class TechInfo:
    name: str
    emoji: str
    svg_file: str
    desc: str
    reason: str
    url: str


TECH_KEYS = {
    "Python": "Python",
    "Aiogram": "Aiogram",
    "SQLAlchemy": "SQLAlchemy",
    "PostgreSQL": "PostgreSQL",
    "Redis": "Redis",
    "Docker": "Docker",
    "FastAPI": "FastAPI",
    "Django": "Django",
    "Celery": "Celery",
    "Dramatiq": "Dramatiq",
    "Kubernetes": "Kubernetes",
    "RabbitMQ": "RabbitMQ",
    "Git": "Git",
    "AI": "AI",
    "APScheduler": "APScheduler",
    "Google Sheets API": "Google Sheets API",
    "Trello API": "Trello API",
    "AmoCRM API": "AmoCRM API",
    "YooKassa": "YooKassa",
    "T-Bank": "T-Bank",
    "Yandex Maps": "Yandex Maps",
    "Yandex GPT": "Yandex GPT",
    "Google Calendar": "Google Calendar",
    "Jinja2": "Jinja2",
    "Alembic": "Alembic",
}

# Icon file extensions: most are .svg, a few are .png (official logo)
_ICON_EXT = {
    "YooKassa": ".png",
}

# Icon file basenames: for techs where key.lower() != filename stem
_ICON_FILE = {
    "Google Sheets API": "googlesheets",
    "Trello API": "trello",
    "AmoCRM API": "amocrm",
    "T-Bank": "tbank",
    "Yandex Maps": "yandexmaps",
    "Yandex GPT": "yandexcloud",
    "Google Calendar": "googlecalendar",
}


def _tech_from_key(key: str) -> TechInfo:
    ext = _ICON_EXT.get(key, ".svg")
    stem = _ICON_FILE.get(key, key.lower())
    return TechInfo(
        name=text(f"tech.{key}.name"),
        emoji=text(f"tech.{key}.emoji"),
        svg_file=f"/static/icons/tech/{stem}{ext}",
        desc=text(f"tech.{key}.desc"),
        reason=text(f"tech.{key}.reason"),
        url=text(f"tech.{key}.url"),
    )


TECHS = {name: _tech_from_key(key) for name, key in TECH_KEYS.items()}


def get_tech_info(name: str) -> TechInfo:
    if name in TECHS:
        return TECHS[name]
    return TechInfo(
        name=name,
        emoji=text("tech.default.emoji"),
        svg_file="/static/icons/tech/default.svg",
        desc=text("tech.default.desc"),
        reason=text("tech.default.reason"),
        url="",
    )


FEATURED_TECH_STACK = (
    "Python",
    "FastAPI",
    "Aiogram",
    "SQLAlchemy",
    "PostgreSQL",
    "Redis",
    "Docker",
    "Django",
    "Celery",
    "Dramatiq",
    "Kubernetes",
    "RabbitMQ",
    "Git",
    "AI",
)