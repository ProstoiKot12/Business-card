from app.db.models import Case
from app.services.cases import format_case_card, get_neighbor_case_ids


def make_case(case_id: int, title: str = "Test") -> Case:
    return Case(
        id=case_id,
        order=case_id,
        emoji="🤖",
        title=title,
        type="AI-бот",
        task="Задача",
        context="для тестов",
        approach="Функция 1\n- Функция 2",
        outcome="Результат",
        stack=["Python"],
        media_group=[],
        bot_link=None,
        extra_link=None,
        is_visible=True,
    )


def test_format_case_card_normalizes_approach_lines() -> None:
    text = format_case_card(make_case(1, "<unsafe>"))
    assert "&lt;unsafe&gt;" in text
    assert "- Функция 1" in text
    assert "- Функция 2" in text


def test_neighbor_case_ids_are_cyclic() -> None:
    cases = [make_case(1), make_case(2), make_case(3)]
    assert get_neighbor_case_ids(cases, 1) == (3, 2)
    assert get_neighbor_case_ids(cases, 3) == (2, 1)

