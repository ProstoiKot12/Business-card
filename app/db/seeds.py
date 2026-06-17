from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.text_catalog import text, text_lines
from app.db.models import Case


DEMO_CASE_IDS = (1, 2, 3, 4, 5, 6, 7)

DEMO_EXTRA_LINKS: dict[int, str] = {
    6: "https://github.com/ProstoiKot12/Upseller-Bot",
    7: "https://github.com/ProstoiKot12/MontazhP",
}


def _demo_case(case_id: int) -> dict:
    return {
        "order": case_id,
        "emoji": text(f"demo.case.{case_id}.emoji"),
        "title": text(f"demo.case.{case_id}.title"),
        "type": text(f"demo.case.{case_id}.type"),
        "task": text(f"demo.case.{case_id}.task"),
        "context": text(f"demo.case.{case_id}.context"),
        "approach": text(f"demo.case.{case_id}.approach"),
        "outcome": text(f"demo.case.{case_id}.outcome"),
        "stack": text_lines(f"demo.case.{case_id}.stack"),
        "media_group": [],
        "bot_link": None,
        "extra_link": DEMO_EXTRA_LINKS.get(case_id),
        "is_visible": True,
    }


DEMO_CASES = [_demo_case(case_id) for case_id in DEMO_CASE_IDS]


async def seed_demo_cases(session: AsyncSession) -> None:
    exists = await session.scalar(select(Case.id).limit(1))
    if exists:
        return
    session.add_all(Case(**item) for item in DEMO_CASES)
    await session.commit()
