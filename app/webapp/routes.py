import json
import re

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.db.session import get_session
from app.db.repositories import CaseRepository
from app.bot.text_catalog import text
from app.services.techs import TECHS, FEATURED_TECH_STACK, get_tech_info
from app.services.calculator import BOT_TYPES, DEADLINES, CALCULATOR_WIZARD, wizard_back, wizard_compute, wizard_start, wizard_step
from app.services.faq import FAQ_ITEMS
from app.config import get_settings

router = APIRouter(tags=["webapp"])

# Get the path to the templates directory
current_dir = Path(__file__).parent
templates_dir = current_dir / "templates"

templates = Jinja2Templates(directory=templates_dir)


def render_htmx_or_full(request: Request, template_name: str, context: dict, status_code: int = 200):
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            request, template_name, context, status_code=status_code
        )

    # If full page load, wrap in base.html
    context["main_content_template"] = template_name
    return templates.TemplateResponse(
        request, "base.html", context, status_code=status_code
    )


def about_context(request: Request) -> dict:
    settings = get_settings()
    about_main = text("about.main", owner_name=settings.owner_name)
    about_experience = text("about.experience")
    # Remove title/Format/Status lines — already in the hero
    about_main_body = about_main.replace("<b>👤 Обо мне</b>\n\n", "", 1)
    about_main_body = re.sub(r"<b>📍 Формат:</b>.*?\n", "", about_main_body)
    about_main_body = re.sub(r"<b>🟢 Статус:</b>.*?\n?", "", about_main_body)
    # Remove emoji from bold headings (e.g. <b>🚀 Что я умею:</b> → <b>Что я умею:</b>)
    about_main_body = re.sub(
        r'(<b>)[^\w<]+(\w)',
        lambda m: m.group(1) + m.group(2),
        about_main_body
    )
    # Parse experience into intro + structured timeline nodes
    exp_body = about_experience.replace("<b>📈 Опыт</b>\n\n", "", 1)
    experience_stages = ("Старт", "Развитие", "Сейчас")
    timeline: list[dict] = []
    experience_intro = ""
    blocks = re.split(r'<b>([^<]+)</b>', exp_body)
    # blocks[0] = text before first <b> — the intro paragraph
    if blocks and blocks[0].strip():
        experience_intro = blocks[0].strip()
    for i in range(1, len(blocks), 2):
        title = re.sub(r'[^\w\s:]+', '', blocks[i]).strip().rstrip(':')
        body = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
        if title.startswith(experience_stages):
            timeline.append({"title": title, "text": body})
    return {
        "request": request,
        "active_tab": "about",
        "owner_name": settings.owner_name,
        "about_main": about_main_body,
        "experience_intro": experience_intro,
        "experience_timeline": timeline,
        "tech_stack": [TECHS[name] for name in FEATURED_TECH_STACK],
    }


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_htmx_or_full(request, "components/about.html", about_context(request))


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return render_htmx_or_full(request, "components/about.html", about_context(request))


@router.get("/cases", response_class=HTMLResponse)
async def cases(request: Request, session: AsyncSession = Depends(get_session)):
    repo = CaseRepository(session)
    visible_cases = await repo.list_visible()
    techs_data = {
        name: {"emoji": t.emoji, "desc": t.desc, "reason": t.reason}
        for name, t in TECHS.items()
    }
    icon_slugs = {
        # devicon CDN (color originals)
        "Python": "https://cdn.jsdelivr.net/npm/devicon@2/icons/python/python-original.svg",
        "PostgreSQL": "https://cdn.jsdelivr.net/npm/devicon@2/icons/postgresql/postgresql-original.svg",
        "Redis": "https://cdn.jsdelivr.net/npm/devicon@2/icons/redis/redis-original.svg",
        "Docker": "https://cdn.jsdelivr.net/npm/devicon@2/icons/docker/docker-original.svg",
        "FastAPI": "https://cdn.jsdelivr.net/npm/devicon@2/icons/fastapi/fastapi-original.svg",
        "Django": "https://cdn.jsdelivr.net/npm/devicon@2/icons/django/django-plain.svg",
        "Kubernetes": "https://cdn.jsdelivr.net/npm/devicon@2/icons/kubernetes/kubernetes-original.svg",
        "Git": "https://cdn.jsdelivr.net/npm/devicon@2/icons/git/git-original.svg",
        "SQLAlchemy": "https://cdn.jsdelivr.net/npm/devicon@2/icons/sqlalchemy/sqlalchemy-original.svg",
        # local — official + custom colored SVGs
        "Aiogram": "/static/icons/tech/aiogram.svg",
        "Trello API": "/static/icons/tech/trello.svg",
        "Google Sheets API": "/static/icons/tech/googlesheets.svg",
        "Google Calendar": "/static/icons/tech/googlecalendar.svg",
        "Yandex Maps": "/static/icons/tech/yandexmaps.svg",
        "Yandex GPT": "/static/icons/tech/yandexcloud.svg",
        "AmoCRM API": "/static/icons/tech/amocrm.svg",
        "YooKassa": "/static/icons/tech/yookassa.png",
        "T-Bank": "/static/icons/tech/tbank.svg",
        "APScheduler": "/static/icons/tech/apscheduler.svg",
    }
    return render_htmx_or_full(
        request,
        "components/cases.html",
        {
            "request": request,
            "cases": visible_cases,
            "active_tab": "cases",
            "techs_json": json.dumps(techs_data, ensure_ascii=False),
            "icon_slugs": icon_slugs,
        }
    )


