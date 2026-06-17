from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    approach: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    stack: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    media_group: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    bot_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

