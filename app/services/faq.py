from dataclasses import dataclass

from app.bot.text_catalog import text


@dataclass(frozen=True)
class FaqItem:
    id: str
    title: str
    answer: str


FAQ_IDS = ("services", "support", "time", "warranty", "price")

FAQ_ITEMS = [
    FaqItem(
        id=item_id,
        title=text(f"faq.{item_id}.title"),
        answer=text(f"faq.{item_id}.answer"),
    )
    for item_id in FAQ_IDS
]