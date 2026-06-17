from aiogram.filters.callback_data import CallbackData


class FaqCallback(CallbackData, prefix="faq"):
    action: str
    question_id: str = ""


class AboutCallback(CallbackData, prefix="about"):
    action: str
    tech: str = ""


class HomeCallback(CallbackData, prefix="home"):
    action: str = "main"


class CasesCallback(CallbackData, prefix="cases"):
    action: str
    case_id: int = 0
    page: int = 0


class CaseStackCallback(CallbackData, prefix="stack"):
    action: str
    case_id: int
    tech: str = ""


class CalculatorCallback(CallbackData, prefix="calc"):
    action: str
    value: str = ""


class CalculatorYesNoCallback(CallbackData, prefix="calc_yn"):
    action: str
    value: bool


class AdminCaseCallback(CallbackData, prefix="admcase"):
    action: str
    case_id: int = 0
    field: str = ""


class AdminFieldCallback(CallbackData, prefix="admfield"):
    field: str

