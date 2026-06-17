from app.services.calculator import calculate_price, money


def test_calculate_price_with_integrations_admin_and_urgency() -> None:
    assert calculate_price("sales", integrations=True, admin_panel=True, deadline="urgent") == (6200, 50000)


def test_other_type_is_individual() -> None:
    assert calculate_price("other", integrations=True, admin_panel=True, deadline="urgent") == (0, 25000)


def test_money_formats_rubles() -> None:
    assert money(31200) == "31 200 ₽"

