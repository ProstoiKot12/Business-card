from app.bot.callbacks import CalculatorCallback, CasesCallback, FaqCallback


def test_faq_callback_pack_unpack() -> None:
    packed = FaqCallback(action="item", question_id="price").pack()
    unpacked = FaqCallback.unpack(packed)
    assert unpacked.action == "item"
    assert unpacked.question_id == "price"


def test_cases_callback_pack_unpack() -> None:
    packed = CasesCallback(action="open", case_id=42, page=0).pack()
    unpacked = CasesCallback.unpack(packed)
    assert unpacked.action == "open"
    assert unpacked.case_id == 42


def test_calculator_back_callback_pack_unpack() -> None:
    packed = CalculatorCallback(action="back", value="deadline").pack()
    unpacked = CalculatorCallback.unpack(packed)
    assert unpacked.action == "back"
    assert unpacked.value == "deadline"
