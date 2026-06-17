from app.config import Settings


def test_admin_ids_accept_comma_separated_string() -> None:
    settings = Settings(
        BOT_TOKEN="token",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db",
        REDIS_URL="redis://localhost:6379/0",
        ADMIN_IDS="1, 2,3",
    )
    assert settings.admin_ids == [1, 2, 3]

