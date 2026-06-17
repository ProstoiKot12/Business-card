"""seed Upseller-Bot and MontazhP cases

Revision ID: 0003_seed_upseller_montazh
Revises: 0002_rename_case_fields
Create Date: 2026-06-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_seed_upseller_montazh"
down_revision: str | None = "0002_rename_case_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INSERT_SQL = sa.text(
    """INSERT INTO cases (
        "order", emoji, title, type, task, context, approach, outcome,
        stack, media_group, bot_link, extra_link, is_visible
    ) VALUES (
        :order, :emoji, :title, :type, :task, :context, :approach, :outcome,
        CAST(:stack AS jsonb), CAST(:media_group AS jsonb), :bot_link, :extra_link, :is_visible
    )"""
)

CASES = [
    {
        "order": 1,
        "emoji": "📦",
        "title": "Upseller",
        "type": "Бот-платформа",
        "task": (
            "Построить единую систему управления складом: от приёмки до отгрузки,"
            " с контролем менеджеров, SLA по клиентским чатам и автоматическими отчётами."
        ),
        "context": "для логистической компании",
        "approach": (
            "Ролевые сценарии для админа, менеджера и логиста\n"
            "Учёт приёмки, сборки, упаковки и отгрузки\n"
            "Контроль SLA в клиентских чатах с напоминаниями\n"
            "Интеграция с Google Sheets и Trello\n"
            "Автоматические отчёты и квартальные опросы клиентов"
        ),
        "outcome": "Менеджеры видят задачи в Telegram, руководство получает ежедневную аналитику автоматически.",
        "stack": '["Python","Aiogram","SQLAlchemy","PostgreSQL","Redis","APScheduler","Google Sheets API","Trello API","Git"]',
        "media_group": "[]",
        "bot_link": None,
        "extra_link": "https://github.com/ProstoiKot12/Upseller-Bot",
        "is_visible": True,
    },
    {
        "order": 2,
        "emoji": "🔧",
        "title": "Montazhp",
        "type": "Бот-сервис",
        "task": (
            "Автоматизировать весь цикл, от заявки до выезда мастера и оплаты:"
            " расчёт стоимости, бронирование, оплата, геолокация и CRM."
        ),
        "context": "для сервиса монтажа в СПб",
        "approach": (
            "Оформление заявки с расчётом цены и AI-консультантом\n"
            "Онлайн-запись на свободную дату с предоплатой\n"
            "Кабинет мастера: заказы, график, фото отчёты, live-геолокация\n"
            "Синхронизация с AmoCRM, приём платежей T-Bank / YooKassa\n"
            "Админ-дашборд, рассылки и ежедневная отчётность"
        ),
        "outcome": (
            "За полтора года в production: 1700+ заказов."
            " Клиент оформляет заявку и оплачивает сам, мастер ведёт работу через Telegram."
        ),
        "stack": '["Python","Aiogram","SQLAlchemy","PostgreSQL","Redis","Docker","AmoCRM API","YooKassa","T-Bank","Yandex Maps","Yandex GPT","Google Calendar","Git"]',
        "media_group": "[]",
        "bot_link": "https://t.me/montazhpbot",
        "extra_link": "https://github.com/ProstoiKot12/MontazhP",
        "is_visible": True,
    },
]


def upgrade() -> None:
    conn = op.get_bind()

    existing = conn.execute(
        sa.text("SELECT extra_link FROM cases WHERE extra_link IN (:a, :b)"),
        {
            "a": "https://github.com/ProstoiKot12/Upseller-Bot",
            "b": "https://github.com/ProstoiKot12/MontazhP",
        },
    ).fetchall()
    existing_links = {row[0] for row in existing}

    max_order = conn.execute(sa.text("SELECT COALESCE(MAX(\"order\"), 0) FROM cases")).scalar()

    for case in CASES:
        if case["extra_link"] in existing_links:
            continue
        max_order += 1
        params = {**case, "order": max_order}
        conn.execute(_INSERT_SQL, params)


def downgrade() -> None:
    op.execute(
        "DELETE FROM cases WHERE extra_link IN "
        "('https://github.com/ProstoiKot12/Upseller-Bot', "
        "'https://github.com/ProstoiKot12/MontazhP')"
    )
