"""seed Business-card-bot case

Revision ID: 0004_seed_business_card_case
Revises: 0003_seed_upseller_montazh
Create Date: 2026-06-17 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_seed_business_card_case"
down_revision: str | None = "0003_seed_upseller_montazh"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    existing = conn.execute(
        sa.text("SELECT extra_link FROM cases WHERE extra_link = :link"),
        {"link": "https://github.com/ProstoiKot12/Business-card"},
    ).fetchone()
    if existing:
        return

    max_order = conn.execute(sa.text("SELECT COALESCE(MAX(\"order\"), 0) FROM cases")).scalar()

    conn.execute(
        sa.text(
            "INSERT INTO cases "
            "(\"order\", emoji, title, type, task, context, approach, outcome, "
            "stack, media_group, bot_link, extra_link, is_visible) "
            "VALUES "
            "(:order, :emoji, :title, :type, :task, :context, :approach, :outcome, "
            "CAST(:stack AS jsonb), CAST(:media_group AS jsonb), :bot_link, :extra_link, :is_visible)"
        ),
        {
            "order": max_order + 1,
            "emoji": "💼",
            "title": "Визитка-бот",
            "type": "Mini App",
            "task": "Сделать визитку-бот: портфолио кейсов, пошаговый калькулятор стоимости, FAQ и контакты. Клиент заходит в Telegram и получает всё без переходов на сайты.",
            "context": "для показа",
            "approach": (
                "Telegram-бот и Web App в одном процессе: aiogram + FastAPI\n"
                "Кейсы на бесконечной карусели, FAQ в формате чат-симулятора\n"
                "Калькулятор стоимости: FSM в боте, server-driven в Web App\n"
                "Админ-панель через FSM: добавление и сортировка кейсов\n"
                "PostgreSQL + Redis + SQLAlchemy + Alembic\n"
                "Docker Compose для деплоя на VPS"
            ),
            "outcome": "Клиент видит кейсы, получает расчёт стоимости, находит контакты — всё в Telegram. Владелец редактирует портфолио через админ-панель в боте.",
            "stack": '["Python","Aiogram","FastAPI","Jinja2","SQLAlchemy","PostgreSQL","Redis","Alembic","Docker"]',
            "media_group": "[]",
            "bot_link": "https://t.me/gavrilov_dev_bot",
            "extra_link": "https://github.com/ProstoiKot12/Business-card",
            "is_visible": True,
        },
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM cases WHERE extra_link = 'https://github.com/ProstoiKot12/Business-card'"
    )
