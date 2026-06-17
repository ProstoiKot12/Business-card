from dataclasses import dataclass

from app.services.calculator_config import (
    BOT_TYPES as _BOT_TYPES,
    DEADLINES as _DEADLINES,
    WIZARD_STEPS,
)


@dataclass(frozen=True)
class PriceItem:
    title: str
    min_price: int
    max_price: int


@dataclass(frozen=True)
class DeadlineItem:
    title: str
    multiplier: float


@dataclass(frozen=True)
class StepChoice:
    value: str
    title: str


@dataclass(frozen=True)
class CalculatorStep:
    id: str
    label: str
    prompt: str
    hint: str
    field: str
    choices: tuple[StepChoice, ...] | None = None
    yes_label: str = ""
    no_label: str = ""
    next_step_id: str | None = None


# ── Строим PriceItem / DeadlineItem из конфига ──

BOT_TYPES = {
    key: PriceItem(title=cfg["title"], min_price=cfg["min"], max_price=cfg["max"])
    for key, cfg in _BOT_TYPES.items()
}

DEADLINES = {
    key: DeadlineItem(title=cfg["title"], multiplier=cfg["multiplier"])
    for key, cfg in _DEADLINES.items()
}


# ── Строим словарь надбавок из yes/no шагов ──

_SURCHARGES: dict[str, tuple[int, int]] = {}
for step_cfg in WIZARD_STEPS:
    if step_cfg.get("type") == "yesno" and "surcharge" in step_cfg:
        _SURCHARGES[step_cfg["field"]] = tuple(step_cfg["surcharge"])


# ── Строим CALCULATOR_WIZARD из конфига ──

_choices_sources = {
    "bot_type": tuple(StepChoice(key, BOT_TYPES[key].title) for key in BOT_TYPES),
    "deadline": tuple(StepChoice(key, DEADLINES[key].title) for key in DEADLINES),
}


def _build_choices(step_cfg: dict) -> tuple[StepChoice, ...] | None:
    if step_cfg.get("type") != "choices":
        return None
    if "choices" in step_cfg:
        return tuple(StepChoice(c["value"], c["title"]) for c in step_cfg["choices"])
    return _choices_sources.get(step_cfg["id"])


_step_list = []
for i, step_cfg in enumerate(WIZARD_STEPS):
    sid = step_cfg["id"]
    next_id = WIZARD_STEPS[i + 1]["id"] if i + 1 < len(WIZARD_STEPS) else None
    _step_list.append(CalculatorStep(
        id=sid,
        label=step_cfg.get("label", sid),
        prompt=step_cfg["question"],
        hint=step_cfg["hint"],
        field=step_cfg["field"],
        choices=_build_choices(step_cfg),
        yes_label=step_cfg.get("yes_label", ""),
        no_label=step_cfg.get("no_label", ""),
        next_step_id=next_id,
    ))
CALCULATOR_WIZARD: tuple[CalculatorStep, ...] = tuple(_step_list)

_WIZARD_INDEX: dict[str, int] = {step.id: i for i, step in enumerate(CALCULATOR_WIZARD)}


def _step_by_id(step_id: str) -> CalculatorStep | None:
    idx = _WIZARD_INDEX.get(step_id)
    return CALCULATOR_WIZARD[idx] if idx is not None else None


def wizard_step(step_id: str, data: dict, value: object) -> tuple[CalculatorStep | None, dict | None]:
    current = _step_by_id(step_id)
    if current is None:
        return None, {"step": "unknown_step"}

    errors = _validate(current, value)
    if errors:
        return current, errors

    data[current.field] = value
    if current.next_step_id is None:
        return None, None
    return _step_by_id(current.next_step_id), None


def wizard_back(step_id: str) -> CalculatorStep | None:
    idx = _WIZARD_INDEX.get(step_id)
    if idx is None or idx == 0:
        return None
    return CALCULATOR_WIZARD[idx - 1]


def wizard_start() -> CalculatorStep:
    return CALCULATOR_WIZARD[0]


def wizard_compute(data: dict) -> tuple[int, int] | None:
    return calculate_price(
        bot_type=str(data.get("bot_type", "")),
        integrations=bool(data.get("integrations", False)),
        admin_panel=bool(data.get("admin_panel", False)),
        deadline=str(data.get("deadline", "")),
        **{k: bool(v) for k, v in data.items() if k not in ("bot_type", "integrations", "admin_panel", "deadline")},
    )


def _validate(step: CalculatorStep, value: object) -> dict | None:
    if step.choices is not None:
        valid_values = {c.value for c in step.choices}
        if str(value) not in valid_values:
            return {"value": "invalid_choice"}
    elif isinstance(value, bool):
        pass
    else:
        return {"value": "expected_bool"}
    return None


def calculate_price(bot_type: str, integrations: bool, admin_panel: bool, deadline: str, **extra: bool) -> tuple[int, int]:
    item = BOT_TYPES[bot_type]

    min_price = item.min_price
    max_price = item.max_price

    # Применяем все yes/no надбавки
    all_data = {"integrations": integrations, "admin_panel": admin_panel, **extra}
    for field, (surge_min, surge_max) in _SURCHARGES.items():
        if all_data.get(field):
            min_price += surge_min
            max_price += surge_max

    multiplier = DEADLINES[deadline].multiplier
    return round(min_price * multiplier / 100) * 100, round(max_price * multiplier / 100) * 100


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"