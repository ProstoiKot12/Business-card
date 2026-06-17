"""Stateless CaseEditor — инкапсулирует wizard добавления/редактирования Кейса.

Не зависит от Aiogram/Telegram. Вызывается хендлерами как step() → StepResult.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from app.bot.text_catalog import text, text_lines


class CaseEditStepID(StrEnum):
    TITLE = "title"
    TYPE = "type"
    OTHER_TYPE = "other_type"
    EMOJI = "emoji"
    TASK = "task"
    CONTEXT = "context"
    APPROACH = "approach"
    OUTCOME = "outcome"
    STACK = "stack"
    MEDIA = "media"
    BOT_LINK = "bot_link"
    EXTRA_LINK = "extra_link"
    PREVIEW = "preview"


@dataclass(frozen=True)
class CaseEditStep:
    id: CaseEditStepID
    prompt_key: str
    field: str
    required: bool = True
    choices: tuple[str, ...] | None = None  # None = free text; tuple = fixed choices
    next_step_id: CaseEditStepID | None = None  # None = last before preview


ADD_FLOW: tuple[CaseEditStep, ...] = (
    CaseEditStep(CaseEditStepID.TITLE, "admin.add.step1.title", "title", next_step_id=CaseEditStepID.TYPE),
    CaseEditStep(CaseEditStepID.TYPE, "admin.case.choose_type", "type", choices=("ai", "sales", "mini_app", "crm", "other"), next_step_id=CaseEditStepID.EMOJI),
    CaseEditStep(CaseEditStepID.EMOJI, "admin.add.step2.emoji", "emoji", next_step_id=CaseEditStepID.CONTEXT),
    CaseEditStep(CaseEditStepID.CONTEXT, "admin.add.step3.context", "context", next_step_id=CaseEditStepID.TASK),
    CaseEditStep(CaseEditStepID.TASK, "admin.add.step4.task", "task", next_step_id=CaseEditStepID.APPROACH),
    CaseEditStep(CaseEditStepID.APPROACH, "admin.add.step5.approach", "approach", next_step_id=CaseEditStepID.OUTCOME),
    CaseEditStep(CaseEditStepID.OUTCOME, "admin.add.step6.outcome", "outcome", next_step_id=CaseEditStepID.STACK),
    CaseEditStep(CaseEditStepID.STACK, "admin.add.step7.stack", "stack", required=False, next_step_id=CaseEditStepID.MEDIA),
    CaseEditStep(CaseEditStepID.MEDIA, "admin.add.step8.media", "media_group", required=False, next_step_id=CaseEditStepID.BOT_LINK),
    CaseEditStep(CaseEditStepID.BOT_LINK, "admin.link.bot", "bot_link", required=False, next_step_id=CaseEditStepID.EXTRA_LINK),
    CaseEditStep(CaseEditStepID.EXTRA_LINK, "admin.link.extra", "extra_link", required=False, next_step_id=None),
)

_FLOW_INDEX: dict[CaseEditStepID, int] = {step.id: i for i, step in enumerate(ADD_FLOW)}

CASE_TYPE_CHOICES = ("ai", "sales", "mini_app", "crm", "other")


@dataclass
class StepResult:
    next_step: CaseEditStepID | None  # None = готово к preview/save
    errors: dict[str, str] | None = None
    extra: dict | None = None  # e.g. {"custom_type": True} when type=other


def normalize_optional_link(value: str) -> str | None:
    value = value.strip()
    if value in {"", *text_lines("admin.optional.none_values")}:
        return None
    if value.startswith("t.me/"):
        return f"https://{value}"
    return value


def step(step_id: str, draft: dict, value: object, *, is_edit: bool = False) -> StepResult:
    """Применяет значение к текущему шагу, возвращает результат."""
    sid = CaseEditStepID(step_id)
    current = _step_by_id(sid)
    if current is None:
        return StepResult(next_step=None, errors={"step": "unknown_step"})

    value = _coerce_value(current, value)

    # type=other redirects to OTHER_TYPE
    if sid == CaseEditStepID.TYPE and str(value) == "other" and not is_edit:
        return StepResult(next_step=CaseEditStepID.OTHER_TYPE, extra={"custom_type": True})

    errors = _validate(current, value)
    if errors:
        return StepResult(next_step=sid, errors=errors)

    draft[current.field] = value

    if current.next_step_id is None:
        return StepResult(next_step=None)

    return StepResult(next_step=current.next_step_id)


def to_case_data(draft: dict) -> dict:
    """Конвертирует черновик в данные для Case(**data)."""
    return {
        "emoji": str(draft.get("emoji", ""))[:8],
        "title": str(draft.get("title", "")).strip(),
        "type": str(draft.get("type", "")).strip(),
        "task": str(draft.get("task", "")).strip(),
        "context": str(draft.get("context", "")).strip(),
        "approach": str(draft.get("approach", "")).strip(),
        "outcome": str(draft.get("outcome", "")).strip(),
        "stack": list(draft.get("stack", [])),
        "media_group": list(draft.get("media_group", [])),
        "bot_link": normalize_optional_link(str(draft.get("bot_link", ""))),
        "extra_link": normalize_optional_link(str(draft.get("extra_link", ""))),
        "is_visible": True,
    }


def start() -> StepResult:
    return StepResult(next_step=ADD_FLOW[0].id)


def _step_by_id(sid: CaseEditStepID) -> CaseEditStep | None:
    idx = _FLOW_INDEX.get(sid)
    return ADD_FLOW[idx] if idx is not None else None


def _coerce_value(step_def: CaseEditStep, value: object) -> object:
    if step_def.field in ("stack", "media_group"):
        return value  # handled externally
    if step_def.field in ("bot_link", "extra_link"):
        s = str(value).strip()
        return None if s == "" else s
    if isinstance(value, bool):
        return value
    return str(value).strip()


def _validate(step_def: CaseEditStep, value: object) -> dict | None:
    if step_def.required and not value:
        return {"value": "required"}

    if step_def.choices is not None and value:
        if str(value) not in step_def.choices and str(value) != "other":
            return {"value": "invalid_choice"}

    if step_def.id == CaseEditStepID.EMOJI and value:
        if len(str(value)) > 8:
            return {"value": "emoji_too_long"}

    return None