@router.get("/calculator", response_class=HTMLResponse)
async def calculator(request: Request):
    wizard_resolved = [
        {
            "id": step.id,
            "label": step.label,
            "prompt": step.prompt,
            "hint": step.hint,
            "field": step.field,
            "choices": [{"value": c.value, "title": c.title} for c in step.choices] if step.choices else None,
            "yes_label": step.yes_label,
            "no_label": step.no_label,
        }
        for step in CALCULATOR_WIZARD
    ]
    return render_htmx_or_full(
        request,
        "components/calculator.html",
        {
            "request": request,
            "bot_types": BOT_TYPES,
            "deadlines": DEADLINES,
            "wizard": wizard_resolved,
            "active_tab": "calculator"
        }
    )


@router.post("/calculator/step")
async def calculator_step(request: Request):
    import json
    body = await request.json()
    step_id = body.get("step_id", "")
    value = body.get("value")
    data = body.get("data", {})

    if step_id == "back":
        previous = wizard_back(body.get("current_step", ""))
        if previous is None:
            return {"error": "no_previous_step"}
        return _step_response(previous, data)

    next_step, errors = wizard_step(step_id, data, value)
    if errors:
        return {"error": "validation_failed", "details": errors}

    if next_step is None or next_step.id == "result":
        result = wizard_compute(data)
        breakdown = _build_breakdown(data)
        return {"done": True, "result": result, "data": data, "breakdown": breakdown}

    return _step_response(next_step, data)


def _build_breakdown(data: dict) -> list[dict]:
    """Строит список всех выборов для отображения в итоге."""
    items = []
    for step in CALCULATOR_WIZARD:
        if step.id == "result" or step.field == "result":
            continue
        value = data.get(step.field)
        if value is None:
            continue
        if step.choices:
            # choices-шаг: ищем название выбранного варианта
            display = str(value)
            for c in step.choices:
                if c.value == str(value):
                    display = c.title
                    break
        else:
            # yesno-шаг
            display = step.yes_label if value else step.no_label
        items.append({"label": step.label, "value": display})
    return items


def _step_response(step, data):
    return {
        "step": {
            "id": step.id,
            "label": step.label,
            "prompt": step.prompt,
            "hint": step.hint,
            "field": step.field,
            "choices": [{"value": c.value, "title": c.title} for c in step.choices] if step.choices else None,
            "yes_label": step.yes_label,
            "no_label": step.no_label,
        },
        "data": data,
        "done": False,
    }


@router.get("/contacts", response_class=HTMLResponse)
async def contacts(request: Request):
    settings = get_settings()
    return render_htmx_or_full(
        request, 
        "components/contacts.html", 
        {
            "request": request, 
            "settings": settings,
            "active_tab": "contacts"
        }
    )


@router.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    settings = get_settings()
    faq_items_json = json.dumps([
        {
            "id": item.id,
            "title": item.title,
            "answer_plain": re.sub(r"<[^>]+>", "", item.answer),
            "answer_html": item.answer,
        }
        for item in FAQ_ITEMS
    ])
    return render_htmx_or_full(request, "components/faq.html", {
        "request": request,
        "faq_items": FAQ_ITEMS,
        "faq_items_json": faq_items_json,
        "owner_telegram_url": settings.owner_telegram_url,
        "owner_name": settings.owner_name,
        "active_tab": "faq",
    })


@router.get("/{path:path}", response_class=HTMLResponse)
async def not_found(request: Request, path: str):
    """Catch-all for undefined routes — returns 404 error page."""
    return render_htmx_or_full(
        request,
        "components/error.html",
        {"request": request, "error_type": "not_found", "active_tab": None},
        status_code=404
    )

