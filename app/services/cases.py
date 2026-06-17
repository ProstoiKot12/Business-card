from app.bot.text_catalog import html_text
from app.db.models import Case


def format_case_card(case: Case) -> str:
    approach_lines = [line.strip() for line in case.approach.splitlines() if line.strip()]
    approach = "\n".join(line if line.startswith("-") else f"- {line}" for line in approach_lines)
    return html_text(
        "cases.card",
        emoji=case.emoji,
        title=case.title,
        case_type=case.type,
        task=case.task,
        solution=approach,
        result=case.outcome,
    )


def format_stack(case: Case) -> str:
    return html_text("cases.stack", case_title=case.title)


from app.services.techs import TechInfo

def format_technology(info: TechInfo) -> str:
    return html_text("cases.technology", emoji=info.emoji, name=info.name, desc=info.desc, reason=info.reason)


def get_neighbor_case_ids(cases: list[Case], case_id: int) -> tuple[int, int]:
    ids = [case.id for case in cases]
    index = ids.index(case_id)
    return ids[(index - 1) % len(ids)], ids[(index + 1) % len(ids)]
